# Olympus vehicle speed modes, based on user-supplied speed.lua.
# Applies to the original source extracted by GitHub Actions, after the UI/player/HUD patches.
from pathlib import Path

root = Path("_olympus/BlackLight/src")
vehicle = root / "cheat_vehicle.cpp"
ini = root / "ini.cpp"
menu = root / "BlackLightMenu.cpp"

def replace_one(path, old, new):
    data = path.read_bytes()
    a = old.encode("utf-8") if isinstance(old, str) else old
    b = new.encode("utf-8") if isinstance(new, str) else new
    if data.count(a) != 1:
        raise SystemExit(f"Unexpected {path.name} anchor count: {data.count(a)}")
    path.write_bytes(data.replace(a, b, 1))

globals_ = """
// Olympus vehicle speed modes. 0 = old fast nitro, 1 = gradual speed.lua mode.
int g_olympusVehicleBoostMode = 0;
float g_olympusSmoothBoostMultiplier = 1.02f;
float g_olympusSmoothBoostSpeedLimit = 120.25f;
int g_olympusSmoothBoostStepMs = 30;
"""
replace_one(vehicle, '#include "main.h"\n', '#include "main.h"\n' + globals_)

state = ("\tstatic uint32_t\t\ttimer;\n"
         "\tstatic int\t\t\tdecelerating;\n"
         "\tstatic float\t\tspeed_off;\n"
         "\tfloat\t\t\t\tpre_speed[3];\n"
         "\tstruct vehicle_info *temp;\n")
smooth = """
    static uint32_t smoothLastTick = 0;
    if (g_olympusVehicleBoostMode == 1)
    {
        decelerating = 0;
        if (!KEYCOMBO_DOWN(set.key_nitro_mod))
        {
            smoothLastTick = 0;
            return;
        }
        const uint32_t now = time_get();
        const int stepMs = (g_olympusSmoothBoostStepMs < 15) ? 15 :
            (g_olympusSmoothBoostStepMs > 150 ? 150 : g_olympusSmoothBoostStepMs);
        if (smoothLastTick != 0 && (uint32_t)(now - smoothLastTick) < (uint32_t)stepMs)
            return;
        smoothLastTick = now;
        const float mult = (g_olympusSmoothBoostMultiplier < 1.001f) ? 1.001f :
            (g_olympusSmoothBoostMultiplier > 1.12f ? 1.12f : g_olympusSmoothBoostMultiplier);
        const float cap = (g_olympusSmoothBoostSpeedLimit < 0.1f) ? 0.1f :
            (g_olympusSmoothBoostSpeedLimit > 120.25f ? 120.25f : g_olympusSmoothBoostSpeedLimit);
        if (info->vehicle_type == VEHICLE_TYPE_TRAIN)
        {
            for (temp = info; temp != NULL; temp = temp->m_train_next_carriage)
            {
                const float accelerated = temp->m_fTrainSpeed * mult;
                float capped = accelerated;
                // Preserve the safe-train-speed behavior of speed.lua.
                if (capped >= 0.99f) capped = 0.9f;
                if (capped <= -0.99f) capped = -0.9f;
                if (capped <= cap && capped >= -cap)
                    temp->m_fTrainSpeed = capped;
            }
        }
        else
        {
            for (temp = info; temp != NULL; temp = temp->trailer)
            {
                const float current = vect3_length(temp->speed);
                if (current > 0.0001f && current * mult <= cap)
                    vect3_mult(temp->speed, mult, temp->speed);
                if (!BlackLightFuncs->bVehicleTrailerSupport)
                    break;
            }
        }
        return;
    }
    // Leave the old classic nitro branch below unchanged.
    smoothLastTick = 0;
"""
replace_one(vehicle, state, state + smooth)

externs = """
extern int g_olympusVehicleBoostMode;
extern float g_olympusSmoothBoostMultiplier;
extern float g_olympusSmoothBoostSpeedLimit;
extern int g_olympusSmoothBoostStepMs;
"""
replace_one(ini, '#include "main.h"\n', '#include "main.h"\n' + externs)
ini_base = '\tBlackLightSetSetting("VehicleBoost", TYPE_BOOL, &BlackLightFuncs->bVehicleBoost, "true");\n'
ini_extra = (
'\tif ( (ent = ini_register_entry("OlympusVehicleBoostMode", TYPE_INT)) != NULL )\n'
'\t\tini_register_data( ent, &g_olympusVehicleBoostMode, "0" );\n'
'\tif ( (ent = ini_register_entry("OlympusSmoothBoostMultiplier", TYPE_FLOAT)) != NULL )\n'
'\t\tini_register_data( ent, &g_olympusSmoothBoostMultiplier, "1.02" );\n'
'\tif ( (ent = ini_register_entry("OlympusSmoothBoostSpeedLimit", TYPE_FLOAT)) != NULL )\n'
'\t\tini_register_data( ent, &g_olympusSmoothBoostSpeedLimit, "120.25" );\n'
'\tif ( (ent = ini_register_entry("OlympusSmoothBoostStepMs", TYPE_INT)) != NULL )\n'
'\t\tini_register_data( ent, &g_olympusSmoothBoostStepMs, "30" );\n')
replace_one(ini, ini_base, ini_base + ini_extra)
replace_one(menu, '#pragma execution_character_set("utf-8")\n',
            '#pragma execution_character_set("utf-8")\n' + externs)

old_btn = ('\t\t\t\tpMenu->AddButton(&BlackLightFuncs->bVehicleBoost, "Прискорення авто##VehicleFunc13");\n'
           '\t\t\t\tpMenu->AddItemDescription("Press LALT to boost your vehicle");\n')
new_btn = ('\t\t\t\tpMenu->AddButton(&BlackLightFuncs->bVehicleBoost, "Прискорення авто##VehicleFunc13");\n'
           '\t\t\t\tpMenu->AddItemDescription("Затисніть лівий Alt для прискорення");\n'
           '\t\t\t\tpMenu->AddMenuText("Режим прискорення");\n'
           '\t\t\t\tImGui::Combo("##OlyVehicleBoostMode", &g_olympusVehicleBoostMode, "Швидкий\\0Плавний\\0");\n'
           '\t\t\t\tif (g_olympusVehicleBoostMode == 1)\n'
           '\t\t\t\t{\n'
           '\t\t\t\t\tpMenu->AddMenuText("Параметри плавного режиму");\n'
           '\t\t\t\t\tImGui::Text("Множник швидкості");\n'
           '\t\t\t\t\tpMenu->AddSlider("##OlySmoothMult", g_olympusSmoothBoostMultiplier, 1.001f, 1.12f, "%.3f");\n'
           '\t\t\t\t\tImGui::Text("Ліміт швидкості");\n'
           '\t\t\t\t\tpMenu->AddSlider("##OlySmoothCap", g_olympusSmoothBoostSpeedLimit, 0.1f, 120.25f, "%.2f");\n'
           '\t\t\t\t\tImGui::Text("Крок прискорення (мс)");\n'
           '\t\t\t\t\tpMenu->AddSlider("##OlySmoothStep", g_olympusSmoothBoostStepMs, 15, 150);\n'
           '\t\t\t\t}\n')
replace_one(menu, old_btn, new_btn)
assert menu.read_bytes().startswith(b"\xef\xbb\xbf"), "Menu source lost UTF-8 BOM"
assert b"g_olympusVehicleBoostMode" in menu.read_bytes()
print("Vehicle boost mode patch applied: Fast preserved, Smooth added and persisted.")
