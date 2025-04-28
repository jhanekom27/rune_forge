from typing import Callable, Dict


EXPLICIT_REGISTRY: Dict[str, Callable] = {}


def inscribe(key: str):
    def wrapper(cls):
        EXPLICIT_REGISTRY[key] = cls
        return cls

    return wrapper
