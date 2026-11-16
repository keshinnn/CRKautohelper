"""Unit checks for the runner's safety contracts (no OCR, no device)."""
import sys, unittest, time
from pathlib import Path
BOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(BOT))
from PIL import Image
import runner

STRAT = {'zones': [{'zone': 1, 'steps': [{'column': 2, 'type': 'battle', 'team': ['金桂']}, {'column': 2, 'type': 'random'}, {'column': None, 'type': 'boss', 'team': ['莫札']}]}]}

def R(state):
    r = object.__new__(runner.Runner); r.s = STRAT; r.dry = True; r.unknown_since = None
    r.d = type('D', (), {'size': (1440, 2560)})(); r.state = {'pending': None, **state}; r.last_img = None; return r

def ev(text, x=100, y=100, score=.99): return {'text': text, 'score': score, 'box': [[x, y], [x + 50, y], [x + 50, y + 30], [x, y + 30]]}

def map_packet(dx=0):
    nodes = [{'id': 'exit-0', 'type': 'exit', 'floor': None, 'column': None, 'box': [1248, 72, 197, 197]},
             {'id': 'visible-1-2', 'type': 'battle', 'floor': 1, 'column': 2, 'visibleRow': 1, 'box': [1101 + dx, 368, 197, 197], 'completed': False}]
    return {'flow': {'state': 'MAP', 'targets': []}, 'evidence': [ev('冥界試煉'), ev('區域1進行中')], 'progress': {'displayedZone': 1},
            'mapReview': {'nodes': nodes, 'currentPosition': {'verified': False}}}

def preview_packet(state='NODE_BATTLE', floor=1):
    return {'flow': {'state': state, 'targets': [{'target': 'enter', 'box': [2000, 1250, 320, 90]}]}, 'evidence': [ev(f'第{floor}層戰鬥')],
            'nodeHeader': {'verified': True, 'floor': floor}, 'progress': {}}

