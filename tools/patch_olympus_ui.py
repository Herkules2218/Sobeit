# Olympus Royal UI hotfix: no startup music, unified submenu theme, and object labels.
from pathlib import Path

root = Path('_olympus/BlackLight/src')
if not root.is_dir():
    raise SystemExit(f'Expected source directory missing: {root}')

menu = root / 'BlackLightMenu.cpp'
chat = root / 'cheat_samp.cpp'

m = menu.read_text(encoding='utf-8-sig')
old = '''\tImGui::PushID(menuid);
\tif (ImGui::Button(pSampMulti->SetText("##%s",szMenuName), this->MenuItemMatchMenuWidth()))
\t{
\t\tif (menus != menuid)
\t\t\tthis->SetMenu(menuid, false);
\t}
\tImGui::PopID();'''
new = '''\tImGui::PushID(menuid);
\t// Olympus Royal: consistent transparent rows, purple hover, gold active.
\tImGui::PushStyleColor(ImGuiCol_Button, ImVec4(0.0f, 0.0f, 0.0f, 0.0f));
\tImGui::PushStyleColor(ImGuiCol_ButtonHovered, ImVec4(0.43f, 0.20f, 0.75f, 0.72f));
\tImGui::PushStyleColor(ImGuiCol_ButtonActive, ImVec4(0.75f, 0.54f, 0.17f, 0.65f));
\tif (ImGui::Button(pSampMulti->SetText("##%s",szMenuName), this->MenuItemMatchMenuWidth()))
\t{
\t\tif (menus != menuid)
\t\t\tthis->SetMenu(menuid, false);
\t}
\tImGui::PopStyleColor(3);
\tImGui::PopID();'''
if m.count(old) != 1:
    raise SystemExit(f'Menu target count {m.count(old)} (expected 1)')
m = m.replace(old, new, 1)
count = m.count('Об’єкт') + m.count('об’єкт')
if count < 3:
    raise SystemExit('Object labels not found; unexpected source')
m = m.replace('Об’єкт', 'Обєкт').replace('об’єкт', 'обєкт')
assert 'Об’єкт' not in m and 'об’єкт' not in m
# Critical: original BlackLightMenu.cpp has a UTF-8 BOM. MSVC can misread
# Ukrainian menu literals as the active Windows code page if BOM is lost.
# utf-8-sig restores the marker and keeps all Ukrainian strings readable.
menu.write_text(m, encoding='utf-8-sig')
if not menu.read_bytes().startswith(b'\xef\xbb\xbf'):
    raise SystemExit('Menu UTF-8 BOM was not preserved')
if 'Гравець'.encode('utf-8') not in menu.read_bytes():
    raise SystemExit('Ukrainian menu text was corrupted')

c = chat.read_text(encoding='utf-8-sig')
autoplay = '\tpSampMulti->PlaySongOnLoading(pSampMulti->SetText("%sSongOnStart.txt",M0D_FOLDER));'
if c.count(autoplay) != 1:
    raise SystemExit(f'Autoplay target count {c.count(autoplay)} (expected 1)')
c = c.replace(autoplay, '\t// Olympus: do not start any song automatically; manual music playback is retained.', 1)
chat.write_text(c, encoding='utf-8')
print(f'Olympus hotfix applied: {count} object labels, unified submenus, startup song disabled.')
