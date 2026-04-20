import json
import os
import re
import requests
import time
from datetime import datetime, timedelta
from typing import Dict, Optional
import config


# ========== МАППИНГ ИМЁН ==========
# Несовпадения между gifts.py и API (gifts.py -> API title)
NAME_OVERRIDES = {
    "Mood pack": "Mood Pack",
    "Timeless book": "Timeless Book",
    "Pool float": "Pool Float",
    "Low rider": "Low Rider",
    "Snoop cigar": "Snoop Cigar",
    "Swag bag": "Swag Bag",
    "Snoop dog": "Snoop Dogg",
    "Rare bird": "Rare Bird",
    "Chill flame": "Chill Flame",
    "Bling binky": "Bling Binky",
    "Ice cream": "Ice Cream",
    "Vice cream": "Vice Cream",
    "Spring basket": "Spring Basket",
    "Happy brownie": "Happy Brownie",
    "Moon pendant": "Moon Pendant",
    "Clover pin": "Clover Pin",
    "Money pot": "Money Pot",
    "Neko helmet": "Neko Helmet",
    "Mousse cake": "Mousse Cake",
    "Pretty posy": "Pretty Posy",
    "Mighty arm": "Mighty Arm",
    "Heroic helmet": "Heroic Helmet",
    "Top hat": "Top Hat",
    "Bow tie": "Bow Tie",
    "Light sword": "Light Sword",
    "Boned ring": "Bonded Ring",
    "Valentine box": "Valentine Box",
    "Love potion": "Love Potion",
    "Toy bear": "Toy Bear",
    "Diamond ring": "Diamond Ring",
    "Cupid charm": "Cupid Charm",
    "Restless jar": "Restless Jar",
    "Loot bag": "Loot Bag",
    "Sky stilettos": "Sky Stilettos",
    "Lunar snake": "Lunar Snake",
    "Big year": "Big Year",
    "Pet snake": "Pet Snake",
    "Snake box": "Snake Box",
    "Tama gadget": "Tama Gadget",
    "Candy cane": "Candy Cane",
    "Xmas stocking": "Xmas Stocking",
    "Cookie heart": "Cookie Heart",
    "Heart locket": "Heart Locket",
    "Ginger cookie": "Ginger Cookie",
    "Winter wreath": "Winter Wreath",
    "Santa hat": "Santa Hat",
    "Snow globe": "Snow Globe",
    "Snow mittens": "Snow Mittens",
    "Sleigh bell": "Sleigh Bell",
    "Jester hat": "Jester Hat",
    "Star notepad": "Star Notepad",
    "Bunny muffin": "Bunny Muffin",
    "Swiss watch": "Swiss Watch",
    "Genie lamp": "Genie Lamp",
    "Astral shard": "Astral Shard",
    "Precious peach": "Precious Peach",
    "Plush Pepe": "Plush Pepe",
    "Handing star": "Hanging Star",
    "Durov's caps": "Durov\u2019s Cap",
    "Perfume bottle": "Perfume Bottle",
    "Mini Oskar": "Mini Oscar",
    "Berry box": "Berry Box",
    "Vintage cigar": "Vintage Cigar",
    "Record player": "Record Player",
    "Magic potion": "Magic Potion",
    "Electric skull": "Electric Skull",
    "Kissed frog": "Kissed Frog",
    "Party sparkler": "Party Sparkler",
    "Jingle bells": "Jingle Bells",
    "Jelly bunny": "Jelly Bunny",
    "Joyful bundle": "Joyful Bundle",
    "Jolly chimp": "Jolly Chimp",
    "Instant ramen": "Instant Ramen",
    "Holiday drink": "Holiday Drink",
    "Victory medal": "Victory Medal",
    "Stellar rocket": "Stellar Rocket",
    "Ionic dryer": "Ionic Dryer",
    "Fresh socks": "Fresh Socks",
    "Input key": "Input Key",
    "Lush bouquet": "Lush Bouquet",
    "Signet ring": "Signet Ring",
    "Spiced vine": "Spiced Wine",
    "Love candle": "Love Candle",
    "Eternal rose": "Eternal Rose",
    "Jack-in-the-box": "Jack-in-the-Box",
    "Gem signet": "Gem Signet",
    "Easter egg": "Easter Egg",
    "Hypno lollipop": "Hypno Lollipop",
    "Hex pot": "Hex Pot",
    "Sharp tongue": "Sharp Tongue",
    "Mad pumpkin": "Mad Pumpkin",
    "Trapped heart": "Trapped Heart",
    "Skull flower": "Skull Flower",
    "Crystal ball": "Crystal Ball",
    "Flying broom": "Flying Broom",
    "Voodoo doll": "Voodoo Doll",
    "Scared cat": "Scared Cat",
    "Witch hat": "Witch Hat",
    "Eternal candle": "Eternal Candle",
    "Spy agaric": "Spy Agaric",
    "Sakura flower": "Sakura Flower",
    "Homemade cake": "Homemade Cake",
    "Desk calendar": "Desk Calendar",
    "B-day candle": "B-Day Candle",
    "Lol pop": "Lol Pop",
    "Whip cupcake": "Whip Cupcake",
    "Evil eye": "Evil Eye",
    "UFC strike": "UFC Strike",
    "Ion gem": "Ion Gem",
    "Khabib's Papakha": "Khabib\u2019s Papakha",
    "Durov's boots": "Durov\u2019s Boots",
    "Durov's coat": "Durov\u2019s Coat",
    "Durov's figurine": "Durov\u2019s Figurine",
    "Gravestone": "Gravestone",
    "Mask": "Mask",
    "Coffin": "Coffin",
}

