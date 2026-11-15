"""Isolated PoC data admission; no formal observer or training imports."""
import math
import re
from collections import Counter

TARGETS = {'train': 240, 'val': 80, 'test': 80}
POLICY = 'visible_outer_solid_extent_v2'


def _sha(value):
    return isinstance(value, str) and bool(re.fullmatch(r'[0-9a-f]{64}', value))


def validate_groups(manifest):
    errors = set()
    groups = {key: {} for key in ('sourceSha256', 'runGroup', 'layoutGroup')}
    seen_images = set()
    records = manifest.get('records', [])
    if not isinstance(records, list):
        return ['INVALID_RECORDS']
    protected = set(manifest.get('excludedSourceHashes', []))
    reasons = {'sourceSha256': 'SOURCE_CROSS_SPLIT',
               'runGroup': 'RUN_CROSS_SPLIT', 'layoutGroup': 'LAYOUT_CROSS_SPLIT'}
    for record in records:
        if not isinstance(record, dict):
            errors.add('INVALID_RECORD'); continue
        split = record.get('split')
        if split not in TARGETS:
            errors.add('INVALID_SPLIT')
        for key in groups:
            value = record.get(key)
            if not isinstance(value, str) or not value.strip():
                errors.add('MISSING_LINEAGE'); continue
            if key == 'sourceSha256' and not _sha(value):
                errors.add('INVALID_SOURCE_HASH')
            prior = groups[key].setdefault(value, split)
            if prior != split:
                errors.add(reasons[key])
        image_hash = record.get('imageSha256')
        if not _sha(image_hash):
            errors.add('INVALID_IMAGE_HASH')
        if image_hash in seen_images:
            errors.add('DUPLICATE_IMAGE')
        seen_images.add(image_hash)
        if record.get('sourceSha256') in protected:
            errors.add('PROTECTED_SOURCE')
        if record.get('protected') is not False:
            errors.add('PROTECTED_RECORD')
        if record.get('provenanceVerified') is not True:
            errors.add('UNVERIFIED_PROVENANCE')
        if (record.get('boundaryPolicy') != POLICY or
                record.get('annotationDisagreement') is not False):
            errors.add('BOUNDARY_UNRESOLVED')
        if (record.get('reviewed') is not True or
                type(record.get('independentReviews')) is not int or
                record['independentReviews'] < 2):
            errors.add('ANNOTATION_NOT_REVIEWED')
        boxes = record.get('boxes')
        if not isinstance(boxes, list):
            errors.add('INVALID_BOX_LABEL'); continue
        # Empty labels are valid only for explicitly reviewed hard negatives.
        if not boxes and record.get('hardNegativeReviewed') is not True:
            errors.add('EMPTY_UNREVIEWED_LABELS')
        for item in boxes:
            if not isinstance(item, dict):
                errors.add('INVALID_BOX_LABEL'); continue
            box = item.get('box')
            if (item.get('className') not in ('map_node', 'entry_gate') or
                    item.get('visibility') not in ('complete', 'partial') or
                    not isinstance(box, list) or len(box) != 4 or
                    any(type(n) not in (int, float) or not math.isfinite(n) for n in box) or
                    (isinstance(box, list) and len(box) == 4 and
                     all(type(n) in (int, float) for n in box) and
                     (box[0] < 0 or box[1] < 0 or box[2] <= 0 or box[3] <= 0))):
                errors.add('INVALID_BOX_LABEL')
    if len(records) > sum(TARGETS.values()):
        errors.add('DATA_CAP_EXCEEDED')
    return sorted(errors)


def readiness(manifest):
    errors = validate_groups(manifest)
    records = manifest.get('records', [])
    counts = Counter(r.get('split') for r in records if isinstance(r, dict)) if not errors else Counter()
    missing = {s: max(0, target - counts[s]) for s, target in TARGETS.items()}
    return {'ready': not errors and not any(missing.values()),
            'certifiedCounts': {s: counts[s] for s in TARGETS},
            'missing': missing, 'errors': errors,
            'scope': 'metadata_admission_only; image and independent-review attestations require audit'}
