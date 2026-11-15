"""Dataset admission tests; synthetic metadata is never training data."""
import copy
import unittest
from freeze_inputs import validate_groups, readiness


def record(key, split):
    return dict(id=key, split=split, sourceSha256=key * 64,
                runGroup='run-' + key, layoutGroup='map-' + key,
                imageSha256=key * 64, reviewed=True,
                boundaryPolicy='visible_outer_solid_extent_v2',
                independentReviews=2, annotationDisagreement=False,
                provenanceVerified=True, protected=False,
                boxes=[dict(className='map_node', box=[1, 2, 20, 20],
                            visibility='complete')])


class DataAdmissionTests(unittest.TestCase):
    def test_unclear_old_boundary_policy_is_not_admitted(self):
        a = record('a', 'train'); a['boundaryPolicy'] = 'visible_outer_solid_edge_v1'
        self.assertIn('BOUNDARY_UNRESOLVED', validate_groups(dict(records=[a])))

    def test_valid_independent_metadata_is_accepted_but_not_count_ready(self):
        data = dict(records=[record('a', 'train'), record('b', 'val'), record('c', 'test')])
        self.assertEqual(validate_groups(data), [])
        self.assertFalse(readiness(data)['ready'])

    def test_source_leak_is_rejected(self):
        a, b = record('a', 'train'), record('b', 'test')
        b['sourceSha256'] = a['sourceSha256']
        self.assertIn('SOURCE_CROSS_SPLIT', validate_groups(dict(records=[a, b])))

    def test_reappearing_map_and_run_are_rejected(self):
        for field, reason in [('layoutGroup', 'LAYOUT_CROSS_SPLIT'), ('runGroup', 'RUN_CROSS_SPLIT')]:
            with self.subTest(field=field):
                a, b = record('a', 'train'), record('b', 'val')
                b[field] = a[field]
                self.assertIn(reason, validate_groups(dict(records=[a, b])))

    def test_exact_duplicate_is_rejected_even_with_different_ids(self):
        a, b = record('a', 'train'), record('b', 'test')
        b['imageSha256'] = a['imageSha256']
        self.assertIn('DUPLICATE_IMAGE', validate_groups(dict(records=[a, b])))

    def test_protected_source_list_cannot_be_overridden_by_record(self):
        a = record('a', 'train')
        self.assertIn('PROTECTED_SOURCE', validate_groups(dict(records=[a], excludedSourceHashes=[a['sourceSha256']])))

    def test_protected_frozen_interaction_is_rejected(self):
        a = record('a', 'train'); a['protected'] = True
        self.assertIn('PROTECTED_RECORD', validate_groups(dict(records=[a])))

    def test_unknown_lineage_is_not_certified_data(self):
        a = record('a', 'train'); a.pop('layoutGroup')
        self.assertIn('MISSING_LINEAGE', validate_groups(dict(records=[a])))

    def test_unresolved_outer_boundary_disagreement_blocks_training(self):
        a = record('a', 'train'); a['annotationDisagreement'] = True
        self.assertIn('BOUNDARY_UNRESOLVED', validate_groups(dict(records=[a])))

    def test_unreviewed_and_single_review_annotations_are_rejected(self):
        for field, value in [('reviewed', False), ('independentReviews', 1), ('provenanceVerified', False)]:
            with self.subTest(field=field):
                a = record('a', 'train'); a[field] = value
                self.assertTrue(validate_groups(dict(records=[a])))

    def test_partial_visibility_is_not_silently_complete(self):
        a = record('a', 'train'); a['boxes'][0]['visibility'] = 'invented_amodal'
        self.assertIn('INVALID_BOX_LABEL', validate_groups(dict(records=[a])))

    def test_zero_data_reports_exact_shortfall(self):
        result = readiness(dict(records=[]))
        self.assertEqual(result['missing'], dict(train=240, val=80, test=80))
        self.assertFalse(result['ready'])

    def test_counts_cannot_override_failed_lineage_gate(self):
        data = dict(records=[record('a', 'train')] * 400)
        self.assertFalse(readiness(data)['ready'])


if __name__ == '__main__':
    unittest.main()
