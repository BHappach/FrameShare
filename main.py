import sys
import numpy as np
import pyautogui
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QShortcut
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen, QColor, QKeySequence
from PyQt5.QtCore import Qt, QRect, QSize, QTimer, QSettings
from PIL import ImageGrab
from functools import partial

ImageGrab.grab = partial(ImageGrab.grab, all_screens=True)

class ScreenCaptureWindow(QMainWindow):
    def __init__(self, overlay_window):
        super().__init__()
        self.overlay_window = overlay_window
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.X11BypassWindowManagerHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.settings = QSettings("screen_capture_settings.ini", QSettings.IniFormat)
        self.load_settings()

        self.label = QLabel(self)
        self.label.setGeometry(self.rect())
        self.label.setScaledContents(True)

        self.start_pos = None
        self.start_rect = self.rect()
        self.border_width = 6
        self.resizing = False
        self.moving = False
        self.resize_corner_size = 30

        self.maximized = False  # Status, ob das Fenster maximiert ist
        self.setWindowTitle("FrameShare Output")
        self.show()

        # QShortcut für Strg+Q hinzufügen
        self.shortcut = QShortcut(QKeySequence("Ctrl+Q"), self)
        self.shortcut.activated.connect(self.close_application)

    def update_capture(self, frame, mouse_rel_x, mouse_rel_y):
        h, w, _ = frame.shape
        qimg = QImage(frame.data, w, h, 3 * w, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg).scaled(self.label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # Erstelle ein QPainter-Objekt, um das Fadenkreuz zu zeichnen
        painter = QPainter(pixmap)
        draw_crosshair(painter, (mouse_rel_x, mouse_rel_y))
        painter.end()

        self.label.setPixmap(pixmap)

    def resize_to_overlay_aspect_ratio(self):
        """Passt das Seitenverhältnis des Fensters an das Overlay-Fenster an"""
        if self.overlay_window is not None:
            overlay_rect = self.overlay_window.geometry()
            aspect_ratio = overlay_rect.width() / overlay_rect.height()

            current_rect = self.geometry()
            new_width = current_rect.width()
            new_height = int(new_width / aspect_ratio)

            if new_height > 0:
                self.setGeometry(current_rect.x(), current_rect.y(), new_width, new_height)
                self.label.setGeometry(self.rect())

            # Begrenze die Fenstergröße auf die Bildschirmgröße
            limit_window_size_to_screen(self)

    def maximize_window(self):
        """Maximiert das Fenster basierend auf der Bildschirmgröße und dem Seitenverhältnis"""
        if self.overlay_window is not None:
            screen = QApplication.screenAt(self.pos())
            if screen is None:
                screen = QApplication.primaryScreen()  # Fallback auf den primären Bildschirm

            available_geometry = screen.availableGeometry()  # Bereich ohne Taskleiste
            aspect_ratio = self.overlay_window.width() / self.overlay_window.height()

            max_width = available_geometry.width()
            max_height = available_geometry.height()

            # Berechne die maximale Größe basierend auf dem Seitenverhältnis
            if aspect_ratio > 1:  # Breiter als hoch
                new_width = max_width
                new_height = int(new_width / aspect_ratio)
            else:  # Höher als breit
                new_height = max_height
                new_width = int(new_height * aspect_ratio)

            self.setGeometry(available_geometry.x(), available_geometry.y(), new_width, new_height)
            self.label.setGeometry(self.rect())
            self.maximized = True  # Setze den Maximierungsstatus

    def move_to_next_screen(self):
        """Verschiebt das Fenster auf den nächsten Bildschirm"""
        screens = QApplication.screens()
        current_screen = QApplication.screenAt(self.pos())
        if current_screen:
            current_index = screens.index(current_screen)
            next_index = (current_index + 1) % len(screens)  # Nächster Bildschirm, zyklisch
            next_screen = screens[next_index]
            screen_geometry = next_screen.geometry()

            # Bewege das Fenster auf den nächsten Bildschirm
            self.setGeometry(screen_geometry.x(), screen_geometry.y(), self.width(), self.height())

    def mouseDoubleClickEvent(self, event):
        """Wird bei einem Doppelklick ausgelöst"""
        if event.button() == Qt.LeftButton:
            if event.modifiers() == Qt.ControlModifier:
                # Strg + Doppelklick: Fenster auf den nächsten Bildschirm verschieben
                self.move_to_next_screen()
            else:
                # Normaler Doppelklick: Fenster maximieren
                self.maximize_window()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            pos = event.pos()
            rect = self.rect()
            self.start_pos = event.globalPos()
            if (abs(rect.width() - pos.x()) <= self.resize_corner_size and 
                abs(rect.height() - pos.y()) <= self.resize_corner_size):
                self.resizing = True
                self.start_rect = self.geometry()
            else:
                self.start_rect = self.geometry()
                self.moving = True

    def mouseMoveEvent(self, event):
        if self.start_pos:
            if self.resizing:
                delta = event.globalPos() - self.start_pos
                new_width = max(self.start_rect.width() + delta.x(), 100)

                # Seitenverhältnis des Overlay-Fensters verwenden
                overlay_rect = self.overlay_window.geometry()
                aspect_ratio = overlay_rect.width() / overlay_rect.height()

                # Höhe basierend auf der neuen Breite berechnen
                new_height = int(new_width / aspect_ratio)
                
                if new_width > 0 and new_height > 0:
                    new_size = QSize(new_width, new_height)
                    new_rect = QRect(self.start_rect.topLeft(), new_size)
                    self.setGeometry(new_rect)
                    self.label.setGeometry(self.rect())
            elif self.moving:
                delta = event.globalPos() - self.start_pos
                new_pos = self.start_rect.topLeft() + delta
                if new_pos.x() >= 0 and new_pos.y() >= 0:
                    new_rect = QRect(new_pos, self.start_rect.size())
                    self.setGeometry(new_rect)
                    self.label.setGeometry(self.rect())

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start_pos = None
            self.resizing = False
            self.moving = False

            # Begrenze die Fenstergröße auf die Bildschirmgröße, wenn das Fenster losgelassen wird
            limit_window_size_to_screen(self)

            self.save_settings()

    def load_settings(self):
        x = self.settings.value("x", 100, type=int)
        y = self.settings.value("y", 100, type=int)
        width = self.settings.value("width", 800, type=int)
        height = self.settings.value("height", 600, type=int)
        self.setGeometry(x, y, width, height)

    def save_settings(self):
        rect = self.geometry()
        self.settings.setValue("x", rect.x())
        self.settings.setValue("y", rect.y())
        self.settings.setValue("width", rect.width())
        self.settings.setValue("height", rect.height())

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QPen(Qt.GlobalColor.lightGray, self.border_width, Qt.SolidLine))
        painter.drawRect(self.rect())

    def close_application(self):
        """Beendet die Applikation, wenn Strg+Q gedrückt wird und das Fenster fokussiert ist"""
        QApplication.quit()

