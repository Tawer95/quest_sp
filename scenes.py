from engine import Scene, Option


def make_scenes() -> dict[str, Scene]:
    s: dict[str, Scene] = {}

    # ───────── Камера ─────────
    s["cell"] = Scene(
        id="cell",
        title="НАРЫ",
        art_caption="Секция Б-7, тюремный блок",
        text=lambda st: cell_text(st),
        options=[
            Option(
                "Осмотреть нары",
                to="bunk",
                availability="hide",
                requires=lambda st: not st.flags.get("bunkLootTaken", False),
            ),
            Option("Поговорить с сокамерником", to="cellmate"),
            Option("Проверить дверь", to="door"),
            Option("Осмотреть вентиляцию", to="vent"),
            Option("Осмотреть раковину", to="sink"),
            Option("Электрощиток у двери", to="panel_cell"),
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
                effect=lambda st: learn_window_tip(st),
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
            Option(
                "Сообщить о протечке в камере",
                visible=lambda st: st.flags.get("maintenanceCalled", False),
                to="maintenance_visit",
                effect=lambda st: report_leak_again(st),
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
        text=lambda st: closet_text(st),
        options=[
            Option(
                "Взять отвёртку",
                visible=lambda st: "отвёртка" not in st.items,
                availability="disable",
                requires=lambda st: len(current_tools(st)) < 2,
                reason=lambda: "Нельзя нести более двух предметов.",
                to=lambda st: take_tool(st),
            ),
            Option(
                "Взять шестигранник",
                visible=lambda st: "шестигранник" not in st.items,
                availability="disable",
                requires=lambda st: len(current_tools(st)) < 2,
                reason=lambda: "Нельзя нести более двух предметов.",
                to=lambda st: take_hex(st),
            ),
            Option(
                "Взять тонкую проволоку",
                visible=lambda st: "проволока" not in st.items,
                availability="disable",
                requires=lambda st: len(current_tools(st)) < 2,
                reason=lambda: "Нельзя нести более двух предметов.",
                to=lambda st: take_wire(st),
            ),
            Option(
                "Взять таймер",
                visible=lambda st: "таймер" not in st.items,
                availability="disable",
                requires=lambda st: len(current_tools(st)) < 2,
                reason=lambda: "Нельзя нести более двух предметов.",
                to=lambda st: take_timer(st),
            ),
            Option(
                "Взять предохранитель",
                visible=lambda st: "предохранитель" not in st.items,
                availability="disable",
                requires=lambda st: len(current_tools(st)) < 2,
                reason=lambda: "Нельзя нести более двух предметов.",
                to=lambda st: take_fuse(st),
            ),
            Option(
                "Положить отвёртку на полку",
                visible=lambda st: "отвёртка" in current_tools(st),
                to=lambda st: drop_tool(st, "отвёртка"),
            ),
            Option(
                "Положить шестигранник на полку",
                visible=lambda st: "шестигранник" in current_tools(st),
                to=lambda st: drop_tool(st, "шестигранник"),
            ),
            Option(
                "Положить проволоку на полку",
                visible=lambda st: "проволока" in current_tools(st),
                to=lambda st: drop_tool(st, "проволока"),
            ),
            Option(
                "Положить таймер на полку",
                visible=lambda st: "таймер" in current_tools(st),
                to=lambda st: drop_tool(st, "таймер"),
            ),
            Option(
                "Положить предохранитель на полку",
                visible=lambda st: "предохранитель" in current_tools(st),
                to=lambda st: drop_tool(st, "предохранитель"),
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
                requires=lambda st: st.flags.get("learnedAboutHiddenDoor", False),
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
                "Снять крышку панели",
                availability="disable",
                requires=lambda st: "отвёртка" in st.items,
                reason=lambda: "Нужна отвёртка.",
                to="hidden_door_open_panel",
            ),
            Option(
                "Открыть ключ-картой",
                availability="disable",
                requires=lambda st: st.flags.get("hasDoorKey", False) and st.flags.get("doorUnlocked", False),
                reason=lambda: "Нужно подготовить панель.",
                to="corridor",
            ),
            Option("Вернуться", to="cell"),
        ],
    )

    s["hidden_door_open_panel"] = Scene(
        id="hidden_door_open_panel",
        title="СКРЫТАЯ ДВЕРЬ",
        art_caption="Скрытая дверь",
        text="Под крышкой старый блок: пара проводов от сканера и питание подсветки.",
        options=[
            Option(
                "Перемкнуть контакты сканера",
                availability="disable",
                requires=lambda st: "проволока" in st.items,
                reason=lambda: "Нужна тонкая проволока.",
                to=lambda st: unlock_hidden_door(st),
                once=True,
            ),
            Option(
                "Открыть ключ-картой",
                availability="disable",
                requires=lambda st: st.flags.get("hasDoorKey", False) and st.flags.get("doorUnlocked", False),
                reason=lambda: "Нужно подготовить панель.",
                to="corridor",
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
                visible=lambda st: not st.flags.get("ventOpened", False),
                # активна только если есть отвёртка
                availability="disable",
                requires=lambda st: "отвёртка" in st.items,
                reason=lambda: "Нужна отвёртка.",
                to="vent_inside",
                effect=lambda st: mark_found_vent(st),  # помечаем ventOpened внутри эффекта
                once=True,  # после клика исчезнет в этой сцене тоже
            ),
            Option(
                "Вернуться",
                to="cell",
            ),
        ],
    )

    s["vent_inside"] = Scene(
        id="vent_inside",
        title="ВОЗДУХОВОД",
        art_caption="Вентиляция",
        text="Тесно и пыльно. Впереди слышно гудение вентилятора и щёлканье камеры.",
        options=[
            Option("К узлу вентиляции", to="vent_hub"),
            Option("Вернуться", to="cell"),
        ],
    )

    s["vent_hub"] = Scene(
        id="vent_hub",
        title="УЗЕЛ ВЕНТИЛЯЦИИ",
        art_caption="Техотсек",
        text=(
            "Снизу решётка в коридор. Слева камера наблюдения. Без отключения питания пройти рискованно."
        ),
        options=[
            Option(
                "Спрыгнуть в коридор",
                availability="disable",
                requires=lambda st: st.flags.get("powerCut", False),
                reason=lambda: "Камера активна. Отключите питание.",
                to="corridor",
            ),
            Option(
                "Подстроиться под окно и спрыгнуть",
                availability="disable",
                requires=lambda st: st.flags.get("knowWindow", False) and ("таймер" in st.items),
                reason=lambda: "Нужно знать цикл и иметь таймер.",
                to="corridor",
            ),
            Option("Назад", to="vent_inside"),
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
                visible=lambda st: not st.flags.get("tokenPicked", False),  # видно, пока не взяли
                to=lambda st: take_token(st),
                once=True,
            ),
            Option("Двигаться к шлюзу", to="exit"),
            Option(
                "Вернуться к развилке вентиляции",
                availability="hide",
                requires=lambda st: st.flags.get("foundVent", False),
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
                requires=lambda st: not st.flags.get("tokenPicked", False),
                to="corridor",
            ),
            Option("Двигаться к шлюзу", to="exit"),
            Option(
                "Назад к развилке вентиляции",
                availability="hide",
                requires=lambda st: st.flags.get("foundVent", False),
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

    # ───────── Раковина / Саботаж ─────────
    s["sink"] = Scene(
        id="sink",
        title="РАКОВИНА",
        art_caption="Санузел камеры",
        text=lambda st: sink_text(st),
        options=[
            Option(
                "Заткнуть слив и устроить протечку",
                visible=lambda st: not st.flags.get("maintenanceCalled", False),
                to=lambda st: clog_sink(st),
                once=True,
            ),
            Option(
                "Подождать, пока наберётся воды",
                visible=lambda st: st.flags.get("maintenanceCalled", False) and not st.flags.get("floodReady", False),
                to=lambda st: wait_flood(st),
                once=True,
            ),
            Option(
                "Вздремнуть, ожидая техника",
                visible=lambda st: st.flags.get("maintenanceCalled", False) and not st.flags.get("techCame", False),
                to=lambda st: nap_for_tech(st),
                once=True,
            ),
            Option(
                "Умыться",
                visible=lambda st: st.flags.get("sinkFixed", False),
                to=lambda st: wash_face(st),
                once=True,
            ),
            Option("Вернуться", to="cell"),
        ],
    )

    # ───────── Визит техника ─────────
    s["maintenance_visit"] = Scene(
        id="maintenance_visit",
        title="ТЕХНИК",
        art_caption="Техслужба",
        text=lambda st: maintenance_text(st),
        options=[
            Option(
                "Пока он ушёл — проскользнуть в кладовую",
                availability="disable",
                requires=lambda st: not st.flags.get("techAlerted", False),
                reason=lambda: "Техник теперь начеку.",
                to=lambda st: enter_closet(st),
                once=True,
            ),
            Option(
                "Вернуться в кладовую позже",
                to=lambda st: reset_closet_visit(st),
                once=True,
            ),
            Option("Вернуться", to="cell"),
        ],
    )

    # ───────── Электрощиток у двери ─────────
    s["panel_cell"] = Scene(
        id="panel_cell",
        title="ЩИТОК",
        art_caption="Электрика",
        text="Под пластиком винты. Похоже, тут питание подсистем блока.",
        options=[
            Option(
                "Открутить крышку",
                availability="disable",
                requires=lambda st: ("отвёртка" in st.items and "шестигранник" in st.items) and not st.flags.get("panelOpen", False),
                reason=lambda: "Нужны отвёртка и шестигранник.",
                to=lambda st: open_panel(st),
                once=True,
            ),
            Option(
                "Перерезать питание камеры",
                availability="disable",
                requires=lambda st: st.flags.get("panelOpen", False) and ("предохранитель" in st.items) and not st.flags.get("powerCut", False),
                reason=lambda: "Нужен предохранитель и открыт щиток.",
                to=lambda st: cut_power(st),
                once=True,
            ),
            Option("Вернуться", to="cell"),
        ],
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
    return "closet"


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


def take_hex(st):
    st.items.add("шестигранник")
    return "closet"


def take_wire(st):
    st.items.add("проволока")
    return "closet"


def take_timer(st):
    st.items.add("таймер")
    return "closet"


def take_fuse(st):
    st.items.add("предохранитель")
    return "closet"


def learn_window_tip(st):
    spend(st, 50)
    add_note(st, "Окно пустого коридора: 30 сек каждые 7 минут")
    st.flags["knowWindow"] = True
    return "guard_path_tip"


def report_leak_again(st):
    # Если раковина уже была отремонтирована, техник теперь настороже
    if st.flags.get("sinkFixed", False):
        st.flags["techAlerted"] = True
    return "maintenance_visit"


def closet_text(st):
    carrying = sorted([x for x in st.items if x in {"отвёртка", "шестигранник", "проволока", "таймер", "предохранитель"}])
    carry_info = f"У вас при себе: {', '.join(carrying)}." if carrying else "У вас при себе ничего из инструментов."
    return (
        "Стеллажи с инструментами: отвёртки, шестигранники, проволока, таймер, коробка предохранителей. " + carry_info
    )


# ===== дополнительные эффекты для расширённых маршрутов =====
def clog_sink(st):
    st.flags["maintenanceCalled"] = True
    add_note(st, "Вызов техслужбы: протечка в камере")
    return "sink"


def open_panel(st):
    st.flags["panelOpen"] = True
    return "panel_cell"


def cut_power(st):
    st.flags["powerCut"] = True
    add_note(st, "Питание камеры отключено")
    return "panel_cell"


def unlock_hidden_door(st):
    st.flags["doorUnlocked"] = True
    add_note(st, "Замок скрытой двери подготовлен")
    return "hidden_door_open_panel"


# ===== динамические тексты и дополнительные эффекты =====
def cell_text(st):
    base = "В углу сопит сокамерник."
    sink_part = " Под раковиной лужица." if not st.flags.get("sinkFixed", False) else " Раковина сухая."
    if st.flags.get("bunkLootTaken", False) or st.items:
        prefix = "После осмотра вы всё ещё в той же камере. "
    else:
        prefix = "Вы просыпаетесь на верхней шконке тюремной камеры. Потолок потрескался, из вентиляции тянет холодом. "
    return prefix + base + sink_part


def sink_text(st):
    if st.flags.get("sinkFixed", False):
        return "Раковина идеально работает. Можно умыться и прийти в себя."
    if st.flags.get("maintenanceCalled", False) and not st.flags.get("floodReady", False):
        return "Слив заткнут, вода медленно поднимается. Похоже, скоро придётся вызывать техслужбу."
    if st.flags.get("floodReady", False) and not st.flags.get("techCame", False):
        return "Пол мокрый, вода переливается. Техник должен прийти с минуты на минуту."
    return "Сифон дребезжит. Если забить тряпкой, вода пойдёт через край."


def wait_flood(st):
    st.flags["floodReady"] = True
    return "sink"


def nap_for_tech(st):
    st.flags["techCame"] = True
    # Техник чинит раковину, но, если игрок уходил через неё раньше, он заносит пометку и будет начеку
    st.flags["sinkFixed"] = True
    add_note(st, "Техник приходил и всё осушил. Теперь раковина исправна.")
    return "maintenance_visit"


def maintenance_text(st):
    if st.flags.get("techAlerted", False):
        return "Техник косится на вас: 'С новой протечкой я уже не поведусь'. Пост открыт, но под присмотром."
    if st.flags.get("sinkFixed", False):
        return "Техник только что был здесь, чертыхаясь ушёл. Дверь поста приоткрыта, но он вернётся."
    return "Техник раздражённо бубнит и уходит за инструментом. Дверь поста приоткрыта."


def wash_face(st):
    add_note(st, "Умылись — стало бодрее.")
    return "sink"


def reset_closet_visit(st):
    return "cell"


def current_tools(st):
    toolset = {"отвёртка", "шестигранник", "проволока", "таймер", "предохранитель"}
    return [x for x in st.items if x in toolset]


def drop_tool(st, name: str):
    st.items.discard(name)
    return "closet"


def enter_closet(st):
    return "closet"