FIXED_PCS_BY_GIFT_ID = {
    1: 29000,
    2: 198560,
    3: 99421,
    4: 246862,
    5: 11992,
    6: 23950,
    7: 119573,
    8: 237970,
    9: 593781,
    10: 14971,
    11: 482271,
    12: 9990,
    13: 342255,
    14: 490553,
    15: 231311,
    16: 6852,
    17: 264231,
    18: 172784,
    19: 111080,
    20: 270970,
    21: 91779,
    22: 16149,
    23: 230505,
    24: 181231,
    25: 4123,
    26: 3794,
    27: 35099,
    28: 65687,
    29: 131222,
    30: 8130,
    31: 4818,
    32: 41025,
    33: 30412,
    34: 56724,
    35: 32924,
    36: 33112,
    37: 120184,
    38: 14489,
    39: 58460,
    40: 259346,
    41: 101415,
    42: 279106,
    43: 273898,
    44: 135097,
    45: 320622,
    46: 334622,
    47: 264486,
    48: 1973,
    49: 188888,
    50: 100846,
    51: 89034,
    52: 72788,
    53: 49969,
    54: 28000,
    55: 190222,
    56: 99082,
    57: 66655,
    58: 29323,
    59: 7666,
    60: 6196,
    61: 3160,
    62: 2861,
    63: 58118,
    64: 4774,
    65: 4848,
    66: 5614,
    67: 66580,
    68: 31024,
    69: 46888,
    70: 4871,
    71: 9407,
    72: 14278,
    73: 243771,
    74: 106652,
    75: 129350,
    76: 114092,
    77: 132155,
    78: 457382,
    79: 120989,
    80: 124608,
    81: 156318,
    82: 25719,
    83: 200509,
    84: 159570,
    85: 140116,
    86: 18499,
    87: 146090,
    88: 30296,
    89: 37640,
    90: 97345,
    91: 6962,
    92: 173176,
    93: 116639,
    94: 69837,
    95: 8546,
    96: 22199,
    97: 26407,
    98: 24126,
    99: 27732,
    100: 25916,
    101: 27620,
    102: 19289,
    103: 88480,
    104: 46590,
    105: 89438,
    106: 93115,
    107: 199482,
    108: 308449,
    109: 307521,
    110: 468745,
    111: 367619,
    112: 65204,
    113: 60000,
    114: 4692,
    115: 10000,
    116: 10000,
    117: 4100,
    118: 10000,
    119: 250000,
    120: 40000,
}