def limit_window_size_to_screen(screen_capture):
    """Begrenzt die Größe des Fensters auf die Größe des Monitors ohne die Taskleiste und behält das Seitenverhältnis bei"""
    screen = QApplication.screenAt(screen_capture.pos())
    if screen is None:
        screen = QApplication.primaryScreen()  # Fallback auf den primären Bildschirm

    available_geometry = screen.availableGeometry()  # Bereich ohne Taskleiste
    screen_geometry = screen.geometry()  # Gesamtbereich des Bildschirms

    # Maximiere die Größe des Fensters innerhalb der verfügbaren Geometrie (ohne Taskleiste)
    max_width = available_geometry.width()
    max_height = available_geometry.height()

    # Hol das aktuelle Seitenverhältnis des Fensters
    window_geometry = screen_capture.geometry()
    aspect_ratio = window_geometry.width() / window_geometry.height()

    # Begrenze die Größe basierend auf dem Seitenverhältnis
    if window_geometry.width() > max_width:
        new_width = max_width
        new_height = int(new_width / aspect_ratio)
    elif window_geometry.height() > max_height:
        new_height = max_height
        new_width = int(new_height * aspect_ratio)
    else:
        # Wenn die Fenstergröße innerhalb der Beschränkungen liegt, behalte sie bei
        new_width = window_geometry.width()
        new_height = window_geometry.height()

    # Stelle sicher, dass das Fenster nicht über den Bildschirmrand hinausgeht
    new_x = max(screen_geometry.x(), min(window_geometry.x(), screen_geometry.right() - new_width))
    new_y = max(screen_geometry.y(), min(window_geometry.y(), screen_geometry.bottom() - new_height))

    # Setze die neue begrenzte Größe und Position
    screen_capture.setGeometry(new_x, new_y, new_width, new_height)

