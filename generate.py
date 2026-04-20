from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import requests
from io import BytesIO
import random
import glob

# =============================================================
#   ВСЕ НАСТРОЙКИ — МЕНЯЙ ТОЛЬКО ЗДЕСЬ
# =============================================================

# Размер подарка (ширина, высота)
GIFT_SIZE = (250, 250)

# Позиция подарка (X от левого края, Y от верхнего)
GIFT_POS = (130, 30)

# Размер иконок TON / Stars
ICON_SIZE = (40, 39)

# Отступ между иконкой и числом цены (отрицательное = ближе)
ICON_SPACING = 0

# Разделитель между TON и Stars. Убрать — поставь ""
TON_STARS_SEP = " • "

# --- Дополнительный PNG объект ---
URL_EXTRA  = "https://i.postimg.cc/hG7QPsqt/Без_названия68_20260410164805.png"
EXTRA_SIZE = (180, 180)   # (ширина, высота)
EXTRA_POS  = (168, 190)   # (X от левого края, Y от верхнего)

# --- Размеры шрифтов ---
FONT_SIZE_USD     = 60   # размер цены в $
FONT_SIZE_TONSTAR = 28   # размер цен в TON и Stars
FONT_SIZE_DATE    = 25  # размер даты
FONT_SIZE_GROWTH  = 30   # размер процента роста

# --- Шрифты для каждого элемента ---
FONT_FILE_USD     = "fonts/Inter-Bold.ttf"
FONT_FILE_TONSTAR = "fonts/Inter-Bold.ttf"
FONT_FILE_DATE    = "fonts/Inter-Bold.ttf"
FONT_FILE_GROWTH  = "fonts/Inter-Bold.ttf"

# --- Y-позиции строк (больше = ниже) ---
Y_USD       = 330
Y_TON_STARS = 392
Y_DATE      = 450
Y_GROWTH    = 30

# --- Смещение иконок по вертикали (0 = без сдвига, + = ниже, - = выше) ---
# Двигает ТОЛЬКО иконку, текст рядом с ней остаётся на месте
ICON_Y_OFFSET_TON   = 6.5   # сдвиг логотипа TON
ICON_Y_OFFSET_STARS = 7.2   # сдвиг иконки Stars

# Сдвиг разделителя по вертикали
SEP_Y_OFFSET = -6

# --- Смещение по X (0 = по центру, + = вправо, - = влево) ---
X_OFFSET_USD    = 0
X_OFFSET_GROWTH = 170

# --- Цвета текста ---
COLOR_USD          = "#F0B71A"
COLOR_TON          = "#F0B71A"
COLOR_STARS        = "#F0B71A"
COLOR_SEP          = "#F0B71A"
COLOR_DATE         = "#F0B71A"
COLOR_GROWTH_PLUS  = "green"
COLOR_GROWTH_MINUS = "red"

# --- Прозрачность текста (255 = полностью видимый, 0 = невидимый) ---
# Смешивается с фоном, не белеет
OPACITY_USD     = 255
OPACITY_TON     = 255
OPACITY_STARS   = 255
OPACITY_SEP     = 255
OPACITY_DATE    = 255
OPACITY_GROWTH  = 255

# --- Ссылки на изображения ---
URL_BASE  = "https://i.postimg.cc/3WM6qpvk/Bez-nazvania90-20260410195148.png"
URL_GIFT  = "https://i.postimg.cc/KYNPwGxc/gifts_emoji_by_gifts_changes_bot_Ag_ADR1k_AAi_WAUEs.webp"
URL_TON   = "https://i.postimg.cc/66jd7L0F/Без_названия83_20260410133905.png"
URL_STARS = "https://i.postimg.cc/dQH87m6K/Без_названия62_20260410134245.png"

# =============================================================
#   КОД НИЖЕ НЕ ТРОГАЙ
# =============================================================

def load_image(url):
    response = requests.get(url, timeout=15)
    return Image.open(BytesIO(response.content)).convert("RGBA")


def get_font(size, font_file=""):
    paths = []
    if font_file:
        paths.append(font_file)
    paths += [
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans.ttf",
        "arial.ttf",
        "arial_downloaded.ttf",
    ]
    for path in paths:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    for pattern in ["/nix/store/*/share/fonts/**/*.ttf", "/usr/share/fonts/**/*.ttf"]:
        for match in glob.glob(pattern, recursive=True):
            try:
                return ImageFont.truetype(match, size)
            except Exception:
                continue
    try:
        resp = requests.get(
            "https://github.com/matomo-org/travis-scripts/raw/master/fonts/Arial.ttf",
            timeout=15,
        )
        with open("arial_downloaded.ttf", "wb") as f:
            f.write(resp.content)
        return ImageFont.truetype("arial_downloaded.ttf", size)
    except Exception:
        return ImageFont.load_default()


def text_size(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1], bbox[0]


def icon_vis_left(icon):
    bbox = icon.getbbox()
    return bbox[0] if bbox else 0


