import os

BOT_TOKEN = os.environ.get("BOT_TOKEN", "").strip()
CONTEST_API_KEY = os.environ.get("CONTEST_API_KEY", "").strip()
ADMIN_ID = 7123672535
PACK_NAME = None  # будет установлено динамически

# ========== КОЛИЧЕСТВО И БАТЧИ ==========
TOTAL_STICKERS = 120

# ========== НОВЫЕ ПОДАРКИ (115-120) ==========
# ID подарков с особым оверлеем
NEW_GIFT_IDS = set(range(115, 121))

STICKER_PAUSE = 0.1            # секунд между стикерами (атомарный режим: ~3 мин)
UPDATE_INTERVAL_MINUTES = 10   # обновление строго по круглым 10-минуткам

# Часовой пояс UTC+3 (Москва)
TIMEZONE_OFFSET = 3

# ========== ПУТИ К ФАЙЛАМ ==========
BASE_TEMPLATE_PATH = "base.png"
EXTRA_IMAGE_PATH = "extra.png"
TON_ICON_PATH = "ton_icon.png"
STARS_ICON_PATH = "stars_icon.png"
FONTS_DIR = "fonts/"
GIFTS_DIR = "gifts/assets/"
METADATA_PATH = "gifts_metadata.json"
HISTORY_PATH = "price_history.json"

# ========== РАЗМЕРЫ И ПОЗИЦИИ ==========
GIFT_SIZE = (250, 250)
GIFT_POS = (130, 30)

ICON_SIZE = (40, 39)
ICON_SPACING = 0
TON_STARS_SEP = " • "

EXTRA_SIZE = (180, 180)
EXTRA_POS = (168, 220)

# ========== ВТОРОЙ ОВЕРЛЕЙ (только для новых подарков 115-121) ==========
# URL для автоматической загрузки, если файл не найден
EXTRA2_IMAGE_URL = "https://i.postimg.cc/sx0rWZtZ/Bez-nazvania95-20260412140849.png"
EXTRA2_IMAGE_PATH = "extra2.png"
# Размер и позиция — меняй по необходимости
EXTRA2_SIZE = (500, 500)
EXTRA2_POS = (-16, -270)

# ========== ШРИФТЫ ==========
# Доступные варианты (просто измени FONT_NAME):
#   Inter-Bold      — современный, геометричный
#   Montserrat-Bold — элегантный, широкий
#   Roboto-Bold     — чёткий, читабельный
#   Oswald-Bold     — узкий, вытянутый
#   BebasNeue       — жирный, плакатный (только заглавные)
#   Nunito-Bold     — мягкий, закруглённый
FONT_SIZE_USD = 70
FONT_SIZE_TONSTAR = 28
FONT_SIZE_DATE = 25
FONT_SIZE_GROWTH = 30
FONT_SIZE_PCS = 18

FONT_FILE_USD = "fonts/BebasNeue.ttf"
FONT_FILE_TONSTAR = "fonts/Roboto-Bold.ttf"
FONT_FILE_DATE = "fonts/Nunito-Bold.ttf"
FONT_FILE_GROWTH = "fonts/Inter-Bold.ttf"
FONT_FILE_PCS = "fonts/Roboto-Bold.ttf"

# ========== ПОЗИЦИИ ТЕКСТА ПО Y ==========
Y_USD = 320
Y_TON_STARS = 372
Y_DATE = 450
Y_GROWTH = 25
PCS_POS = (256, 313)

# ========== СМЕЩЕНИЯ ==========
ICON_Y_OFFSET_TON = 10
ICON_Y_OFFSET_STARS = 10
SEP_Y_OFFSET = -2.3
X_OFFSET_USD = 0
X_OFFSET_GROWTH = 170
GROWTH_TEXT_OFFSET_X = 0
GROWTH_TEXT_OFFSET_Y = 0

# ========== БЕЙДЖ РОСТА (верхний правый угол) ==========
GROWTH_UP_IMAGE_PATH = "growth_up.png"
GROWTH_DOWN_IMAGE_PATH = "growth_down.png"

# --- Зелёная лента (рост) ---
GROWTH_UP_SIZE         = (450, 300)   # (ширина, высота)
GROWTH_UP_POS          = (240, -55)   # позиция вставки на стикере (x, y)
GROWTH_UP_TEXT_CENTER  = (451, 49)    # центр текста на стикере (x, y)
GROWTH_UP_TEXT_ANGLE   = -41.3        # угол поворота текста

# --- Красная лента (падение) ---
GROWTH_DOWN_SIZE       = (450, 300)   # (ширина, высота)
GROWTH_DOWN_POS        = (250, -59)   # позиция вставки на стикере (x, y)
GROWTH_DOWN_TEXT_CENTER = (453, 49)   # центр текста на стикере (x, y)
GROWTH_DOWN_TEXT_ANGLE  = -41.3       # угол поворота текста

# --- Общие настройки текста ---
GROWTH_BADGE_FONT_SIZE = 30
GROWTH_BADGE_FONT_FILE = "fonts/Inter-Bold.ttf"
GROWTH_BADGE_TEXT_COLOR = "white"

# ========== ЦВЕТА ==========
COLOR_USD = "#F0B71A"
COLOR_TON = "#F0B71A"
COLOR_STARS = "#F0B71A"
COLOR_SEP = "#F0B71A"
COLOR_DATE = "#F0B71A"
COLOR_GROWTH_PLUS = "green"
COLOR_GROWTH_MINUS = "red"
COLOR_PCS = "#000000"

# ========== ПРОЗРАЧНОСТЬ (0-255) ==========
OPACITY_USD = 255
OPACITY_TON = 255
OPACITY_STARS = 255
OPACITY_SEP = 255
OPACITY_DATE = 255
OPACITY_GROWTH = 255
OPACITY_PCS= 255

# ========== КОНВЕРТАЦИЯ ВАЛЮТ ==========
# Цена одной Звезды в USD (Fragment: $0.015/Star)
STAR_PRICE_USD = 0.015
