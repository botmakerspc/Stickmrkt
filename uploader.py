import asyncio
import os
from datetime import datetime
from aiogram import Bot
from aiogram.types import FSInputFile, InputSticker
from PIL import Image
import config


class BatchStickerUploader:
    """
    Атомарное обновление стикеров: удалить → добавить → поставить на позицию.
    Никакого беспорядка в паке во время цикла.
    Сортировка: от дорогих к дешёвым (дорогой — позиция 0).
    """

    def __init__(self, bot: Bot, pack_name: str, admin_id: int):
        self.bot = bot
        self.pack_name = pack_name
        self.admin_id = admin_id

    def _save_temp(self, gift_id: int, img: Image.Image) -> str:
        path = f"temp_sticker_{gift_id}.webp"
        img.resize((512, 512), Image.LANCZOS).save(path, "WEBP", quality=95)
        return path

    async def _update_atomic(self, gift_id: int, img: Image.Image,
                              price_ton: float, old_file_id: str | None,
                              target_position: int) -> bool:
        """
        Атомарный блок без пауз внутри:
        1. Удалить старый стикер
        2. Добавить новый (встаёт в конец)
        3. Сразу поставить на target_position
        """
        # 1. Удаляем старый (без паузы после)
        if old_file_id:
            try:
                await self.bot.delete_sticker_from_set(old_file_id)
            except Exception as e:
                print(f"  ⚠️ Удаление #{gift_id}: {e}")

        # 2. Добавляем новый (без паузы после)
        temp_file = self._save_temp(gift_id, img)
        try:
            file = FSInputFile(temp_file)
            await self.bot.add_sticker_to_set(
                user_id=self.admin_id,
                name=self.pack_name,
                sticker=InputSticker(
                    sticker=file,
                    emoji_list=["🔥"],
                    format="static"
                )
            )
        except Exception as e:
            print(f"  ❌ #{gift_id} добавление: {e}")
            return False
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

        # 3. Получаем file_id нового стикера (он последний в паке) и ставим на позицию
        try:
            sticker_set = await self.bot.get_sticker_set(self.pack_name)
            new_file_id = sticker_set.stickers[-1].file_id
            await self.bot.set_sticker_position_in_set(
                sticker=new_file_id,
                position=target_position
            )
            print(f"  ✅ #{gift_id} → поз.{target_position} ({price_ton} TON)")
            return True
        except Exception as e:
            print(f"  ❌ #{gift_id} установка позиции: {e}")
            return False

    async def update_all_sorted(self, images: dict, prices: dict):
        """
        Полный цикл обновления:
        1. Сортировка от дорогих к дешёвым.
        2. Для каждого стикера: атомарно удалить→добавить→позиция.
        3. Пауза 1.5 сек между стикерами.
        """
        print(f"🚀 Начинаем атомарное обновление {len(images)} стикеров")
        start_time = datetime.now()

        # Сортируем от ДОРОГИХ к ДЕШЁВЫМ (дорогой — позиция 0)
        sorted_ids = sorted(
            images.keys(),
            key=lambda gid: prices[gid]["price_ton"],
            reverse=True
        )
        print(f"📊 Позиция 0 (дорогой): #{sorted_ids[0]} "
              f"({prices[sorted_ids[0]]['price_ton']} TON) | "
              f"Позиция 119 (дешёвый): #{sorted_ids[-1]} "
              f"({prices[sorted_ids[-1]]['price_ton']} TON)")

        # Получаем текущий пак (один запрос в начале)
        try:
            sticker_set = await self.bot.get_sticker_set(self.pack_name)
            old_file_ids = [s.file_id for s in sticker_set.stickers]
            print(f"📦 Стикеров в паке: {len(old_file_ids)}")
        except Exception as e:
            print(f"⚠️ Не удалось получить пак: {e}")
            old_file_ids = []

        # Удаляем лишние стикеры если пак переполнен
        excess = len(old_file_ids) - config.TOTAL_STICKERS
        if excess > 0:
            print(f"🧹 Удаляем {excess} лишних стикеров...")
            for fid in old_file_ids[-excess:]:
                try:
                    await self.bot.delete_sticker_from_set(fid)
                except Exception as e:
                    print(f"  ⚠️ {e}")
            old_file_ids = old_file_ids[:-excess]

        # Атомарное обновление каждого стикера
        total = len(sorted_ids)
        for target_pos, gift_id in enumerate(sorted_ids):
            old_fid = old_file_ids[target_pos] if target_pos < len(old_file_ids) else None
            await self._update_atomic(
                gift_id=gift_id,
                img=images[gift_id],
                price_ton=prices[gift_id]["price_ton"],
                old_file_id=old_fid,
                target_position=target_pos
            )

            # Пауза только между стикерами, не после последнего
            if target_pos < total - 1:
                await asyncio.sleep(config.STICKER_PAUSE)

            if (target_pos + 1) % 20 == 0:
                elapsed = (datetime.now() - start_time).total_seconds()
                print(f"  📈 {target_pos + 1}/{total} за {elapsed:.0f} сек")

        elapsed = (datetime.now() - start_time).total_seconds()
        print(f"\n✅ Готово: {total} стикеров за {elapsed:.0f} сек ({elapsed / 60:.1f} мин)")
