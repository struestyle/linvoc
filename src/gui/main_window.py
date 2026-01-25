"""Fenêtre principale avec indicateur microphone."""

import math
import signal
import sys
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QApplication
)
from PySide6.QtCore import (
    Qt, QTimer, Signal, QSize
)
from PySide6.QtGui import QFont, QPainter, QColor, QPen, QBrush, QPixmap
from PySide6.QtSvg import QSvgRenderer

from .styles import Styles, ICONS
from ..core.dictation import DictationManager, DictationState
from ..core.text_injector import TextInjector


class MicrophoneWidget(QWidget):
    """
    Widget flottant modernisé avec indicateur microphone.
    """

    # Signaux
    recording_started = Signal()
    recording_stopped = Signal(str)
    error_occurred = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._setup_window()
        self._setup_ui()
        self._setup_dictation()
        self._setup_animations()

        self._dark_mode = True
        self._drag_pos = None
        self._is_dragging = False
        self._update_style()

    def _setup_window(self):
        self.setObjectName("MicrophoneWidget")
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowDoesNotAcceptFocus  # IMPORTANT: Ne jamais prendre le focus
        )
        self.setFixedSize(100, 100)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._position_window()

    def _position_window(self):
        screen = QApplication.primaryScreen()
        if screen:
            geometry = screen.availableGeometry()
            x = geometry.right() - self.width() - 40
            y = geometry.bottom() - self.height() - 40
            self.move(x, y)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 25, 10, 10)
        layout.setSpacing(2)

        # Bouton fermer en haut à droite
        self._close_btn = QLabel(self)
        self._close_btn.setFixedSize(20, 20)
        self._close_btn.move(self.width() - 28, 8)
        self._close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._close_btn.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._close_btn.setObjectName("CloseButton")
        self._close_btn.installEventFilter(self)

        # Icône centrale (SVG)
        self._icon_label = QLabel()
        self._icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._icon_label.setFixedSize(40, 40)

        self._status_label = QLabel("DICTÉE")
        self._status_label.setObjectName("StatusLabel")
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._status_label.setContentsMargins(0, 0, 0, 0)

        font = QFont("Sans Serif", 9, QFont.Weight.Bold)
        self._status_label.setFont(font)

        layout.addWidget(
            self._icon_label,
            alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom
        )
        layout.addWidget(
            self._status_label,
            alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop
        )

    def _render_svg_to_label(self, label: QLabel, icon_name: str, color: QColor, size: int):
        """Affiche un SVG dans un label spécifique avec une couleur et taille données."""
        svg_xml = ICONS[icon_name].replace('currentColor', color.name())
        renderer = QSvgRenderer(svg_xml.encode('utf-8'))

        pixmap_size = QSize(size, size)
        target = QPixmap(pixmap_size)
        target.fill(Qt.GlobalColor.transparent)

        painter = QPainter(target)
        renderer.render(painter)
        painter.end()

        label.setPixmap(target)

    def eventFilter(self, obj, event):
        """Détecte le clic sur le bouton de fermeture."""
        if obj == self._close_btn and event.type() == event.Type.MouseButtonPress:
            self.close()
            return True
        return super().eventFilter(obj, event)

    def _setup_dictation(self):
        self._dictation = DictationManager(
            language="fr",
            on_state_change=self._on_dictation_state_change,
        )
        try:
            self._injector = TextInjector.get_instance()
        except RuntimeError:
            self._injector = None

    def _setup_animations(self):
        self._pulse_timer = QTimer(self)
        self._pulse_timer.timeout.connect(self._animate_pulse)
        self._pulse_phase = 0.0

    def _update_style(self):
        state = self._dictation.state
        colors = Styles.get_theme_colors(self._dark_mode)

        # Icône de fermeture (toujours visible)
        self._render_svg_to_label(
            self._close_btn, "close", QColor(colors['text_muted']), 14
        )

        if state == DictationState.RECORDING:
            style = Styles.get_recording_style(self._dark_mode)
            self._status_label.setText("ÉCOUTE")
            self._render_svg_to_label(
                self._icon_label, "microphone_on", QColor(colors['recording']), 40
            )
        elif state == DictationState.PROCESSING:
            style = Styles.get_processing_style(self._dark_mode)
            self._status_label.setText("VOSK...")
            self._render_svg_to_label(
                self._icon_label, "spinner", QColor(colors['primary']), 40
            )
        elif state == DictationState.ERROR:
            style = Styles.get_error_style(self._dark_mode)
            self._status_label.setText("ERREUR")
            self._render_svg_to_label(
                self._icon_label, "warning", QColor(colors['warning']), 40
            )
        else:
            style = Styles.get_widget_style(self._dark_mode)
            self._status_label.setText("DICTÉE")
            self._render_svg_to_label(
                self._icon_label, "microphone", QColor(colors['text']), 40
            )

        self.setStyleSheet(style)
        self.update()

    def _on_dictation_state_change(self, state: DictationState):
        self._update_style()
        if state == DictationState.RECORDING:
            self._pulse_timer.start(50)
            self.recording_started.emit()
        else:
            self._pulse_timer.stop()

    def _animate_pulse(self):
        self.update()

    def paintEvent(self, _event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        colors = Styles.get_theme_colors(self._dark_mode)
        state = self._dictation.state

        # Fond
        painter.setBrush(QBrush(QColor(colors['surface'])))
        pen_color = colors['border']
        pen_width = 2

        if state == DictationState.RECORDING:
            self._pulse_phase += 0.1
            pulse = abs(math.sin(self._pulse_phase)) * 2
            pen_color = colors['recording']
            pen_width = 2 + pulse
        elif state == DictationState.PROCESSING:
            pen_color = colors['primary']

        painter.setPen(QPen(QColor(pen_color), pen_width))
        painter.drawRoundedRect(5, 5, self.width()-10, self.height()-10, 20, 20)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint()
            # On ne lance pas la dictée immédiatement si on veut permettre le drag
            # On vérifiera au relâchement si c'était un clic ou un drag
            self._is_dragging = False
        elif event.button() == Qt.MouseButton.RightButton:
            self.close()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton:
            new_pos = event.globalPosition().toPoint()
            delta = new_pos - self._drag_pos
            if delta.manhattanLength() > 5: # Seuil pour éviter les micro-mouvements
                self.move(self.pos() + delta)
                self._drag_pos = new_pos
                self._is_dragging = True

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if not getattr(self, '_is_dragging', False):
                # C'était un simple clic, on bascule la dictée
                self.toggle_recording()
            self._is_dragging = False

    def toggle_recording(self):
        if self._dictation.state == DictationState.RECORDING:
            self._dictation.stop()
            self.recording_stopped.emit("")
        else:
            if not self._dictation.start():
                self.error_occurred.emit("Erreur Vosk")

    def closeEvent(self, event):
        """Arrête proprement la dictée et les threads à la fermeture."""
        self._dictation.stop()
        event.accept()
        QApplication.quit()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        elif event.key() == Qt.Key.Key_Space:
            self.toggle_recording()


class LinvocApplication:
    def __init__(self, start_immediately=False):
        self._app = QApplication.instance() or QApplication(sys.argv)
        self._app.setQuitOnLastWindowClosed(True)
        self._widget = MicrophoneWidget()

        # Créer le fichier lock
        from ..core.single_instance import create_lock, remove_lock
        create_lock()
        self._remove_lock = remove_lock

        # Gestion propre de Ctrl+C et signaux
        signal.signal(signal.SIGINT, self.quit)
        signal.signal(signal.SIGTERM, self.quit)
        signal.signal(signal.SIGUSR1, self._on_toggle_signal)

        # Timer pour permettre à Python de recevoir les signaux (Qt loop bloque sinon)
        self._timer = QTimer()
        self._timer.timeout.connect(lambda: None)
        self._timer.start(500)

        if start_immediately:
            # Léger délai pour laisser la fenêtre s'afficher
            QTimer.singleShot(500, self._widget.toggle_recording)

    def _on_toggle_signal(self, _signum, _frame):
        """Handler pour SIGUSR1 - toggle la dictée."""
        self._widget.toggle_recording()

    def quit(self, *_args):
        print("\nArrêt de l'application...")
        self._remove_lock()
        if hasattr(self, '_widget'):
            self._widget.close()
        self._app.quit()
        sys.exit(0)

    def run(self) -> int:
        self._widget.show()
        return self._app.exec()


    def _on_recording_stopped(self, text: str):
        """Callback quand l'enregistrement est terminé."""
        print(f"Texte capturé: {text}")

    def _on_error(self, message: str):
        """Callback en cas d'erreur."""
        print(f"Erreur: {message}")
