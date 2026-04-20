"""
Генерирует один тестовый стикер и сохраняет как preview.png.
Запускается автоматически через preview_watcher.py при изменении файлов.
"""

import importlib
import sys

# Сбрасываем кэш модулей чтобы подхватить свежий config
for mod in ["config", "renderer", "gifts"]:
    if mod in sys.modules:
        del sys.modules[mod]

import config
importlib.invalidate_caches()

from renderer import StickerRenderer

PREVIEW_GIFT_ID = 64  # Durov's Cap — для превью, меняй на любой 1-120

SAMPLE_PRICE = {
    "price_ton": 589.97,
    "price_usd": 835.34,
    "price_stars": 55457,
    "pcs": 4774,
    "growth": 12.5,
}

if __name__ == "__main__":
    renderer = StickerRenderer()
    img = renderer.render_one(PREVIEW_GIFT_ID, SAMPLE_PRICE)
    img.save("preview.png", "PNG")
