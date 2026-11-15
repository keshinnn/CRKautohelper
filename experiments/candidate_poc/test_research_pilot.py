"""Small research metrics/split safety; no actual training in tests."""
import unittest
try:
 import research_pilot as p
except ImportError: p=None

def obj(box, visibility='complete', cls='map_node'):
 return dict(box=box,visibility=visibility,className=cls)

class PilotTests(unittest.TestCase):
 def setUp(self): self.assertIsNotNone(p,'small research runner missing')
 def test_same_video_cannot_be_split_for_validation(self):
  with self.assertRaisesRegex(ValueError,'SOURCE_OVERLAP'):
   p.check_split([dict(sourceId='new',imageSha256='a',pixelSha256='p')],[dict(sourceId='new',imageSha256='b',pixelSha256='q')])
 def test_old_protected_sources_never_enter_training(self):
  with self.assertRaisesRegex(ValueError,'PROTECTED_TRAINING_SOURCE'):
   p.check_split([dict(sourceId='LX46_2XTfJg',imageSha256='a',pixelSha256='p')],[dict(sourceId='new',imageSha256='b',pixelSha256='q')])
 def test_same_pixels_across_sources_are_not_independent(self):
  with self.assertRaisesRegex(ValueError,'PIXEL_OVERLAP'):
   p.check_split([dict(sourceId='a',imageSha256='a',pixelSha256='same')],[dict(sourceId='b',imageSha256='b',pixelSha256='same')])
 def test_duplicate_predictions_are_false_positives(self):
  r=p.score([obj([0,0,10,10]),obj([0,0,10,10])],[obj([0,0,10,10])],.5)
  self.assertEqual((r['tp'],r['fp'],r['fn']),(1,1,0))
 def test_one_prediction_cannot_recall_two_truth_objects(self):
  r=p.score([obj([0,0,10,10])],[obj([0,0,10,10]),obj([0,0,10,10])],.5)
  self.assertEqual((r['tp'],r['fp'],r['fn']),(1,0,1))
 def test_partial_is_reported_separately(self):
  r=p.score([obj([0,0,10,10])],[obj([0,0,10,10],'partial')],.5)
  self.assertEqual(r['partial']['tp'],1); self.assertEqual(r['complete']['tp'],0)
 def test_wrong_class_and_empty_negative_are_scored(self):
  r=p.score([obj([0,0,10,10],cls='entry_gate')],[obj([0,0,10,10])],.5)
  self.assertEqual((r['tp'],r['fp'],r['fn']),(0,1,1))
  self.assertEqual(p.score([obj([0,0,10,10])],[],.5)['fp'],1)
 def test_half_overlap_does_not_masquerade_as_formal_box_pass(self):
  a=[obj([0,0,10,10])]; b=[obj([2,0,10,10])]
  self.assertEqual(p.score(a,b,.5)['tp'],1); self.assertEqual(p.score(a,b,.9)['tp'],0)

class PilotDeadlineTests(unittest.TestCase):
 def test_direct_fit_cannot_bypass_supervisor_wall_limit(self):
  with self.assertRaisesRegex(ValueError,'SUPERVISED_RESEARCH_LAUNCH_REQUIRED'):
   p.require_supervisor()

if __name__=='__main__':unittest.main()