class PriceHistory:
    """
    Хранит историю цен для расчёта % роста за 24 часа.
    Формат: { "1": {"price_24h_ago": 123.45, "timestamp": 1712746800}, ... }
    """

    def __init__(self):
        self.history_file = config.HISTORY_PATH
        self.history = self._load()

    def _load(self) -> dict:
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _save(self):
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, indent=2, ensure_ascii=False)

    def get_growth(self, gift_id: int, current_price: float) -> float:
        now = datetime.now().timestamp()
        key = str(gift_id)

        if key not in self.history:
            self.history[key] = {"price_24h_ago": current_price, "timestamp": now}
            self._save()
            return 0.0

        record = self.history[key]
        hours_passed = (now - record["timestamp"]) / 3600
        old_price = record["price_24h_ago"]

        if hours_passed >= 24:
            self.history[key] = {"price_24h_ago": current_price, "timestamp": now}
            self._save()

        if old_price == 0:
            return 0.0

        return round(((current_price - old_price) / old_price) * 100, 2)


class PriceConverter:
    """Конвертер TON -> USD и TON -> Stars."""

    def __init__(self):
        self.ton_usd_rate = 1.37
        self.stars_per_ton = int(1.37 / config.STAR_PRICE_USD)
        self.refresh_rates()

    def refresh_rates(self):
        import re as _re

        # 1. Fragment HTML — tonRate
        try:
            resp = requests.get(
                "https://fragment.com/stars",
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
                timeout=10
            )
            match = _re.search(r'ajInit\(\{.*?"tonRate"\s*:\s*([\d.]+)', resp.text)
            if not match:
                raise ValueError("tonRate не найден")
            self.ton_usd_rate = float(match.group(1))
            self.stars_per_ton = int(self.ton_usd_rate / config.STAR_PRICE_USD)
            print(f"💱 TON/USD: {self.ton_usd_rate:.4f} (Fragment)")
            print(f"⭐ Stars/TON: {self.stars_per_ton}")
            return
        except Exception as e:
            print(f"⚠️ Fragment: {e}")

        # 2. CoinGecko fallback
        try:
            resp = requests.get(
                "https://api.coingecko.com/api/v3/simple/price?ids=the-open-network&vs_currencies=usd",
                timeout=10
            )
            self.ton_usd_rate = float(resp.json()["the-open-network"]["usd"])
            self.stars_per_ton = int(self.ton_usd_rate / config.STAR_PRICE_USD)
            print(f"💱 TON/USD: {self.ton_usd_rate:.4f} (CoinGecko)")
        except Exception as e:
            print(f"⚠️ CoinGecko: {e}, используем {self.ton_usd_rate:.4f}")

    def ton_to_usd(self, ton: float) -> float:
        return round(ton * self.ton_usd_rate, 2)

    def ton_to_stars(self, ton: float) -> int:
        return int(ton * self.stars_per_ton)


class ContestApiClient:
    """Клиент для Contest API — получает реальные floor prices."""

    API_URL = "https://contest.tgmrkt.io/contest/v1/gifts-collections"

    def __init__(self):
        self.api_key = config.CONTEST_API_KEY
        if not self.api_key:
            print("⚠️ CONTEST_API_KEY не задан — цены будут None")
        # Нормализованная таблица: lower(title) -> price_ton
        self._cache: Dict[str, Optional[float]] = {}
        self._last_fetch = 0.0

    @staticmethod
    def _normalize(name: str) -> str:
        """Приводим к нижнему регистру для нечёткого совпадения."""
        return name.lower().strip()

    def fetch(self) -> bool:
        """Загружает все коллекции и кэширует цены. Возвращает True при успехе."""
        if not self.api_key:
            return False
        try:
            resp = requests.get(
                self.API_URL,
                headers={"X-CONTEST-KEY": self.api_key, "User-Agent": "Mozilla/5.0"},
                timeout=15
            )
            resp.raise_for_status()
            data = resp.json()
            self._cache = {}
            for item in data:
                title = item.get("title", "")
                fp = item.get("floorPrice")
                price_ton = float(fp) / 1e9 if fp is not None else None
                self._cache[self._normalize(title)] = price_ton
            self._last_fetch = datetime.now().timestamp()
            print(f"📡 Contest API: загружено {len(self._cache)} коллекций")
            return True
        except Exception as e:
            print(f"❌ Contest API ошибка: {e}")
            return False

    def get_price_ton(self, gift_name: str) -> Optional[float]:
        """Возвращает floor price в TON для подарка по имени, или None."""
        # Применяем маппинг если есть
        api_name = NAME_OVERRIDES.get(gift_name, gift_name)
        key = self._normalize(api_name)
        return self._cache.get(key)


