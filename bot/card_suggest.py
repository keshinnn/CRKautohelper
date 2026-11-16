"""Suggest identities for unknown team-select cards in bot/cards/inbox/ with the MuMu card recogniser (card_model2).
Suggestions are shown to the user; a card enters the confirmed bank only when the user confirms it."""
import json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import cv2

def main():
    inbox = HERE / 'cards' / 'inbox'; todo = [p for p in sorted(inbox.glob('*.png')) if not p.with_suffix('.json').exists()]
    if not todo: print(json.dumps({'done': 0})); return
    from card_model2 import CardRecognizer
    rec = CardRecognizer()
    for p in todo:
        o = rec.identify(cv2.imread(str(p)))
        p.with_suffix('.json').write_text(json.dumps({'suggestions': [{'id': t['id'], 'name': t['name'], 'similarity': t['score']} for t in o.get('top', [])],
            'modelStatus': o['status'], 'modelId': o.get('id') if o['status'] == 'ok' else None, 'reason': o.get('reason', '')}, ensure_ascii=False, indent=1), encoding='utf-8')
    print(json.dumps({'done': len(todo)}))

if __name__ == '__main__': main()
