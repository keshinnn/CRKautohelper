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

    def recover():
        repaired = recover_map_geometry(image, packet)
        if repaired is not packet.get('mapReview'):
            if 'v2OriginalMapReview' not in packet:
                packet['v2OriginalMapReview'] = packet.get('mapReview')
            packet['mapReview'] = repaired
        if timing is not None:
            timing.mark('sparse_geometry')
        aspect = recover_map_aspect(image, packet)
        if aspect is not packet.get('mapReview'):
            if 'v2OriginalMapReview' not in packet:
                packet['v2OriginalMapReview'] = packet.get('mapReview')
            packet['mapReview'] = aspect
        if timing is not None:
            timing.mark('aspect_geometry')

    if not coverage or not isinstance(prior, dict):
        if coverage and timing is not None:
            timing.mark('source_coverage')
        recover()
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

    import map_vision
    from fast_map_candidates import coverage_node_candidates
    packet['v2OriginalMapReview'] = copy.deepcopy(prior)
    with context.backend(coverage_node_candidates):
        # Same current raster; do not repeat OCR or borrow an earlier frame's map.
        expanded = map_vision.inspect_map(rgb, root / 'data/map', read_header=False)
        expanded['header'] = copy.deepcopy(prior.get('header'))
        packet['mapReview'] = expanded
        if timing is not None:
            timing.mark('source_coverage')
        recover()
    return packet