class TonAPISupplyProvider:
    """
    Получает реальный PCS (тираж) через TonAPI.
    Адреса коллекций берёт из collection_addresses.json (gift_name → TON address).
    Supply кэшируется в supply_cache.json и обновляется раз в 24 часа.
    Для Telegram gift коллекций (next_item_index=-1) считает items постранично.
    """

    TONAPI_BASE = "https://tonapi.io/v2"
    ADDRESSES_FILE = "collection_addresses.json"
    SUPPLY_CACHE_FILE = "supply_cache.json"
    SUPPLY_TTL_HOURS = 24
    PAGE_SIZE = 1000

    def __init__(self):
        self.addresses: Dict[str, str] = self._load_json(self.ADDRESSES_FILE)
        self.supply_cache: Dict[str, Dict] = self._load_json(self.SUPPLY_CACHE_FILE)
        if self.addresses:
            print(f"📋 TonAPI адресов в кэше: {len(self.addresses)}")
        # Обновляем supply для всех известных адресов (если кэш устарел)
        self._refresh_stale()

    def _load_json(self, path: str) -> dict:
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_json(self, path: str, data: dict):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _is_stale(self, address: str) -> bool:
        entry = self.supply_cache.get(address)
        if not entry:
            return True
        updated_at = entry.get("updated_at", 0)
        return (time.time() - updated_at) > self.SUPPLY_TTL_HOURS * 3600

    def _refresh_stale(self):
        """Обновляет supply для адресов с устаревшим кэшем."""
        stale = [addr for addr in self.addresses.values() if self._is_stale(addr)]
        if not stale:
            return
        print(f"🔄 TonAPI: обновляю supply для {len(stale)} коллекций...")
        for name, addr in self.addresses.items():
            if self._is_stale(addr):
                count = self._count_items(addr)
                if count is not None:
                    self.supply_cache[addr] = {"supply": count, "updated_at": time.time()}
                    print(f"  ✅ {name}: {count:,} PCS")
                else:
                    print(f"  ⚠️ {name}: не удалось получить supply")
        self._save_json(self.SUPPLY_CACHE_FILE, self.supply_cache)

    def _count_items(self, address: str) -> Optional[int]:
        """
        Определяет total supply через максимальный серийный номер среди всех items.
        Telegram gift NFTs имеют имена вида "Plush Pepe #2825".
        Часть items могут быть конвертированы в wearable (burned), поэтому
        простой подсчёт count() даёт заниженное значение.
        Максимальный #N = реальный total supply.
        """
        import re as _re
        max_num = 0
        raw_count = 0
        offset = 0
        max_pages = 200  # до 200 000 items
        try:
            while offset < max_pages * self.PAGE_SIZE:
                resp = requests.get(
                    f"{self.TONAPI_BASE}/nfts/collections/{address}/items",
                    params={"limit": self.PAGE_SIZE, "offset": offset},
                    headers={"Accept": "application/json", "User-Agent": "Mozilla/5.0"},
                    timeout=15
                )
                resp.raise_for_status()
                items = resp.json().get("nft_items", [])
                for item in items:
                    name = item.get("metadata", {}).get("name", "")
                    m = _re.search(r"#(\d+)", name)
                    if m:
                        max_num = max(max_num, int(m.group(1)))
                raw_count += len(items)
                if len(items) < self.PAGE_SIZE:
                    break
                offset += self.PAGE_SIZE
                time.sleep(0.3)  # не превышаем rate limit
            # Если нашли серийные номера — возвращаем максимальный (= total supply)
            # Иначе — простой подсчёт
            return max_num if max_num > 0 else (raw_count if raw_count > 0 else None)
        except Exception as e:
            print(f"❌ TonAPI count_items {address[:20]}...: {e}")
            return None

    def add_address(self, gift_name: str, address: str):
        """Добавляет адрес коллекции и сразу обновляет кэш."""
        self.addresses[gift_name] = address
        self._save_json(self.ADDRESSES_FILE, self.addresses)
        count = self._count_items(address)
        if count is not None:
            self.supply_cache[address] = {"supply": count, "updated_at": time.time()}
            self._save_json(self.SUPPLY_CACHE_FILE, self.supply_cache)
            print(f"✅ TonAPI добавлен: {gift_name} = {count:,} PCS")

    def get_pcs(self, gift_name: str) -> Optional[int]:
        """Возвращает кэшированный supply или None если адрес неизвестен."""
        # Пробуем точное совпадение и case-insensitive
        for key in (gift_name, gift_name.lower()):
            addr = self.addresses.get(key)
            if addr:
                entry = self.supply_cache.get(addr)
                if entry:
                    return entry.get("supply")
        return None


