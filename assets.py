import os
import requests

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

ASSETS = {
    "base.png": "https://i.postimg.cc/3WM6qpvk/Bez-nazvania90-20260410195148.png",
    "extra.png": "https://i.postimg.cc/hG7QPsqt/Bez-nazvania68-20260410164805.png",
    "ton_icon.png": "https://i.postimg.cc/66jd7L0F/Bez-nazvania83-20260410133905.png",
    "stars_icon.png": "https://i.postimg.cc/dQH87m6K/Bez-nazvania62-20260410134245.png",
    "growth_up.png": "https://i.postimg.cc/WhJd40LD/F017A308-F49F-413A-A31A-53802736AC45.png",
    "growth_down.png": "https://i.postimg.cc/qzCN72VR/1920B162-A5E0-4729-99FA-22F74A5E8F66.png",
}

FALLBACK_ASSETS = {
    "extra.png": [
        "https://i.postimg.cc/hG7QPsqt/Bez-nazvania68-20260410164805.png",
        "https://i.postimg.cc/hG7QPsqt/%D0%91%D0%B5%D0%B7_%D0%BD%D0%B0%D0%B7%D0%B2%D0%B0%D0%BD%D0%B8%D1%8F68_20260410164805.png",
    ],
    "ton_icon.png": [
        "https://i.postimg.cc/66jd7L0F/Bez-nazvania83-20260410133905.png",
        "https://i.postimg.cc/66jd7L0F/%D0%91%D0%B5%D0%B7_%D0%BD%D0%B0%D0%B7%D0%B2%D0%B0%D0%BD%D0%B8%D1%8F83_20260410133905.png",
    ],
    "stars_icon.png": [
        "https://i.postimg.cc/dQH87m6K/Bez-nazvania62-20260410134245.png",
        "https://i.postimg.cc/dQH87m6K/%D0%91%D0%B5%D0%B7_%D0%BD%D0%B0%D0%B7%D0%B2%D0%B0%D0%BD%D0%B8%D1%8F62_20260410134245.png",
    ],
}

FONTS = {
    "Inter-Bold": "https://github.com/google/fonts/raw/main/ofl/inter/Inter%5Bopsz,wght%5D.ttf",
    "Montserrat-Bold": "https://github.com/JulietaUla/Montserrat/raw/master/fonts/ttf/Montserrat-Bold.ttf",
    "Roboto-Bold": "https://github.com/googlefonts/roboto-2/raw/main/src/hinted/Roboto-Bold.ttf",
    "Oswald-Bold": "https://github.com/google/fonts/raw/main/ofl/oswald/Oswald%5Bwght%5D.ttf",
    "BebasNeue": "https://github.com/google/fonts/raw/main/ofl/bebasneue/BebasNeue-Regular.ttf",
    "Nunito-Bold": "https://github.com/google/fonts/raw/main/ofl/nunito/Nunito%5Bwght%5D.ttf",
}


def _try_download(url: str, path: str) -> bool:
    try:
        r = requests.get(url, timeout=20, headers=HEADERS)
        r.raise_for_status()
        if len(r.content) < 100:
            return False
        with open(path, "wb") as f:
            f.write(r.content)
        return True
    except Exception as e:
        print(f"  ⚠️ {url}: {e}")
        return False


def download_assets():
    missing = [name for name in ASSETS if not os.path.exists(name)]
    if missing:
        print(f"📥 Скачиваю {len(missing)} ассета(ов)...")
        for name in missing:
            urls = FALLBACK_ASSETS.get(name, [ASSETS[name]])
            ok = False
            for url in urls:
                print(f"  → {name} ...")
                if _try_download(url, name):
                    size = os.path.getsize(name)
                    print(f"  ✅ {name} ({size // 1024} KB)")
                    ok = True
                    break
            if not ok:
                print(f"  ❌ Не удалось скачать {name}. Положите файл вручную в корень проекта.")
    else:
        print("✅ Все ассеты на месте")

    os.makedirs("fonts", exist_ok=True)
    missing_fonts = [name for name in FONTS if not os.path.exists(f"fonts/{name}.ttf")]
    if missing_fonts:
        print(f"🔤 Скачиваю {len(missing_fonts)} шрифт(ов)...")
        for name in missing_fonts:
            path = f"fonts/{name}.ttf"
            print(f"  → {name} ...")
            if _try_download(FONTS[name], path):
                size = os.path.getsize(path)
                print(f"  ✅ {name} ({size // 1024} KB)")
            else:
                print(f"  ❌ Не удалось скачать шрифт {name}")
    else:
        print("✅ Все шрифты на месте")
