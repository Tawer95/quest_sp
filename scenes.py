from engine import Scene, Option


def make_scenes() -> dict[str, Scene]:
    s: dict[str, Scene] = {}

    # ───────── Камера ─────────
    s["cell"] = Scene(
        id="cell",
        title="НАРЫ",
        art_caption="Секция Б-7, тюремный блок",
        text=(
            "Вы просыпаетесь на верхней шконке тюремной камеры. Потолок потрескался, "
            "из вентиляции тянет холодом. У двери — глазок и старый замок. В углу сопит сокамерник."
        ),
        options=[
            Option(
                "Осмотреть нары",
                to="bunk",
                availability="hide",
                requires=lambda st: not st.flags["bunkLootTaken"],
            ),
            Option("Поговорить с сокамерником", to="cellmate"),
            Option("Проверить дверь", to="door"),
            Option("Осмотреть вентиляцию", to="vent"),
            Option("Позвать охранника", to="guard"),
        ],
    )

    # ───────── Нары ─────────
    s["bunk"] = Scene(
        id="bunk",
        title="НАРЫ",
        art_caption="Секция Б-7, тюремный блок",
        text=(
            "Вы находите под матрасом свёрток: ржавая ключ-карта и 12 кредитов. "
            "Карта выглядит древней, но, возможно, ещё сработает."
        ),
        options=[
            Option("Забрать находку", to=lambda st: after_take_key(st), once=True),
            Option("Вернуться", to="cell"),
        ],
    )

    # ───────── Сокамерник ─────────
    s["cellmate"] = Scene(
        id="cellmate",
        title="СОКАМЕРНИК",
        art_caption="Тюремный блок",
        text=(
            "Лысый мужик представляется Феней. Он шепчет: «Ходят слухи, что в этой секции есть "
            "скрытая дверь в технический коридор. Поищи за старым плакатом у дальнего угла. "
            "Но без карты ты её не откроешь…»"
        ),
        options=[
            Option("Спросить о скрытой двери", to=lambda st: learn_door_scene(st), once=True),
            Option(
                "Предложить 50 cr за подробности",
                availability="disable",
                requires=lambda st: st.credits >= 50,
                reason=lambda st: f"Нужно 50 cr (у вас {st.credits})",
                to="guard_path_tip",
                once=True,
                effect=lambda st: (spend(st, 50), add_note(st, "Охрана: окно пустого коридора 30 сек каждые 7 минут")),
            ),
            Option("Назад", to="cell"),
        ],
    )

    s["cellmate_hint"] = Scene(
        id="cellmate_hint",
        title="СОКАМЕРНИК",
        art_caption="Тюремный блок",
        text=("«Дверь ищи за старым плакатом в дальнем углу камеры. "
              "Без ключ-карты панель не откроется», — шепчет Феня."),
        options=[Option("Понятно", to="cell")],
    )

    s["guard_path_tip"] = Scene(
        id="guard_path_tip",
        title="СЕКРЕТЫ КАРАУЛКИ",
        art_caption="Тюремный блок",
        text=("Феня подробно описывает график смен: «Через семь минут коридор пустеет на тридцать секунд». "
              "Вы заносите пометку в заметки."),
        options=[Option("Вернуться в камеру", to="cell")],
    )

    # ───────── Охранник ─────────
    s["guard"] = Scene(
        id="guard",
        title="ОХРАННИК",
        art_caption="Контрольный пост охраны",
        text="Вы бьёте в дверь. В глазке появляется сонный охранник. «Что надо?»",
        options=[
            Option("Пожаловаться на проблему с вентиляцией", to="guard_vent"),
            Option(
                "Предложить 80 cr за прогулку в кладовую",
                availability="disable",
                requires=lambda st: st.credits >= 80,
                reason=lambda st: f"Нужно 80 cr (у вас {st.credits})",
                to="closet",
                effect=lambda st: spend(st, 80),
            ),
            Option("Уйти", to="cell"),
        ],
    )

    s["guard_vent"] = Scene(
        id="guard_vent",
        title="ДИАЛОГ",
        art_caption="Тюремный блок",
        text="«Опять жалобы? Ладно, позже посмотрим». Кажется, его это мало волнует.",
        options=[Option("Вернуться", to="cell")],
    )

    # ───────── Кладовая ─────────
    s["closet"] = Scene(
        id="closet",
        title="КЛАДОВАЯ",
        art_caption="Кладовая",
        text="На стеллажах — инструменты. Пока охранник отвлёкся, вы успеваете схватить небольшую отвёртку.",
        options=[
            Option(
                "Взять отвёртку",
                visible=lambda st: "отвёртка" not in st.items,  # видно, пока нет отвёртки
                to=lambda st: take_tool(st),
                once=True,
            ),
            Option("Назад в камеру", to="cell"),
        ],
    )

    # ───────── Дверь ─────────
    s["door"] = Scene(
        id="door",
        title="ДВЕРЬ",
        art_caption="Дверь камеры",
        text="Замок электрический, но старый. Рядом заметен след от переклеенного плаката…",
        options=[
            Option(
                "Найти скрытую дверь за плакатом",
                availability="hide",
                requires=lambda st: st.flags["learnedAboutHiddenDoor"],
                to="hidden_door",
            ),
            Option("Вернуться", to="cell"),
        ],
    )

    s["hidden_door"] = Scene(
        id="hidden_door",
        title="СКРЫТАЯ ДВЕРЬ",
        art_caption="Скрытая дверь",
        text="За плакатом действительно панель с карточным замком.",
        options=[
            Option(
                "Открыть ключ-картой",
                availability="disable",
                requires=lambda st: st.flags["hasDoorKey"],
                reason=lambda: "Нужна ключ-карта.",
                to="corridor",
                effect=lambda st: set_unlocked(st),
            ),
            Option("Вернуться", to="cell"),
        ],
    )

    # ───────── Вентиляция ─────────
    s["vent"] = Scene(
        id="vent",
        title="ВЕНТИЛЯЦИЯ",
        art_caption="Вентиляция",
        text="Решётка держится на двух винтах. Без инструмента её не снять.",
        options=[
            Option(
                "Открутить решётку отвёрткой",
                # видно, пока решётка НЕ снята
                visible=lambda st: not st.flags["ventOpened"],
                # активна только если есть отвёртка
                availability="disable",
                requires=lambda st: "отвёртка" in st.items,
                reason=lambda: "Нужна отвёртка.",
                to="vent_inside",
                effect=lambda st: mark_found_vent(st),  # помечаем ventOpened внутри эффекта
                once=True,  # после клика исчезнет в этой сцене тоже
            ),
            Option("Вернуться", to="cell"),
        ],
    )

    s["vent_inside"] = Scene(
        id="vent_inside",
        title="ВОЗДУХОВОД",
        art_caption="Вентиляция",
        text="Металл скрипит, впереди слышно эхо шагов. Есть развилка.",
        options=[
            Option("Ползти к коридору", to="corridor"),
            Option("Назад в камеру", to="cell"),
        ],
    )

    # ───────── Сервисный коридор ─────────
    s["corridor"] = Scene(
        id="corridor",
        title="СЕРВИСНЫЙ КОРИДОР",
        art_caption="Сервисный коридор",
        text="Узкий освещённый тоннель ведёт к шлюзу. На полу валяется жетон пропуска.",
        options=[
            Option(
                "Подобрать жетон",
                visible=lambda st: not st.flags["tokenPicked"],  # видно, пока не взяли
                to=lambda st: take_token(st),
                once=True,
            ),
            Option("Двигаться к шлюзу", to="exit"),
            Option(
                "Вернуться к развилке вентиляции",
                availability="hide",
                requires=lambda st: st.flags["foundVent"],
                to="vent_inside",
            ),
        ],
    )

    s["corridor2"] = Scene(
        id="corridor2",
        title="СЕРВИСНЫЙ КОРИДОР",
        art_caption="Сервисный коридор",
        text="Вы собираетесь к шлюзу.",
        options=[
            Option(
                "Вернуться и подобрать жетон",
                availability="hide",
                requires=lambda st: not st.flags["tokenPicked"],
                to="corridor",
            ),
            Option("Двигаться к шлюзу", to="exit"),
            Option(
                "Назад к развилке вентиляции",
                availability="hide",
                requires=lambda st: st.flags["foundVent"],
                to="vent_inside",
            ),
        ],
    )

    # ───────── Шлюз ─────────
    s["exit"] = Scene(
        id="exit",
        title="ШЛЮЗ",
        art_caption="Шлюз",
        text="На панели требуется жетон пропуска.",
        options=[
            Option(
                "Приложить жетон и сбежать",
                availability="disable",
                requires=lambda st: "жетон пропуска" in st.items,
                reason=lambda: "Нужен жетон пропуска.",
                to="freedom",
            ),
            Option("Вернуться в коридор", to="corridor2"),
        ],
    )

    # ───────── Финал ─────────
    s["freedom"] = Scene(
        id="freedom",
        title="СВОБОДА!",
        art_caption="Техлабиринты станции",
        text="Вы проскальзываете через шлюз и растворяетесь в техлабиринтах. Побег удался — но история только начинается.",
        options=[Option("Начать заново", to="__RESET__")],
    )

    return s


# ================= эффекты / утилиты =================

def after_take_key(st):
    st.items.add("ключ-карта")
    st.credits += 12
    st.flags["hasDoorKey"] = True
    st.flags["bunkLootTaken"] = True
    return "cell"


def learn_door_scene(st):
    st.flags["learnedAboutHiddenDoor"] = True
    st.flags["spokeWithCellmate"] = True
    add_note(st, "Скрытая дверь за старым плакатом в дальнем углу камеры.")
    return "cellmate_hint"


def spend(st, amount: int):
    st.credits -= amount


def take_tool(st):
    st.items.add("отвёртка")
    return "cell"


def set_unlocked(st):
    st.flags["doorUnlocked"] = True


def mark_found_vent(st):
    st.flags["foundVent"] = True
    st.flags["ventOpened"] = True    # ← помним, что решётка уже снята


def take_token(st):
    st.items.add("жетон пропуска")
    st.flags["tokenPicked"] = True
    return "corridor"


def add_note(st, text: str):
    st.notes.append(text)
