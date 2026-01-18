FRAME_W = 240
FRAME_H = 48

PT_X = 820
PT_Y = 305
PT_SPACING = 34

HP_BAR_HEIGHT = 8
MP_BAR_HEIGHT = 8
HP_BAR_X = 748
HP_BAR_Y = 396
HP_BAR_WIDTH = 192
MP_BAR_X = 748
MP_BAR_Y = 416
MP_BAR_WIDTH = 192

FONT0_FILENAME = "font3.png"
FONT0_WIDTH = 7
FONT0_HEIGHT = 13
FONT0_SCALE = 4
FONT0_SPACING = 28
FONT1_FILENAME = "font5.png"
FONT1_WIDTH = 7
FONT1_HEIGHT = 13
FONT1_SCALE = 3
FONT1_SPACING = 16
FONT2_FILENAME = "font4.png"
FONT2_WIDTH = 6
FONT2_HEIGHT = 13
FONT2_SCALE = 4
FONT2_SPACING = 21

COLOR_WHITE = (255, 255, 255)
COLOR_MAGENTA = (255, 0, 228)

FILENAME_HPFILL  = "hpfill.png"
FILENAME_MPFILL  = "mpfill.png"
FILENAME_CURSOR  = "cursor.png"
FILENAME_HPMP    = "hpmp.png"
FILENAME_LV      = "lv.png"
FILENAME_PBRED   = "pokeballred.png"
FILENAME_PBBLUE  = "pokeballblue.png"
FILENAME_MOVES   = "data/smt/smt_moves.json"
FILENAME_FRAME   = "battleframe.png"

SCALE_PRESSTURN = 2

PLAYER_BASE_X = -64
PLAYER_Y = 192
PLAYER_SPACING = 150

ENEMY_BASE_X = 300
ENEMY_Y = 0
ENEMY_SPACING = 152

PLAYER_OFFSET = 50

COORDS_BACKGROUND = (0, 0)
COORDS_FRAME= (0, 448)
COORDS_MENU_MAIN = [
    (65, 525), (316, 525), (536, 525), (765, 525),
    (65, 573), (316, 573), (536, 573), (765, 573)
]
COORDS_MENU_SKILLS = [
    (40, 475), 
    (40, 525), 
    (40, 575)
]

PT_STATE_TRANSPARENT = "transparent"
PT_STATE_SOLIDBLUE   = "solid_blue"
PT_STATE_SOLIDRED    = "solid_red"
PT_STATE_FLASHBLUE   = "flash_blue"
PT_STATE_FLASHRED    = "flash_red"
PT_DURATION_FLASH    = 10

AMP = 8
SPEED = 0.18
PHASE = 0.6

ENEMY_DRAW_ORDER = [1, 3, 0, 2]

PLAYER_Y_OFFSET = 64
NORMAL_Y_OFFSET = 16

HPMP_X = 672
HPMP_Y = 328

ACTIVE_POKEMON_NAME_X = 692
ACTIVE_POKEMON_NAME_Y_OFFSET = 14
LV_X = 877
LV_Y_OFFSET = 23
LV_TEXT_X = 902
LV_TEXT_Y_OFFSET = 14

X_MENU_MAIN = 40
Y_MENU_MAIN_0 = 470
Y_MENU_MAIN_1 = 517
Y_MENU_MAIN_2 = 565
MENU_MAIN_LINE_1 = "  Skills   Item    Guard   Talk"
MENU_MAIN_LINE_2 = "  Change   Escape  Pass    Info"

MENU_MODE_MAIN = "main"
MENU_MODE_SKILLS = "skills"
MENU_MODE_SUBMENU = "submenu"

SKILLS_X = 80
SKILLS_Y = 470
SKILLS_Y_INCR = 50

DUMMY_TEXTS = [
    "Skills submenu placeholder",
    "Item submenu placeholder",
    "Guard submenu placeholder",
    "Talk submenu placeholder",
    "Change submenu placeholder",
    "Escape submenu placeholder",
    "Pass submenu placeholder",
    "Info submenu placeholder"
]
DUMMY_MSG = "(Press X to return)"

FRESH_PRESS_TURNS = [2, 2, 2, 2]

PLAYER_DEX_NO = -1