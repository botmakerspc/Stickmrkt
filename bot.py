import asyncio
import os
from datetime import datetime, timezone, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

import config
from assets import download_assets
from data_provider import GiftDataProvider
from renderer import StickerRenderer
from uploader import BatchStickerUploader

bot = None
dp = Dispatcher()

PACK_NAME = None
uploader = None
renderer = None
data_provider = None

MSK = timezone(timedelta(hours=3))


def moscow_now() -> datetime:
    """Текущее время по Москве (UTC+3)."""
    return datetime.now(MSK)


def next_round_10min(now: datetime) -> datetime:
    """Возвращает следующую круглую 10-минутку по Москве."""
    minutes_to_next = 10 - (now.minute % 10)
    if minutes_to_next == 10 and now.second == 0 and now.microsecond == 0:
        minutes_to_next = 0
    return now.replace(second=0, microsecond=0) + timedelta(minutes=minutes_to_next)


async def wait_until_next_10min():
    """Ждёт до ближайшей круглой 10-минутки по московскому времени."""
    now = moscow_now()
    target = next_round_10min(now)
    wait_seconds = (target - now).total_seconds()
    if wait_seconds > 0:
        print(f"💤 Жду до {target.strftime('%H:%M')} МСК ({wait_seconds / 60:.1f} мин)")
        await asyncio.sleep(wait_seconds)


async def get_pack_name():
    if bot is None:
        raise RuntimeError("Bot is not initialized")
    me = await bot.get_me()
    return f"nftmagnattest_by_{me.username}"


async def ensure_pack_exists():
    if bot is None:
        raise RuntimeError("Bot is not initialized")

    global PACK_NAME, renderer, data_provider

    try:
        await bot.get_sticker_set(PACK_NAME)
        print(f"✅ Стикерпак {PACK_NAME} уже существует")
    except Exception:
        print(f"📦 Создаю новый стикерпак {PACK_NAME}...")

        prices = data_provider.get_all_prices()
        first_id = list(prices.keys())[0]
        first_image = renderer.render_one(first_id, prices[first_id])

        temp_file = "temp_first_sticker.webp"
        first_image.save(temp_file, "WEBP")

        file = types.FSInputFile(temp_file)
        await bot.create_new_sticker_set(
            user_id=config.ADMIN_ID,
            name=PACK_NAME,
            title="@ruzanina",
            stickers=[
                types.InputSticker(
                    sticker=file,
                    emoji_list=["🔥"],
                    format="static"
                )
            ],
            sticker_type="regular"
        )
        if os.path.exists(temp_file):
            os.remove(temp_file)
        print("✅ Стикерпак создан!")


async def update_cycle():
    global uploader, renderer, data_provider

    # Синхронизируемся с ближайшей круглой 10-минуткой по МСК
    await wait_until_next_10min()

    while True:
        cycle_start = moscow_now()
        print(f"\n{'=' * 60}")
        print(f"🔄 НАЧАЛО ЦИКЛА: {cycle_start.strftime('%Y-%m-%d %H:%M:%S')} МСК")
        print(f"{'=' * 60}")

        try:
            print("📡 Получение данных...")
            prices = data_provider.get_all_prices()
            print(f"✅ Данные для {len(prices)} подарков получены")

            print("🎨 Генерация всех стикеров...")
            gen_start = moscow_now()
            images = renderer.render_all(prices)
            gen_duration = (moscow_now() - gen_start).total_seconds()
            print(f"✅ Сгенерировано {len(images)} стикеров за {gen_duration:.1f} сек")

            await uploader.update_all_sorted(images, prices)

        except Exception as e:
            print(f"❌ ОШИБКА В ЦИКЛЕ: {e}")
            import traceback
            traceback.print_exc()

        cycle_duration = (moscow_now() - cycle_start).total_seconds() / 60
        print(f"\n🏁 ЦИКЛ ЗАВЕРШЁН за {cycle_duration:.1f} мин | МСК: {moscow_now().strftime('%H:%M:%S')}")

        # Ждём следующую круглую 10-минутку по МСК
        await wait_until_next_10min()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    pack_url = f"https://t.me/addstickers/{PACK_NAME}"
    now = moscow_now()
    target = next_round_10min(now)
    await message.answer(
        f"👋 Привет! Я бот NFT Magnat.\n\n"
        f"📦 Стикерпак: {pack_url}\n"
        f"🎁 Подарков: {config.TOTAL_STICKERS}\n\n"
        f"Команды:\n"
        f"/update — принудительное обновление (только админ)\n"
        f"/status — статус стикерпака\n\n"
        f"⏱ Автообновление каждые {config.UPDATE_INTERVAL_MINUTES} мин по круглым минуткам МСК.\n"
        f"📊 Сортировка: дорогие в начале пака."
    )


@dp.message(Command("update"))
async def cmd_update(message: types.Message):
    if message.from_user.id != config.ADMIN_ID:
        await message.answer("⛔ Доступ запрещён")
        return

    await message.answer("🔄 Запускаю принудительное обновление...")
    try:
        prices = data_provider.get_all_prices()
        images = renderer.render_all(prices)
        await uploader.update_all_sorted(images, prices)
        await message.answer("✅ Обновление завершено!")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")


@dp.message(Command("status"))
async def cmd_status(message: types.Message):
    try:
        if bot is None:
            await message.answer("❌ Бот ещё не инициализирован")
            return
        sticker_set = await bot.get_sticker_set(PACK_NAME)
        now = moscow_now()
        target = next_round_10min(now)
        wait_min = (target - now).total_seconds() / 60
        await message.answer(
            f"📊 Статус стикерпака:\n"
            f"📦 Имя: {PACK_NAME}\n"
            f"🎁 Стикеров: {len(sticker_set.stickers)} / {config.TOTAL_STICKERS}\n"
            f"🕐 Время МСК: {now.strftime('%H:%M:%S')}\n"
            f"⏱ Следующее обновление: {target.strftime('%H:%M')} МСК (~{wait_min:.0f} мин)\n"
            f"🔗 https://t.me/addstickers/{PACK_NAME}"
        )
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")


async def main():
    global PACK_NAME, uploader, renderer, data_provider, bot

    now = moscow_now()
    print(f"🤖 Запуск бота NFT Magnat | МСК: {now.strftime('%Y-%m-%d %H:%M:%S')}")

    if not config.BOT_TOKEN:
        print("⚠️ BOT_TOKEN не задан. Добавьте секрет BOT_TOKEN, затем перезапустите бота.")
        print("✅ Код загружается корректно, но Telegram polling не стартует без токена.")
        return

    if not config.CONTEST_API_KEY:
        print("⚠️ CONTEST_API_KEY не задан. Бот запустится, но реальные цены появятся после добавления ключа.")

    bot = Bot(token=config.BOT_TOKEN)

    PACK_NAME = await get_pack_name()
    print(f"📦 Имя стикерпака: {PACK_NAME}")

    download_assets()
    renderer = StickerRenderer()
    data_provider = GiftDataProvider()
    uploader = BatchStickerUploader(bot, PACK_NAME, config.ADMIN_ID)

    await ensure_pack_exists()

    asyncio.create_task(update_cycle())

    print("✅ Бот запущен и готов к работе!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
