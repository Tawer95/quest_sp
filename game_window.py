from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QGridLayout, QLabel, QVBoxLayout, QHBoxLayout,
    QPushButton, QFrame, QSizePolicy
)
from engine import Engine
from scenes import make_scenes


class GameWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Побег из тюрьмы — текстовый квест (PySide6)")
        self.setMinimumSize(1100, 680)

        # флаг: не анимируем самый первый рендер
        self._first_render = True

        # Движок
        self.engine = Engine(make_scenes())
        self.engine.on_state_changed = self.render_all

        # ---------- Разметка ----------
        root = QWidget(objectName="Root")
        self.setCentralWidget(root)
        grid = QGridLayout(root)
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(12)
        grid.setContentsMargins(16, 16, 16, 16)

        # Header
        header = QFrame(objectName="Panel")
        hbox = QHBoxLayout(header)
        hbox.setContentsMargins(10, 8, 10, 8)
        self.title_label = QLabel("Побег из тюрьмы · v0.2 (Python)")
        self.title_label.setObjectName("Title")
        self.credit_label = QLabel()
        self.credit_label.setObjectName("Money")
        hbox.addWidget(self.title_label, 1)
        hbox.addWidget(QLabel("Кредиты:"))
        hbox.addWidget(self.credit_label)

        # Story (left top)
        self.story_panel = QFrame(objectName="Panel")
        story_l = QVBoxLayout(self.story_panel)
        story_l.setContentsMargins(12, 12, 12, 12)
        self.story_text = QLabel(wordWrap=True)
        self.story_text.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        story_l.addWidget(self.story_text, 1)

        # Art (right top)
        self.art_panel = QFrame(objectName="Panel")
        art_l = QVBoxLayout(self.art_panel)
        art_l.setContentsMargins(12, 12, 12, 12)

        self.art_box = QLabel()
        self.art_box.setObjectName("ArtBox")
        # стабильные размеры, чтобы не «прыгало» вообще
        self.art_box.setMinimumHeight(260)
        self.art_box.setFixedHeight(260)
        self.art_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.art_caption = QLabel(objectName="Muted")

        # подпись — СНИЗУ (как раньше)
        art_l.addWidget(self.art_box)
        art_l.addWidget(self.art_caption)

        # Choices (left bottom)
        self.choices_panel = QFrame(objectName="Panel")
        choices_l = QVBoxLayout(self.choices_panel)
        choices_l.setContentsMargins(12, 12, 12, 12)
        choices_l.setSpacing(6)
        self.choices_box = QVBoxLayout()
        self.choices_box.setSpacing(6)
        choices_l.addLayout(self.choices_box)

        # Inventory (right bottom) — текстом
        self.inv_panel = QFrame(objectName="Panel")
        inv_l = QVBoxLayout(self.inv_panel)
        inv_l.setContentsMargins(12, 12, 12, 12)
        inv_l.setSpacing(8)
        inv_l.addWidget(QLabel("<b>Инвентарь</b>"))
        self.inv_text = QLabel()
        self.inv_text.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.inv_text.setWordWrap(True)
        inv_l.addWidget(self.inv_text, 1)

        # Footer
        self.footer = QFrame(objectName="Panel")
        foot_l = QHBoxLayout(self.footer)
        foot_l.setContentsMargins(12, 8, 12, 8)
        self.hint = QLabel(
            "Подсказка: недоступные варианты будут либо скрываться, либо "
            "подсвечиваться как неактивные с пояснением."
        )
        self.hint.setObjectName("Muted")
        foot_l.addWidget(self.hint)

        # Сетка как в вебе
        grid.addWidget(header, 0, 0, 1, 2)
        grid.addWidget(self.story_panel, 1, 0, 1, 1)
        grid.addWidget(self.art_panel,   1, 1, 1, 1)
        grid.addWidget(self.choices_panel, 2, 0, 1, 1)
        grid.addWidget(self.inv_panel,     2, 1, 1, 1)
        grid.addWidget(self.footer,     3, 0, 1, 2)

        grid.setRowStretch(1, 4)
        grid.setRowStretch(2, 2)
        grid.setColumnStretch(0, 7)
        grid.setColumnStretch(1, 4)

        # Стиль плейсхолдера арта
        self.art_box.setStyleSheet(
            "QLabel#ArtBox {background: qlineargradient(x1:0,y1:0,x2:1,y2:1, "
            "stop:0 #0f2a36, stop:1 #173a4b);"
            "border:1px solid #1a5266; border-radius:10px;}"
        )

        self.render_all()

    # ---------- Рендер ----------
    def render_all(self):
        scene = self.engine.get_scene()
        self.title_label.setText(scene.title)
        self.credit_label.setText(str(self.engine.state.credits))

        # Текст сцены; поддержка динамического текста (callable)
        try:
            text = scene.text(self.engine.state) if callable(scene.text) else scene.text
        except TypeError:
            text = scene.text()
        # Анимацию запускаем только со второго вызова
        self.story_text.setText(text)
        if not self._first_render:
            anim = QPropertyAnimation(self.story_panel, b"maximumHeight", self)
            self.story_panel.setMaximumHeight(10_000)
            anim.setDuration(130)
            anim.setStartValue(self.story_panel.height() - 6)
            anim.setEndValue(self.story_panel.height())
            anim.setEasingCurve(QEasingCurve.OutCubic)
            anim.start(QPropertyAnimation.DeleteWhenStopped)
        else:
            self._first_render = False

        # Подпись к визуалу (снизу)
        self.art_caption.setText(scene.art_caption)

        # Кнопки-действия (учитываем hide/disable)
        while self.choices_box.count():
            item = self.choices_box.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        for opt in list(scene.options):
            # сначала проверяем условие видимости (если задано)
            try:
                is_visible = True if not getattr(opt, "visible", None) else opt.visible(self.engine.state)
            except TypeError:
                # поддержка visible без параметров
                is_visible = opt.visible()
            if not is_visible:
                continue

            allowed = True if not opt.requires else opt.requires(self.engine.state)
            if not allowed and opt.availability == "hide":
                continue

            btn = QPushButton(opt.text)
            btn.setObjectName("Choice")
            btn.setCursor(Qt.PointingHandCursor)

            if not allowed and opt.availability == "disable":
                btn.setDisabled(True)
                if opt.reason:
                    try:
                        tip = opt.reason(self.engine.state)
                    except TypeError:
                        tip = opt.reason()
                    btn.setToolTip(tip)
            else:
                btn.clicked.connect(lambda _, o=opt: self.on_choice(o))

            self.choices_box.addWidget(btn)

        # Инвентарь — текстом
        items = sorted(self.engine.state.items)
        notes = list(self.engine.state.notes)
        # Добавляем строку с лимитом инструментов
        toolset = {"отвёртка", "шестигранник", "проволока", "таймер", "предохранитель"}
        tools_carry = sorted([x for x in items if x in toolset])
        tools_line = f"Инструменты при себе: {len(tools_carry)}/2" if tools_carry or True else ""
        if not items and not notes:
            self.inv_text.setText("пусто\n" + tools_line)
        else:
            lines = []
            if items:
                lines.append("Предметы:")
                for it in items:
                    lines.append(f" • {it}")
                lines.append("")
                lines.append(tools_line)
            if notes:
                if items:
                    lines.append("")
                lines.append("Заметки:")
                for n in notes:
                    lines.append(f" • {n}")
            self.inv_text.setText("\n".join(lines))

    # ---------- Обработка клика ----------
    def on_choice(self, opt):
        self.engine.choose(opt)
