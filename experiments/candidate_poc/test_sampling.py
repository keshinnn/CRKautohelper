import unittest
from sampling import choose_indices


class SourceTimelineSamplingTests(unittest.TestCase):
    def test_sampling_spans_whole_source_not_first_half(self):
        indices = choose_indices(10000, 80, [])
        self.assertLessEqual(min(indices), 999)
        self.assertGreaterEqual(max(indices), 9000)
        self.assertTrue(all(any(q * 2500 <= n < (q+1) * 2500 for n in indices) for q in range(4)))

    def test_existing_qa_frames_are_kept_without_duplicates(self):
        pins = [100, 200, 8000]
        result = choose_indices(10000, 80, pins)
        self.assertEqual(len(result), 80)
        self.assertEqual(len(set(result)), 80)
        self.assertTrue(set(pins) <= set(result))

    def test_invalid_index_or_insufficient_source_is_rejected(self):
        for n, quota, pins in [(4, 5, []), (10, 4, [-1]), (10, 4, [10]), (10, 4, [1.5])]:
            with self.subTest(n=n, quota=quota, pins=pins):
                with self.assertRaises(ValueError):
                    choose_indices(n, quota, pins)


if __name__ == '__main__':
    unittest.main()
