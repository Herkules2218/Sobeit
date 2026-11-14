# Enable the bottom Friends/Admins/Logger/Settings HUD automatically at every launch.
# Use byte-level edits: this legacy source contains non-UTF-8 bytes, so decoding
# and re-encoding the entire file would risk corrupting existing strings.
from pathlib import Path

path = Path("_olympus/BlackLight/src/BlackLightCore.cpp")
if not path.is_file():
    raise SystemExit(f"Source not found: {path}")

data = path.read_bytes()
anchor = b"\tBlackLightFuncs->Menu.bRadioVolume = true;"
insertion = (
    b"\t// Restore the bottom HUD each time the game starts, after INI settings load.\r\n"
    b"\t// The user may still hide it manually during the current game session.\r\n"
    b"\tBlackLightFuncs->Menu.bImGuiHudMenu = true;\r\n"
)
if data.count(anchor) != 1:
    raise SystemExit(f"Expected one radio initialization anchor; got {data.count(anchor)}")
if data.count(b"\tBlackLightFuncs->Menu.bImGuiHudMenu = true;") != 0:
    raise SystemExit("Bottom HUD autostart already patched")
if data.count(b"void StartUpFuncs(void)") != 1:
    raise SystemExit("Unexpected initialization layout")

data = data.replace(anchor, insertion + anchor, 1)
path.write_bytes(data)
verified = path.read_bytes()
if verified.count(b"\tBlackLightFuncs->Menu.bImGuiHudMenu = true;") != 1:
    raise SystemExit("Bottom HUD initialization verification failed")
print("Olympus: bottom HUD is now enabled at every startup after INI load.")
