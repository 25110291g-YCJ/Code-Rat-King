"""Quick smoke test: ensure key modules import cleanly (does not start the game loop).

Run this to catch ImportError / syntax errors in modules after refactors.
"""
MODULES = [
    'settings', 'resources', 'audio', 'utils',
    'cat', 'dog', 'house', 'trees', 'particles', 'items', 'background', 'hud', 'text_target'
]

errors = []
for m in MODULES:
    try:
        __import__(m)
        print('IMPORT_OK', m)
    except Exception as e:
        print('IMPORT_ERROR', m, e)
        errors.append((m, e))

if errors:
    raise SystemExit(f"Smoke imports failed for {len(errors)} module(s): {', '.join(e[0] for e in errors)}")
