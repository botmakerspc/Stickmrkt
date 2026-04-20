"""
Предпросмотр стикера без запуска бота.
Запуск: python preview.py [gift_id]
Пример: python preview.py 1   — подарок #1
         python preview.py     — рандомный подарок
"""
import sys
import random
from renderer import StickerRenderer
from data_provider import GiftDataProvider

gift_id = int(sys.argv[1]) if len(sys.argv) > 1 else random.randint(1, 114)

print(f"🎨 Генерирую стикер для подарка #{gift_id}...")

provider = GiftDataProvider()
prices = provider.get_all_prices()

# Можно заменить на любые значения для теста
prices[gift_id]["price_ton"] = 1234.56
prices[gift_id]["price_usd"] = 8888.0
prices[gift_id]["price_stars"] = 622160
prices[gift_id]["growth"] = 12.34

renderer = StickerRenderer()
img = renderer.render_one(gift_id, prices[gift_id])
img.save("preview.webp", "WEBP")

print(f"✅ Сохранено: preview.webp (подарок #{gift_id})")
print("Открой файл preview.webp чтобы увидеть результат.")
