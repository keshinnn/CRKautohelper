"""Separate same-frame M1 routing evidence from bounded candidate coverage.

Geometry, aspect estimation and independent proof checks remain unchanged.
The existing original-map field always holds the current source's M1 map.
"""
import copy
import hashlib
import re

from map_aspect import recover_map_aspect
from sparse_map_geometry import recover_map_geometry


def observe_geometry(image, packet, root, *, context, coverage=False, timing=None):
    if type(coverage) is not bool:
        raise ValueError('BOOLEAN_MAP_COVERAGE_REQUIRED')
    original = packet.pop('v2OriginalMapReview', None)
    if original is not None:
        packet['mapReview'] = original
    prior = packet.get('mapReview')

    def recover(target, *, baseline=None, record_timing=True):
        repaired = recover_map_geometry(image, target)
        if repaired is not target.get('mapReview'):
            if 'v2OriginalMapReview' not in target:
                target['v2OriginalMapReview'] = target.get('mapReview')
            target['mapReview'] = repaired
        if timing is not None and record_timing:
            timing.mark('sparse_geometry')
        before_aspect = target.get('mapReview')
        expected = baseline.get('aspectRectification') if baseline is not None else None
        source_working = copy.deepcopy(before_aspect) if baseline is not None and not expected else None
        aspect = recover_map_aspect(image, target)
        if baseline is not None:
            observed = aspect.get('aspectRectification') if isinstance(aspect, dict) else None
            geometry_keys = ('sourceSize', 'rectifiedInputSize', 'modelAnalysisSize',
                             'forwardMatrix', 'inverseMatrix', 'sourceCaptureFrameId',
                             'sourceImageSha256', 'pixelSha256')
            reason = None
            if not expected and observed:
                reason = 'coverage_cannot_introduce_unaccepted_rectification'
                accepted = source_working
            elif expected and (not observed or any(observed.get(k) != expected.get(k) for k in geometry_keys)):
                reason = 'coverage_geometry_differs_from_same_frame_m1'
                accepted = copy.deepcopy(baseline)
            if reason is not None:
                target['v2CoverageGeometryDecision'] = {
                    'reason': reason, 'baselineAspect': copy.deepcopy(expected),
                    'rejectedMapReview': copy.deepcopy(aspect), 'actionsExecuted': False,
                }
                aspect = accepted
        if aspect is not before_aspect:
            if 'v2OriginalMapReview' not in target:
                target['v2OriginalMapReview'] = before_aspect
            target['mapReview'] = aspect
        graph = target.get('mapReview')
        if coverage and record_timing and isinstance(graph, dict):
            # Re-measure against final source-space nodes; never copy a prior node ID.
            from map_current import inspect_current_node
            progress = prior.get('header') if isinstance(prior, dict) else None
            if not isinstance(progress, dict):
                progress = target.get('progress') or {}
            graph['currentPosition'] = inspect_current_node(
                image, target.get('evidence') or [], graph, root / 'data/map', progress)
        if timing is not None and record_timing:
            timing.mark('aspect_geometry')

    if not coverage or not isinstance(prior, dict):
        if coverage and timing is not None:
            timing.mark('source_coverage')
        recover(packet)
        return packet

    rgb = image.convert('RGB')
    digest = hashlib.sha256(rgb.tobytes()).hexdigest()
    binding = packet.get('binding', {})
    if (prior.get('frameId') != digest[:20]
            or binding.get('pixelSha256') != digest
            or [binding.get('width'), binding.get('height')] != list(rgb.size)
            or re.fullmatch(r'[a-f0-9]{64}', binding.get('imageSha256', '')) is None
            or context.source_id != binding.get('frameId')
            or context.source_sha256 != binding.get('imageSha256')
            or context.source_size != list(rgb.size)):
        raise ValueError('FRAME_MAP_PRIOR_SOURCE_MISMATCH')

    # Geometry acceptance is decided with the unchanged M1 backend on this frame.
    # Coverage may add candidates inside that route, never select another raster.
    from fast_map_candidates import node_candidates, coverage_node_candidates
    routing = copy.deepcopy(packet)
    with context.backend(node_candidates):
        recover(routing, record_timing=False)
    baseline = routing['mapReview']
    if timing is not None:
        timing.mark('baseline_geometry')

    import map_vision
    packet['v2OriginalMapReview'] = copy.deepcopy(prior)
    with context.backend(coverage_node_candidates):
        # Same current raster; do not repeat OCR or borrow an earlier frame's map.
        expanded = map_vision.inspect_map(rgb, root / 'data/map', read_header=False)
        expanded['header'] = copy.deepcopy(prior.get('header'))
        packet['mapReview'] = expanded
        if timing is not None:
            timing.mark('source_coverage')
        recover(packet, baseline=baseline)
    return packet
