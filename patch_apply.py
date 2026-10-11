#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Универсальный загрузчик патчей для index.py.

Использование:
    python3 patch_apply.py <имя_патча>
"""
import os
import sys
import shutil
import datetime
import urllib.request
import importlib.util

GITHUB_RAW = "https://raw.githubusercontent.com/irinakopytkova24-byte/ege-platform/main/patches/"
TARGET = "index.py"

def _download(name):
    url = GITHUB_RAW + name + ".py"
    print("[patch] Скачиваю: " + url)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "patch-apply/1.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.read().decode("utf-8")
    except Exception as e:
        print("[patch] Ошибка скачивания: " + str(e))
        sys.exit(1)

def _load_module(code, name):
    spec = importlib.util.spec_from_loader(name, loader=None)
    mod = importlib.util.module_from_spec(spec)
    exec(compile(code, name + ".py", "exec"), mod.__dict__)
    return mod

def main():
    if len(sys.argv) < 2:
        print("Использование: python3 patch_apply.py <имя_патча>")
        sys.exit(1)

    patch_name = sys.argv[1]
    if not os.path.exists(TARGET):
        print("[patch] Не найден " + TARGET)
        sys.exit(1)

    code = _download(patch_name)
    mod = _load_module(code, patch_name)

    print("[patch] " + getattr(mod, "PATCH_NAME", patch_name))
    print("[patch] " + getattr(mod, "PATCH_DESCRIPTION", ""))

    with open(TARGET, "r", encoding="utf-8") as f:
        original = f.read()

    if hasattr(mod, "is_applied") and mod.is_applied(original):
        print("[patch] Патч уже применён.")
        sys.exit(0)

    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = TARGET + ".bak_" + ts
    shutil.copy(TARGET, backup)
    print("[patch] Backup: " + backup)

    try:
        new_src = mod.apply(original)
    except Exception as e:
        print("[patch] ОШИБКА: " + str(e))
        sys.exit(2)

    if new_src is None or new_src == original:
        print("[patch] Патч не внёс изменений.")
        sys.exit(3)

    with open(TARGET, "w", encoding="utf-8") as f:
        f.write(new_src)

    print("[patch] OK.")
    print("Дальше: sudo systemctl restart ege")

if __name__ == "__main__":
    main()