class Contracts(unittest.TestCase):
    def test_map_needs_two_consistent_observations(self):
        r = R({'zone': 1, 'step': 0})
        self.assertEqual(r.decide(map_packet())[0], 'wait')
        self.assertEqual(r.decide(map_packet())[0], 'tap')

    def test_map_moving_target_resets(self):
        r = R({'zone': 1, 'step': 0})
        r.decide(map_packet()); self.assertEqual(r.decide(map_packet(dx=40))[0], 'wait')

    def test_no_blind_map_retaps(self):
        r = R({'zone': 1, 'step': 0}); kinds = []
        for _ in range(8): kinds.append(r.decide(map_packet())[0])
        self.assertEqual(kinds.count('tap'), 2); self.assertEqual(kinds[-1], 'pause')

    def test_preview_wrong_type_pauses(self):
        r = R({'zone': 1, 'step': 0}); self.assertEqual(r.decide(preview_packet('NODE_BOSS'))[0], 'pause')

    def test_preview_wrong_floor_pauses(self):
        r = R({'zone': 1, 'step': 0}); self.assertEqual(r.decide(preview_packet(floor=2))[0], 'pause')

    def test_preview_needs_two_observations_before_enter(self):
        r = R({'zone': 1, 'step': 0})
        self.assertEqual(r.decide(preview_packet())[0], 'wait'); self.assertEqual(r.decide(preview_packet())[0], 'tap')

    def test_halt_blocks_preview_enter(self):
        r = R({'zone': 1, 'step': 0, 'halt': 'x'}); self.assertEqual(r.decide(preview_packet())[0], 'pause')

    def test_preview_panel_over_map_is_not_a_map(self):
        # held-out S4 video: V1 said MAP while the preview panel was open and the floor title was unreadable
        pk = map_packet(); pk['evidence'] += [ev('激门'), ev('危险度'), ev('01:30'), ev('套用效果'), ev('可獲得'), ev('進入', 2100, 1290)]
        r = R({'zone': 1, 'step': 0}); kinds = [r.decide(pk)[0] for _ in range(3)]
        self.assertNotIn('tap', kinds); self.assertIn('pause', kinds)

    def test_entry_confirm_dialog_over_panel_keeps_dialog_state(self):
        pk = {'flow': {'state': 'NODE_ENTRY_CONFIRM', 'targets': []}, 'progress': {},
              'evidence': [ev('第1層戰鬥'), ev('危险度'), ev('套用效果'), ev('可獲得'), ev('進入', 2100, 1290), ev('續', 1260, 990)]}
        a = R({'zone': 1, 'step': 0}).decide(pk); self.assertEqual(a[0], 'tap'); self.assertLess(abs(a[1][0] - 1285), 60)

    def test_rift_panel_without_floor_pauses_not_map(self):
        pk = map_packet(); pk['evidence'] += [ev('冥界裂縫'), ev('危险度'), ev('可能發生的事件'), ev('確', 2100, 1290)]
        kinds = [R({'zone': 1, 'step': 0}).decide(pk)[0] for _ in range(2)]; self.assertEqual(kinds, ['pause', 'pause'])

    def test_heal_panel_off_strategy_closes_then_pauses(self):
        # a heal preview we did not open for this step: closing a preview is reversible, but only twice; never 恢復
        pk = map_packet(); pk['evidence'] += [ev('恢復'), ev('危险度'), ev('選擇恢復方式'), ev('恢復所有餅乾')]
        r = R({'zone': 1, 'step': 0}); acts = [r.decide(pk) for _ in range(3)]
        self.assertEqual([a[0] for a in acts], ['tap', 'tap', 'pause'])
        self.assertEqual(acts[0][1], (2490, 290))

    def test_heal_panel_on_strategy_taps_recover_after_two_observations(self):
        strat = {'zones': [{'zone': 1, 'steps': [{'column': 2, 'type': 'battle'}, {'column': 3, 'type': 'heal'}]}]}
        pk = map_packet(); pk['evidence'] += [ev('恢復', 2600, 100), ev('危险度'), ev('選擇恢復方式'), ev('恢復所有餅乾'), ev('15/15恢復', 2200, 1290)]
        r = R({'zone': 1, 'step': 1, 'pending': {'type': 'heal', 'floor': 2}}); r.s = strat
        self.assertEqual(r.decide(pk)[0], 'wait'); a = r.decide(pk)
        self.assertEqual(a[0], 'tap'); self.assertGreater(a[1][1], 1200); self.assertEqual(r.state['step'], 2)

    def test_heal_slot_on_battle_step_heals_and_waits_for_result(self):
        # route digits are fixed map slots; another player's map may hold a heal where the author fought
        strat = {'zones': [{'zone': 1, 'steps': [{'column': 2, 'type': 'battle', 'team': ['金桂']}, {'column': 2, 'type': 'battle', 'team': ['莫札']}]}]}
        pk = map_packet(); pk['evidence'] += [ev('第1層恢復', 2600, 100), ev('危险度'), ev('選擇恢復方式'), ev('恢復所有餅乾'), ev('15/15恢復', 2200, 1290)]
        r = R({'zone': 1, 'step': 0, 'pending': {'type': 'battle', 'floor': 1}}); r.s = strat
        self.assertEqual(r.decide(pk)[0], 'wait'); a = r.decide(pk); self.assertEqual(a[0], 'tap'); self.assertEqual(r.state['step'], 1)
        self.assertEqual(r.decide(pk)[0], 'wait')                     # panel still open right after 恢復: wait, never pause
        r.state['healed']['at'] -= 30; self.assertEqual(r.decide(pk)[0], 'pause')   # 20 s and still no 已恢復: ask
        pk2 = map_packet(); pk2['evidence'] += [ev('第1層恢復', 2600, 100), ev('危险度'), ev('選擇恢復方式'), ev('已恢復')]
        self.assertEqual(r.decide(pk2), ('tap', (2490, 290), 'heal done (已恢復) -> close panel'))

    def test_reward_box_notice_confirms(self):
        pk = map_packet(); pk['evidence'] += [ev('所獲得的自寶箱'), ev('已移動至庫，'), ev('確', 1280, 1010)]
        a = R({'zone': 1, 'step': 0}).decide(pk); self.assertEqual(a[0], 'tap'); self.assertLess(abs(a[1][1] - 1025), 40)

    def test_recruit_popup_joins(self):
        pk = map_packet(); pk['evidence'] += [ev('發現新夥伴！'), ev('加入', 1280, 1200)]
        a = R({'zone': 1, 'step': 0}).decide(pk); self.assertEqual(a[0], 'tap'); self.assertLess(abs(a[1][1] - 1215), 40)

    def test_expedition_menu_over_map_pauses(self):
        pk = map_packet(); pk['evidence'] += [ev('繼續'), ev('儲存並前往大廳'), ev('結束探險')]
        self.assertEqual(R({'zone': 1, 'step': 0}).decide(pk)[0], 'pause')

    def test_loading_waits(self):
        pk = {'flow': {'state': 'UNKNOWN', 'targets': []}, 'evidence': [ev('讀取中...')], 'progress': {}}
        self.assertEqual(R({'zone': 1, 'step': 0}).decide(pk)[0], 'wait')

    def test_freshness_guard(self):
        a = Image.open(BOT / 'runs/20261116-021024/0002-full.png'); b = Image.open(BOT / 'runs/20261116-021024/0005-full.png')
        self.assertFalse(runner.patch_changed(a, b, (1533, 1014)))
        self.assertTrue(runner.patch_changed(Image.open(BOT / 'shots/031525.png'), Image.open(BOT / 'shots/031637.png'), (1200, 762)))

if __name__ == '__main__': unittest.main(verbosity=2)
