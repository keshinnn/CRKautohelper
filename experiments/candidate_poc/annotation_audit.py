"""Compare two data annotation passes; never runtime proof or train admission.

IoU .90 is a preregistered research agreement gate, not a guarantee that two
visual annotators are physically correct. Source/exhaustiveness review and
run/layout/dedup qualification remain separate requirements.
"""
import hashlib
import io
import math
from pathlib import Path
from PIL import Image


def box_iou(a, b):
    intersection = max(0, min(a[0]+a[2], b[0]+b[2])-max(a[0], b[0])) * max(0, min(a[1]+a[3], b[1]+b[3])-max(a[1], b[1]))
    return intersection / (a[2]*a[3] + b[2]*b[3] - intersection)


def audit_full_frame(source, first, second):
    result = dict(consistent=False, matchedBoxes=0, trainingAdmitted=False,
                  scope='annotation_agreement_only_not_physical_truth_or_action_authority',
                  requiredIoU=.90, errors=[])
    try:
        raw = Path(source['image']).read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        if any(p.get('imageSha256') != digest for p in [source, first, second]):
            raise ValueError('ANNOTATION_SOURCE_MISMATCH')
        with Image.open(io.BytesIO(raw)) as image:
            if image.format != 'PNG' or image.mode != 'RGB' or list(image.size) != source['sourceSize']:
                raise ValueError('ANNOTATION_GEOMETRY_MISMATCH')
            image.load()  # Header/hash agreement alone cannot prove decodable pixels.
            width, height = image.size
        if any(p.get('exhaustive') is not True for p in [first, second]):
            raise ValueError('EXHAUSTIVENESS_UNREVIEWED')
        reviewers = [p.get('reviewerId') for p in [first, second]]
        if any(not isinstance(x, str) or not x.strip() for x in reviewers) or reviewers[0] == reviewers[1]:
            raise ValueError('INDEPENDENT_REVIEW_MISSING')
        sets = [p.get('annotations') for p in [first, second]]
        for annotations in sets:
            if not isinstance(annotations, list):
                raise ValueError('ANNOTATIONS_MISSING')
            for annotation in annotations:
                box = annotation.get('box')
                if (annotation.get('className') not in ('map_node', 'entry_gate') or
                        annotation.get('visibility') not in ('complete', 'partial') or
                        not isinstance(box, list) or len(box) != 4 or
                        any(type(n) not in (int, float) or not math.isfinite(n) for n in box) or
                        min(box[:2]) < 0 or min(box[2:]) <= 0 or
                        box[0]+box[2] > width or box[1]+box[3] > height):
                    raise ValueError('ANNOTATION_BOX_INVALID')
        a, b = sets
        if len(a) != len(b):
            raise ValueError('ANNOTATION_COUNT_DISAGREEMENT')
        if not a and any(p.get('hardNegativeReviewed') is not True for p in [first, second]):
            raise ValueError('NEGATIVE_NOT_EXPLICITLY_REVIEWED')
        edges = []
        for x in a:
            choices = []
            for j, y in enumerate(b):
                if x['className'] != y['className'] or x['visibility'] != y['visibility']:
                    continue
                score = box_iou(x['box'], y['box'])
                if score >= .90:
                    choices.append((score, j))
            edges.append([j for _, j in sorted(choices, reverse=True)])
        matched = {}

        def augment(i, seen):
            for j in edges[i]:
                if j in seen:
                    continue
                seen.add(j)
                if j not in matched or augment(matched[j], seen):
                    matched[j] = i
                    return True
            return False

        for i in range(len(a)):
            augment(i, set())
        pairs = [dict(firstIndex=i, secondIndex=j, iou=box_iou(a[i]['box'], b[j]['box'])) for j, i in sorted(matched.items())]
        result.update(matchedBoxes=len(pairs), pairs=pairs,
                      minimumAgreementIoU=min((p['iou'] for p in pairs), default=None))
        if len(pairs) != len(a):
            raise ValueError('BOX_OR_VISIBILITY_DISAGREEMENT')
        result['consistent'] = True
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as error:
        result['errors'].append(str(error))
    return result
