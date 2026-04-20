"""
Watcher: следит за config.py и renderer.py по хэшу содержимого.
При любом изменении автоматически генерирует preview.png.
"""

import hashlib
import os
import sys
import time
import subprocess
from datetime import datetime


WATCH_FILES = ["config.py", "renderer.py", "gifts.py"]
GENERATE_SCRIPT = "preview_gen.py"


def file_hash(path: str) -> str:
    try:
        with open(path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()
    except FileNotFoundError:
        return ""


def run_preview():
    result = subprocess.run(
        [sys.executable, "-B", GENERATE_SCRIPT],
        capture_output=True, text=True
    )
    now = datetime.now().strftime("%H:%M:%S")
    if result.returncode == 0:
        size = os.path.getsize("preview.png") // 1024 if os.path.exists("preview.png") else 0
        print(f"[{now}] ✅ preview.png обновлён ({size} KB)")
    else:
        print(f"[{now}] ❌ Ошибка:")
        out = (result.stderr or result.stdout or "").strip()
        print(out[-800:] if len(out) > 800 else out)


def main():
    print("👁  Watcher запущен. Слежу за:", ", ".join(WATCH_FILES))
    print(f"    Результат → preview.png")
    print("    Сохрани config.py — preview.png обновится автоматически.\n")

    run_preview()

    hashes = {f: file_hash(f) for f in WATCH_FILES}

    while True:
        time.sleep(1.5)
        changed_files = []
        for f in WATCH_FILES:
            cur = file_hash(f)
            if cur and cur != hashes[f]:
                hashes[f] = cur
                changed_files.append(f)
        if changed_files:
            print(f"  📝 Изменён(ы): {', '.join(changed_files)}")
            run_preview()


if __name__ == "__main__":
    main()
