from dataclasses import dataclass, field
from typing import Callable, List, Dict, Optional, Any


@dataclass
class Option:
    text: str
    to: Any  # str | Callable[[GameState], str]
    availability: str = "hide"  # 'hide' | 'disable'  (как и раньше)
    requires: Optional[Callable] = None    # когда опция активна (True) / неактивна (False)
    reason: Optional[Callable] = None
    effect: Optional[Callable] = None
    once: bool = False
    # НОВОЕ: отдельное условие видимости (не влияет на enabled/disabled)
    visible: Optional[Callable] = None     # если задано и возвращает False — опция не рисуется


@dataclass
class Scene:
    id: str
    title: str
    text: str
    art_caption: str
    options: List[Option] = field(default_factory=list)


class GameState:
    def __init__(self):
        self.credits: int = 200
        self.items: set[str] = set()
        self.notes: list[str] = []
        self.flags: dict[str, bool] = {
            "spokeWithCellmate": False,
            "learnedAboutHiddenDoor": False,
            "hasDoorKey": False,
            "foundVent": False,
            "ventOpened": False,         # <- решётка однажды откручена
            "doorUnlocked": False,
            "bunkLootTaken": False,
            "tokenPicked": False,
        }
        self.scene: str = "cell"


class Engine:
    def __init__(self, scenes: Dict[str, Scene]):
        self.state = GameState()
        self.scenes = scenes
        self.on_state_changed = None  # callback из UI

    def get_scene(self) -> Scene:
        return self.scenes[self.state.scene]

    def choose(self, option: Option):
        # проверка доступности
        if option.requires and not option.requires(self.state):
            return

        # эффект
        if option.effect:
            option.effect(self.state)

        # вычисляем следующий экран
        next_scene = option.to(self.state) if callable(option.to) else option.to

        # одноразовые опции удаляем ТОЛЬКО если реально выбрана эта опция
        if option.once:
            try:
                self.get_scene().options.remove(option)
            except ValueError:
                pass

        # спец-режим «полный сброс»
        if next_scene == "__RESET__":
            self.state = GameState()
            next_scene = "cell"

        # переход
        self.state.scene = next_scene
        if self.on_state_changed:
            self.on_state_changed()