def draw_text_transparent(img, xy, text, font, color, opacity=255):
    """Рисует текст правильно смешиваясь с фоном, не белеет."""
    if opacity >= 255:
        draw = ImageDraw.Draw(img)
        draw.text(xy, text, fill=color, font=font)
        return
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    layer_draw = ImageDraw.Draw(layer)
    c = Image.new("RGBA", (1, 1), color)
    r, g, b, _ = c.getpixel((0, 0))
    layer_draw.text(xy, text, fill=(r, g, b, 255), font=font)
    r_ch, g_ch, b_ch, a_ch = layer.split()
    a_ch = a_ch.point(lambda p: p * opacity // 255)
    layer = Image.merge("RGBA", (r_ch, g_ch, b_ch, a_ch))
    img.alpha_composite(layer)


def draw_double_with_icons(img, draw, center_x, y,
                           text1, icon1, color1, icon1_y_offset,
                           text2, icon2, color2, icon2_y_offset,
                           sep_y_offset,
                           font, img_width, sep="",
                           opacity1=255, opacity2=255, sep_opacity=255,
                           sep_color=None):
    current_font = font
    font_size = getattr(current_font, "size", FONT_SIZE_TONSTAR)
    vis1 = icon_vis_left(icon1)
    vis2 = icon_vis_left(icon2)
    if sep_color is None:
        sep_color = color1

    while font_size >= 10:
        tw1, _, tx1 = text_size(draw, text1, current_font)
        tw2, _, tx2 = text_size(draw, text2, current_font)
        sw, _, _ = text_size(draw, sep, current_font) if sep else (0, 0, 0)
        vw = (icon1.width + ICON_SPACING - tx1 + tw1 - vis1
              + sw
              + icon2.width + ICON_SPACING - tx2 + tw2 - vis2)
        if vw <= img_width - 10:
            break
        font_size -= 2
        current_font = get_font(font_size, FONT_FILE_TONSTAR)

    tw1, th1, tx1_off = text_size(draw, text1, current_font)
    tw2, th2, tx2_off = text_size(draw, text2, current_font)
    sep_w, sep_h, sep_off = text_size(draw, sep, current_font) if sep else (0, 0, 0)

    visual_width = (icon1.width + ICON_SPACING - tx1_off + tw1 - vis1
                    + sep_w
                    + icon2.width + ICON_SPACING - tx2_off + tw2 - vis2)

    x = center_x - vis1 - visual_width / 2

    img.paste(icon1, (round(x), round(y + icon1_y_offset)), icon1)
    text_y1 = y + (icon1.height - th1) // 2
    draw_text_transparent(img, (x + icon1.width + ICON_SPACING - tx1_off, text_y1),
                          text1, current_font, color1, opacity1)

    x += icon1.width + ICON_SPACING - tx1_off + tw1

    if sep:
        sep_y = y + (icon1.height - sep_h) // 2 + sep_y_offset
        draw_text_transparent(img, (x - sep_off, sep_y),
                              sep, current_font, sep_color, sep_opacity)
    x += sep_w

    img.paste(icon2, (round(x - vis2), round(y + icon2_y_offset)), icon2)
    text_y2 = y + (icon2.height - th2) // 2
    draw_text_transparent(img, (x - vis2 + icon2.width + ICON_SPACING - tx2_off, text_y2),
                          text2, current_font, color2, opacity2)


def generate_sticker():
    base  = load_image(URL_BASE)
    gift  = load_image(URL_GIFT).resize(GIFT_SIZE)
    ton   = load_image(URL_TON).resize(ICON_SIZE)
    stars = load_image(URL_STARS).resize(ICON_SIZE)
    extra = load_image(URL_EXTRA).resize(EXTRA_SIZE)

    img  = base.copy()
    draw = ImageDraw.Draw(img)

    font_usd     = get_font(FONT_SIZE_USD,     FONT_FILE_USD)
    font_tonstar = get_font(FONT_SIZE_TONSTAR,  FONT_FILE_TONSTAR)
    font_date    = get_font(FONT_SIZE_DATE,     FONT_FILE_DATE)
    font_growth  = get_font(FONT_SIZE_GROWTH,   FONT_FILE_GROWTH)

    price_usd   = round(random.uniform(100, 500), 1)
    price_ton   = round(price_usd / 7, 2)
    price_stars = int(price_usd * 70)
    date        = datetime.now().strftime("%d %b %Y %H:%M")
    growth      = round(random.uniform(-10, 15), 2)

    img.paste(gift, GIFT_POS, gift)
    img.paste(extra, EXTRA_POS, extra)
    cx = img.width // 2

    usd_text = f"${price_usd}"
    uw, uh, ux_off = text_size(draw, usd_text, font_usd)
    draw_text_transparent(img,
                          (cx - uw / 2 - ux_off + X_OFFSET_USD, Y_USD),
                          usd_text, font_usd, COLOR_USD, OPACITY_USD)

    draw_double_with_icons(
        img, draw, cx, Y_TON_STARS,
        f"{price_ton}",   ton,   COLOR_TON,   ICON_Y_OFFSET_TON,
        f"{price_stars}", stars, COLOR_STARS, ICON_Y_OFFSET_STARS,
        SEP_Y_OFFSET,
        font_tonstar, img.width,
        sep=TON_STARS_SEP,
        opacity1=OPACITY_TON,
        opacity2=OPACITY_STARS,
        sep_opacity=OPACITY_SEP,
        sep_color=COLOR_SEP,
    )

    dw, _, dx_off = text_size(draw, date, font_date)
    draw_text_transparent(img,
                          (cx - dw / 2 - dx_off, Y_DATE),
                          date, font_date, COLOR_DATE, OPACITY_DATE)

    gtext = f"{growth}%"
    gw, _, gx_off = text_size(draw, gtext, font_growth)
    gcolor = COLOR_GROWTH_PLUS if growth >= 0 else COLOR_GROWTH_MINUS
    draw_text_transparent(img,
                          (cx - gw / 2 - gx_off + X_OFFSET_GROWTH, Y_GROWTH),
                          gtext, font_growth, gcolor, OPACITY_GROWTH)

    img = img.resize((512, 512), Image.LANCZOS)
    img.save("sticker.webp", "WEBP")
    print("✅ Стикер готов!")


if __name__ == "__main__":
    generate_sticker()
