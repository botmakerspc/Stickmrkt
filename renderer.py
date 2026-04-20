import glob
import os
from datetime import datetime, timezone
from io import BytesIO

import requests
from PIL import Image, ImageDraw, ImageFont

import config
from assets import download_assets
from gifts import GIFTS


HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


class StickerRenderer:
    def __init__(self):
        download_assets()
        os.makedirs(config.GIFTS_DIR, exist_ok=True)
        self.base = self._load_local(config.BASE_TEMPLATE_PATH)
        self.ton_icon = self._load_local(config.TON_ICON_PATH).resize(config.ICON_SIZE, Image.LANCZOS)
        self.stars_icon = self._load_local(config.STARS_ICON_PATH).resize(config.ICON_SIZE, Image.LANCZOS)
        self.extra = self._load_optional(config.EXTRA_IMAGE_PATH, config.EXTRA_SIZE)
        self.extra2 = self._load_extra2()

    def _load_local(self, path: str) -> Image.Image:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Не найден ассет: {path}")
        return Image.open(path).convert("RGBA")

    def _load_optional(self, path: str, size: tuple[int, int]) -> Image.Image | None:
        if not os.path.exists(path):
            return None
        return self._load_local(path).resize(size, Image.LANCZOS)

    def _load_extra2(self) -> Image.Image | None:
        if not os.path.exists(config.EXTRA2_IMAGE_PATH):
            try:
                response = requests.get(config.EXTRA2_IMAGE_URL, timeout=20, headers=HEADERS)
                response.raise_for_status()
                with open(config.EXTRA2_IMAGE_PATH, "wb") as file:
                    file.write(response.content)
            except Exception as exc:
                print(f"⚠️ extra2 не загружен: {exc}")
                return None
        return self._load_optional(config.EXTRA2_IMAGE_PATH, config.EXTRA2_SIZE)

    def _download_image(self, url: str, path: str) -> Image.Image:
        if not os.path.exists(path):
            response = requests.get(url, timeout=25, headers=HEADERS)
            response.raise_for_status()
            with open(path, "wb") as file:
                file.write(response.content)
        return Image.open(path).convert("RGBA")

    def _gift_image(self, gift_id: int) -> Image.Image:
        gift = GIFTS.get(gift_id)
        if not gift:
            raise KeyError(f"Подарок #{gift_id} не найден")
        # Check local overrides first (persistent replacements)
        for ext in (".webp", ".png"):
            override_path = os.path.join("gifts/overrides", f"gift_{gift_id:03d}{ext}")
            if os.path.exists(override_path):
                return Image.open(override_path).convert("RGBA").resize(config.GIFT_SIZE, Image.LANCZOS)
        ext = ".png" if gift["url"].lower().endswith(".png") else ".webp"
        path = os.path.join(config.GIFTS_DIR, f"gift_{gift_id:03d}{ext}")
        return self._download_image(gift["url"], path).resize(config.GIFT_SIZE, Image.LANCZOS)

    def _font(self, size: int, path: str) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
        paths = [path]
        paths.extend(
            [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
                "/usr/share/fonts/liberation/LiberationSans-Bold.ttf",
            ]
        )
        for candidate in paths:
            try:
                return ImageFont.truetype(candidate, size)
            except Exception:
                pass
        for pattern in ["/nix/store/*/share/fonts/**/*.ttf", "/usr/share/fonts/**/*.ttf"]:
            for candidate in glob.glob(pattern, recursive=True):
                try:
                    return ImageFont.truetype(candidate, size)
                except Exception:
                    pass
        return ImageFont.load_default()

    def _text_size(self, draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> tuple[int, int, int]:
        bbox = draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0], bbox[3] - bbox[1], bbox[0]

    def _draw_text(
        self,
        image: Image.Image,
        xy: tuple[float, float],
        text: str,
        font: ImageFont.ImageFont,
        color: str,
        opacity: int = 255,
    ):
        if opacity >= 255:
            ImageDraw.Draw(image).text(xy, text, fill=color, font=font)
            return
        layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(layer)
        r, g, b, _ = Image.new("RGBA", (1, 1), color).getpixel((0, 0))
        draw.text(xy, text, fill=(r, g, b, 255), font=font)
        r_ch, g_ch, b_ch, a_ch = layer.split()
        a_ch = a_ch.point(lambda p: p * opacity // 255)
        image.alpha_composite(Image.merge("RGBA", (r_ch, g_ch, b_ch, a_ch)))

    def _visible_left(self, icon: Image.Image) -> int:
        bbox = icon.getbbox()
        return bbox[0] if bbox else 0

    def _draw_price_line(
        self,
        image: Image.Image,
        draw: ImageDraw.ImageDraw,
        center_x: int,
        y: int,
        ton_text: str,
        stars_text: str,
        font: ImageFont.ImageFont,
    ):
        current_font = font
        font_size = getattr(current_font, "size", config.FONT_SIZE_TONSTAR)
        vis1 = self._visible_left(self.ton_icon)
        vis2 = self._visible_left(self.stars_icon)
        while font_size >= 10:
            tw1, _, tx1 = self._text_size(draw, ton_text, current_font)
            tw2, _, tx2 = self._text_size(draw, stars_text, current_font)
            sw, _, _ = self._text_size(draw, config.TON_STARS_SEP, current_font)
            width = (
                self.ton_icon.width
                + config.ICON_SPACING
                - tx1
                + tw1
                - vis1
                + sw
                + self.stars_icon.width
                + config.ICON_SPACING
                - tx2
                + tw2
                - vis2
            )
            if width <= image.width - 10:
                break
            font_size -= 2
            current_font = self._font(font_size, config.FONT_FILE_TONSTAR)

        tw1, th1, tx1 = self._text_size(draw, ton_text, current_font)
        tw2, th2, tx2 = self._text_size(draw, stars_text, current_font)
        sw, sh, so = self._text_size(draw, config.TON_STARS_SEP, current_font)
        width = (
            self.ton_icon.width
            + config.ICON_SPACING
            - tx1
            + tw1
            - vis1
            + sw
            + self.stars_icon.width
            + config.ICON_SPACING
            - tx2
            + tw2
            - vis2
        )
        x = center_x - vis1 - width / 2
        image.paste(self.ton_icon, (round(x), round(y + config.ICON_Y_OFFSET_TON)), self.ton_icon)
        self._draw_text(
            image,
            (x + self.ton_icon.width + config.ICON_SPACING - tx1, y + (self.ton_icon.height - th1) // 2),
            ton_text,
            current_font,
            config.COLOR_TON,
            config.OPACITY_TON,
        )
        x += self.ton_icon.width + config.ICON_SPACING - tx1 + tw1
        self._draw_text(
            image,
            (x - so, y + (self.ton_icon.height - sh) // 2 + config.SEP_Y_OFFSET),
            config.TON_STARS_SEP,
            current_font,
            config.COLOR_SEP,
            config.OPACITY_SEP,
        )
        x += sw
        image.paste(self.stars_icon, (round(x - vis2), round(y + config.ICON_Y_OFFSET_STARS)), self.stars_icon)
        self._draw_text(
            image,
            (x - vis2 + self.stars_icon.width + config.ICON_SPACING - tx2, y + (self.stars_icon.height - th2) // 2),
            stars_text,
            current_font,
            config.COLOR_STARS,
            config.OPACITY_STARS,
        )

    def _format_usd(self, value: float) -> str:
        if value >= 1000:
            return f"${value:,.0f}".replace(",", " ")
        if value >= 100:
            return f"${value:.0f}"
        return f"${value:.2f}".rstrip("0").rstrip(".")

    def _format_ton(self, value: float) -> str:
        if value >= 1000:
            return f"{value:,.0f}".replace(",", " ")
        if value >= 100:
            return f"{value:.1f}".rstrip("0").rstrip(".")
        return f"{value:.2f}".rstrip("0").rstrip(".")

    def _format_stars(self, value: int) -> str:
        return f"{value:,}".replace(",", " ")

    def _draw_growth(self, image: Image.Image, draw: ImageDraw.ImageDraw, growth: float):
        if growth >= 0:
            badge_path = config.GROWTH_UP_IMAGE_PATH
            size = config.GROWTH_UP_SIZE
            pos = config.GROWTH_UP_POS
            center = config.GROWTH_UP_TEXT_CENTER
            angle = config.GROWTH_UP_TEXT_ANGLE
            color = "#19A948"
            sign = "+"
        else:
            badge_path = config.GROWTH_DOWN_IMAGE_PATH
            size = config.GROWTH_DOWN_SIZE
            pos = config.GROWTH_DOWN_POS
            center = config.GROWTH_DOWN_TEXT_CENTER
            angle = config.GROWTH_DOWN_TEXT_ANGLE
            color = "#D93636"
            sign = ""
        text = f"{sign}{growth:.2f}%"
        font = self._font(config.GROWTH_BADGE_FONT_SIZE, config.GROWTH_BADGE_FONT_FILE)
        text_center = (
            center[0] + config.GROWTH_TEXT_OFFSET_X,
            center[1] + config.GROWTH_TEXT_OFFSET_Y,
        )
        if os.path.exists(badge_path):
            badge = self._load_local(badge_path).resize(size, Image.LANCZOS)
            image.paste(badge, pos, badge)
            layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
            layer_draw = ImageDraw.Draw(layer)
            tw, th, tx = self._text_size(layer_draw, text, font)
            layer_draw.text((text_center[0] - tw / 2 - tx, text_center[1] - th / 2), text, font=font, fill=config.GROWTH_BADGE_TEXT_COLOR)
            image.alpha_composite(layer.rotate(angle, center=center, resample=Image.Resampling.BICUBIC))
            return

        ribbon = Image.new("RGBA", image.size, (0, 0, 0, 0))
        ribbon_draw = ImageDraw.Draw(ribbon)
        ribbon_width = 190
        ribbon_height = 48
        x0 = center[0] - ribbon_width / 2
        y0 = center[1] - ribbon_height / 2
        x1 = center[0] + ribbon_width / 2
        y1 = center[1] + ribbon_height / 2
        shadow_offset = 4
        ribbon_draw.rounded_rectangle(
            (x0 + shadow_offset, y0 + shadow_offset, x1 + shadow_offset, y1 + shadow_offset),
            radius=18,
            fill=(0, 0, 0, 90),
        )
        ribbon_draw.rounded_rectangle((x0, y0, x1, y1), radius=18, fill=color)
        ribbon_draw.line((x0 + 18, y0 + 8, x1 - 18, y0 + 8), fill=(255, 255, 255, 55), width=2)
        ribbon = ribbon.rotate(angle, center=center, resample=Image.Resampling.BICUBIC)
        image.alpha_composite(ribbon)

        text_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
        text_draw = ImageDraw.Draw(text_layer)
        tw, th, tx = self._text_size(text_draw, text, font)
        text_draw.text(
            (text_center[0] - tw / 2 - tx, text_center[1] - th / 2 - 2),
            text,
            font=font,
            fill=config.GROWTH_BADGE_TEXT_COLOR,
        )
        image.alpha_composite(text_layer.rotate(angle, center=center, resample=Image.Resampling.BICUBIC))

    def _draw_pcs(self, image: Image.Image, draw: ImageDraw.ImageDraw, pcs: int):
        text = f"{pcs:,} pcs".replace(",", " ")
        font = self._font(config.FONT_SIZE_PCS, config.FONT_FILE_PCS)
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        self._draw_text(
            image,
            (config.PCS_POS[0] - tw / 2 - bbox[0], config.PCS_POS[1] - th / 2 - bbox[1]),
            text,
            font,
            config.COLOR_PCS,
            config.OPACITY_PCS,
        )

    def render_one(self, gift_id: int, price: dict) -> Image.Image:
        image = self.base.copy()
        draw = ImageDraw.Draw(image)
        gift = self._gift_image(gift_id)
        image.paste(gift, config.GIFT_POS, gift)
        if self.extra:
            image.paste(self.extra, config.EXTRA_POS, self.extra)
        if gift_id in config.NEW_GIFT_IDS and self.extra2:
            image.paste(self.extra2, config.EXTRA2_POS, self.extra2)

        font_usd = self._font(config.FONT_SIZE_USD, config.FONT_FILE_USD)
        font_tonstar = self._font(config.FONT_SIZE_TONSTAR, config.FONT_FILE_TONSTAR)
        font_date = self._font(config.FONT_SIZE_DATE, config.FONT_FILE_DATE)
        center_x = image.width // 2

        usd_text = self._format_usd(float(price.get("price_usd", 0)))
        ton_text = self._format_ton(float(price.get("price_ton", 0)))
        stars_text = self._format_stars(int(price.get("price_stars", 0)))
        date_text = datetime.now(timezone.utc).strftime("%d %b %Y %H:%M") + " (UTC)"
        growth = float(price.get("growth", 0))
        pcs = int(price.get("pcs", 0))

        tw, _, tx = self._text_size(draw, usd_text, font_usd)
        self._draw_text(image, (center_x - tw / 2 - tx + config.X_OFFSET_USD, config.Y_USD), usd_text, font_usd, config.COLOR_USD, config.OPACITY_USD)
        self._draw_pcs(image, draw, pcs)
        self._draw_price_line(image, draw, center_x, config.Y_TON_STARS, ton_text, stars_text, font_tonstar)
        dw, _, dx = self._text_size(draw, date_text, font_date)
        self._draw_text(image, (center_x - dw / 2 - dx, config.Y_DATE), date_text, font_date, config.COLOR_DATE, config.OPACITY_DATE)
        self._draw_growth(image, draw, growth)
        return image.resize((512, 512), Image.LANCZOS)

    def render_all(self, prices: dict[int, dict]) -> dict[int, Image.Image]:
        return {gift_id: self.render_one(gift_id, price) for gift_id, price in prices.items()}