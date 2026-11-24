import importlib
from types import SimpleNamespace


# Dil modülü lower() ve CHECKS sağlar. Modülü olmayan dil yalnızca genel denetimleri alır.
def get(lang: str):
    try:
        return importlib.import_module(f"{__name__}.{lang}")
    except ModuleNotFoundError as e:
        if e.name != f"{__name__}.{lang}":
            raise
        return SimpleNamespace(lower=str.lower, CHECKS=[])