class GiftDataProvider:
    """
    Провайдер данных для всех подарков.
    Берёт реальные цены из Contest API.
    PCS: fixed values.
    """

    def __init__(self):
        from gifts import GIFTS
        self.gifts = GIFTS
        self.total_stickers = config.TOTAL_STICKERS
        self.price_history = PriceHistory()
        self.converter = PriceConverter()
        self.api = ContestApiClient()
        self.tonapi = TonAPISupplyProvider()
        self.api.fetch()
        # Последние известные цены (fallback при ошибке API)
        self._last_prices: Dict[int, float] = {}

    def get_all_prices(self) -> Dict[int, Dict]:
        self.converter.refresh_rates()
        self.api.fetch()

        result = {}
        missing_price = []
        missing_pcs = []

        for gift_id in range(1, self.total_stickers + 1):
            gift_name = self.gifts[gift_id]["name"] if gift_id in self.gifts else f"Gift {gift_id}"
            api_name = NAME_OVERRIDES.get(gift_name, gift_name)

            # --- Цена из Contest API ---
            price_ton = self.api.get_price_ton(gift_name)
            if price_ton is None:
                price_ton = self._last_prices.get(gift_id, 0.0)
                missing_price.append(gift_name)
            else:
                price_ton = round(price_ton, 4)
                self._last_prices[gift_id] = price_ton

            pcs = FIXED_PCS_BY_GIFT_ID.get(gift_id)
            if pcs is None:
                pcs = 0
                missing_pcs.append(gift_name)

            price_usd = self.converter.ton_to_usd(price_ton)
            price_stars = self.converter.ton_to_stars(price_ton)
            growth = self.price_history.get_growth(gift_id, price_ton)

            result[gift_id] = {
                "price_ton": price_ton,
                "price_usd": price_usd,
                "price_stars": price_stars,
                "pcs": pcs,
                "growth": growth
            }

        if missing_price:
            print(f"⚠️ Цена не найдена ({len(missing_price)}): {', '.join(missing_price[:10])}"
                  + (" и др." if len(missing_price) > 10 else ""))
        if missing_pcs:
            print(f"⚠️ PCS не найден ({len(missing_pcs)}): {', '.join(missing_pcs[:10])}"
                  + (" и др." if len(missing_pcs) > 10 else ""))

        matched_price = self.total_stickers - len(missing_price)
        matched_pcs = self.total_stickers - len(missing_pcs)
        print(f"✅ Цены: {matched_price}/{self.total_stickers} из Contest API")
        print(f"✅ PCS: {matched_pcs}/{self.total_stickers} фиксированные")
        return result