class OverlayWindow(QMainWindow):
    def __init__(self, screen_capture):
        super().__init__()
        self.screen_capture = screen_capture  # Referenz auf das ScreenCaptureWindow
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.X11BypassWindowManagerHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.settings = QSettings("overlay_settings.ini", QSettings.IniFormat)
        self.load_settings()

        self.start_pos = None
        self.start_rect = self.rect()
        self.border_width = 6
        self.resizing = False
        self.moving = False
        self.resize_corner_size = 30

        self.default_color = QColor(Qt.GlobalColor.lightGray)
        self.moving_color = QColor(0, 255, 0)
        self.resizing_color = QColor(0, 0, 255)

        self.label = QLabel(self)
        self.label.setGeometry(self.rect())
        self.label.setScaledContents(True)
        self.update_style()
        self.setWindowTitle("Overlay")
        self.show()

    def paintEvent(self, event):
        painter = QPainter(self)
        if self.resizing:
            painter.setPen(QPen(self.resizing_color, self.border_width, Qt.SolidLine))
        elif self.moving:
            painter.setPen(QPen(self.moving_color, self.border_width, Qt.SolidLine))
        else:
            painter.setPen(QPen(self.default_color, self.border_width, Qt.SolidLine))
        painter.drawRect(self.rect())

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            pos = event.pos()
            rect = self.rect()
            self.start_pos = event.globalPos()
            if (abs(rect.width() - pos.x()) <= self.resize_corner_size and 
                abs(rect.height() - pos.y()) <= self.resize_corner_size):
                self.resizing = True
                self.start_rect = self.geometry()
                self.update_style()
            else:
                self.start_rect = self.geometry()
                self.moving = True
                self.update_style()

    def mouseMoveEvent(self, event):
        if self.start_pos:
            if self.resizing:
                delta = event.globalPos() - self.start_pos
                new_width = max(self.start_rect.width() + delta.x(), 100)
                new_height = max(self.start_rect.height() + delta.y(), 100)
                if new_width > 0 and new_height > 0:
                    new_size = QSize(new_width, new_height)
                    new_rect = QRect(self.start_rect.topLeft(), new_size)
                    self.setGeometry(new_rect)
                    self.label.setGeometry(self.rect())
                    self.update_overlay()
                    self.update_style()
            elif self.moving:
                delta = event.globalPos() - self.start_pos
                new_pos = self.start_rect.topLeft() + delta
                if new_pos.x() >= 0 and new_pos.y() >= 0:
                    new_rect = QRect(new_pos, self.start_rect.size())
                    self.setGeometry(new_rect)
                    self.label.setGeometry(self.rect())
                    self.update_style()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start_pos = None
            self.resizing = False
            self.moving = False
            self.save_settings()
            self.update_style()

    def resizeEvent(self, event):
        """Ruft das ScreenCaptureWindow auf, um das Seitenverhältnis anzupassen."""
        self.screen_capture.resize_to_overlay_aspect_ratio()

    def load_settings(self):
        x = self.settings.value("x", 100, type=int)
        y = self.settings.value("y", 100, type=int)
        width = self.settings.value("width", 800, type=int)
        height = self.settings.value("height", 600, type=int)
        self.setGeometry(x, y, width, height)

    def save_settings(self):
        rect = self.geometry()
        self.settings.setValue("x", rect.x())
        self.settings.setValue("y", rect.y())
        self.settings.setValue("width", rect.width())
        self.settings.setValue("height", rect.height())

    def update_style(self):
        self.label.setStyleSheet(f"background:rgba(0,0,0,0); border: {self.border_width}px solid {self.border_to_hex()}")

    def border_to_hex(self):
        if self.resizing:
            return self.resizing_color.name()
        elif self.moving:
            return self.moving_color.name()
        else:
            return self.default_color.name()

    def update_overlay(self):
        overlay_img = np.ones((self.height(), self.width(), 4), dtype=np.uint8) * 255
        overlay_img[:, :, 3] = 0
        overlay_img = np.array(overlay_img)
        h, w, _ = overlay_img.shape
        qimg = QImage(overlay_img.data, w, h, 4 * w, QImage.Format_RGBA8888)
        self.label.setPixmap(QPixmap.fromImage(qimg).scaled(self.label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def get_screenshot_region(self):
        rect = self.geometry()
        screen = QApplication.primaryScreen()
        screen_rect = screen.geometry()
        absolute_rect = QRect(rect.x() + screen_rect.x() + self.border_width, rect.y() + screen_rect.y() + self.border_width, rect.width() - (2*self.border_width), rect.height() - (2*self.border_width))
        return (absolute_rect.x(), absolute_rect.y(), absolute_rect.x() + absolute_rect.width(), absolute_rect.y() + absolute_rect.height())

def draw_crosshair(painter, center, size=20, color=QColor(0, 255, 0), thickness=2):
    x, y = center
    half_size = size // 2
    pen = QPen(color, thickness)
    painter.setPen(pen)
    # Horizontal line
    painter.drawLine(x - half_size, y, x + half_size, y)
    # Vertical line
    painter.drawLine(x, y - half_size, x, y + half_size)

def capture_frame(overlay, screen_capture):
    # Hol den Screenshot-Bereich des Overlay-Fensters
    region = overlay.get_screenshot_region()
    screenshot = ImageGrab.grab(bbox=region)
    frame = np.array(screenshot)

    # Mausposition relativ zum Overlay-Bereich
    mouse_x, mouse_y = pyautogui.position()
    mouse_rel_x = mouse_x - region[0]
    mouse_rel_y = mouse_y - region[1]

    # Verhältnis der Größen zwischen dem Overlay und dem ScreenCaptureWindow
    overlay_width = overlay.width()
    overlay_height = overlay.height()
    capture_width = screen_capture.width()
    capture_height = screen_capture.height()

    # Skaliere die Mausposition entsprechend dem Verhältnis der Fenstergrößen
    if overlay_width > 0 and overlay_height > 0:  # Um Division durch Null zu vermeiden
        scale_x = capture_width / overlay_width
        scale_y = capture_height / overlay_height

        scaled_mouse_x = int(mouse_rel_x * scale_x)
        scaled_mouse_y = int(mouse_rel_y * scale_y)

        # Sicherstellen, dass die Mausposition innerhalb des aufgenommenen Bereichs liegt
        scaled_mouse_x = max(0, min(scaled_mouse_x, capture_width - 1))
        scaled_mouse_y = max(0, min(scaled_mouse_y, capture_height - 1))

        screen_capture.update_capture(frame, scaled_mouse_x, scaled_mouse_y)
    else:
        screen_capture.update_capture(frame, 0, 0)

def main():
    app = QApplication(sys.argv)

    screen_capture = ScreenCaptureWindow(None)  # Initialisiere das ScreenCaptureWindow ohne Overlay
    overlay = OverlayWindow(screen_capture)  # Übergibt das ScreenCaptureWindow an das OverlayWindow
    screen_capture.overlay_window = overlay  # Jetzt kennt ScreenCaptureWindow auch das Overlay

    # Passe das Seitenverhältnis basierend auf dem Overlay direkt beim Start an
    screen_capture.resize_to_overlay_aspect_ratio()

    timer = QTimer()
    timer.timeout.connect(lambda: overlay.update_overlay())
    timer.start(50)

    capture_timer = QTimer()
    capture_timer.timeout.connect(lambda: capture_frame(overlay, screen_capture))
    capture_timer.start(50)

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
