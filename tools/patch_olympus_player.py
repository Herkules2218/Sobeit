# Patch Olympus player menu without touching gameplay implementations.
from pathlib import Path

path = Path('_olympus/BlackLight/src/BlackLightMenu.cpp')
if not path.is_file():
    raise SystemExit(f'Missing menu source: {path}')
text = path.read_text(encoding='utf-8-sig')

# The old 'Бій та зброя' page is a duplicate. The same No Spread toggle
# is already present under 'Бойові режими'.
entry = 'pMenu->AddMenu("Бій та зброя", MENU_OLYMPUS_PLAYER_COMBAT);'
if text.count(entry) != 1:
    raise SystemExit('Unexpected player combat menu entry count')
text = text.replace(entry + '\n', '', 1)

start = '\t\t\tcase MENU_OLYMPUS_PLAYER_COMBAT:\n'
end = '\t\t\tcase MENU_OLYMPUS_PLAYER_EFFECTS:\n'
if text.count(start) != 1 or text.count(end) != 1:
    raise SystemExit('Unexpected combat/effects page anchors')
a, tail = text.split(start, 1)
old_case, b = tail.split(end, 1)
if old_case.count('bNoSpread') != 1:
    raise SystemExit('Combat duplicate did not contain exactly one No Spread')
text = a + end + b

# Hide Fake Jetpack and its tooltip, preserving the real Give Jetpack button.
lines = text.splitlines(keepends=True)
indices = [i for i, line in enumerate(lines) if 'pMenu->AddButton(&BlackLightFuncs->bFakeJetpack, "Імітація джетпака##PlayerFunc6b");' in line]
if len(indices) != 1 or indices[0] + 1 >= len(lines) or 'pMenu->AddItemDescription("Others see you having jetpack' not in lines[indices[0] + 1]:
    raise SystemExit('Fake Jetpack toggle and tooltip not found together')
i = indices[0]
del lines[i:i + 2]
text = ''.join(lines)

# No Stun V1 used DMFunc4 already; give No Spread a unique ImGui ID.
old = '"Без розкиду##DMFunc4"'
if text.count(old) != 1:
    raise SystemExit('Expected one No Spread button in Deathmatch menu')
text = text.replace(old, '"Без розкиду##DMNoSpread"', 1)

# Normalize typographic U+2019 to plain ASCII apostrophes for the menu font.
text = text.replace('’', "'")
if '’' in text or text.count('"Без розкиду##DMNoSpread"') != 1 or '"Імітація джетпака##PlayerFunc6b"' in text or entry in text:
    raise SystemExit('Player menu post-check failed')
if '"Бойові режими", MENU_PLAYER_DEATHMATCH' not in text:
    raise SystemExit('Deathmatch page was accidentally lost')
path.write_text(text, encoding='utf-8-sig')
if not path.read_bytes().startswith(b'\xef\xbb\xbf'):
    raise SystemExit('MSVC UTF-8 BOM missing')
print('Olympus player menu fixes applied: Fake Jetpack hidden, No Spread deduplicated, combat menu consolidated, apostrophes normalized.')
