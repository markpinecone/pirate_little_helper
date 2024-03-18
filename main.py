import threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.properties import ObjectProperty, BooleanProperty
from kivy.core.window import Window
from kivy.lang import Builder
from color_detector import ColorDetector
from pystray import MenuItem as item, Menu as menu, Icon as PystrayIcon
from PIL import Image

Builder.load_file('pirate_little_helper.kv')

class MainWindow(BoxLayout):
    log_layout = ObjectProperty()
    paused = BooleanProperty(True)

    def update_log(self, message):
        new_log_entry = Label(text=message, size_hint_y=None, height=30, markup=True, color=(1, 1, 1, 1))
        self.log_layout.add_widget(new_log_entry)
        self.log_layout.height += new_log_entry.height

    def start(self):
        if self.paused:
            self.paused = False
            self.update_log("Started")
            app = App.get_running_app()
            Clock.schedule_interval(app.update_detection, 2)

    def stop(self):
        if not self.paused:
            self.paused = True
            self.update_log("Stopped")
            app = App.get_running_app()
            Clock.unschedule(app.update_detection)

class Application(App):
    tray_icon = None

    def build(self):
        self.colors_dict = {'blue': (1, 1, 192), 'red': (175, 1, 1), 'green': (0, 191, 1)}
        self.detector = ColorDetector(window_title='Entropia Universe Client (64 bit) [Space]', colors_dict=self.colors_dict)
        self.main_window = MainWindow()
        Window.bind(on_request_close=self.on_request_close)
        return self.main_window

    def on_request_close(self, instance, *args):
        self.hide_app()
        return True

    def hide_app(self):
        # Hide the application's window and remove it from the taskbar
        if self.tray_icon:
            Window.minimize()
            Window.hide()
        return True

    def show_app(self):
        # Restore the application's window when the user wants to show the app
        if self.tray_icon:
            Window.restore()
            Window.show()

    def on_stop(self):
        if self.tray_icon:
            self.tray_icon.stop()

    def update_detection(self, dt):
        if not self.main_window.paused:
            pixel_counts = self.detector.detect_and_alert()
            if pixel_counts:
                formatted_counts = self.format_pixel_counts(pixel_counts)
                self.main_window.update_log(f"Pixel counts for each color: {formatted_counts}")

    def format_pixel_counts(self, pixel_counts):
        formatted_counts = "{"
        for color, count in pixel_counts.items():
            hex_color = '0000ff' if color == 'blue' else 'ff0000' if color == 'red' else '00bf01'
            formatted_counts += f"[color={hex_color}]{color}[/color]: {count}, "
        formatted_counts = formatted_counts.rstrip(', ') + "}"
        return formatted_counts

def run_tray_icon(app):
    icon_image = Image.open('icon.png')
    menu_items = menu(
        item('Show', lambda: app.show_app()),
        item('Quit', lambda: quit_app(app))
    )
    app.tray_icon = PystrayIcon('test', icon_image, 'Pirate Little Helper', menu_items)
    app.tray_icon.run()

def quit_app(app):
    def quit_app_internal(dt):
        app.stop()
        if app.tray_icon:
            app.tray_icon.stop()
    Clock.schedule_once(quit_app_internal)

if __name__ == '__main__':
    app = Application()
    tray_thread = threading.Thread(target=run_tray_icon, args=(app,))
    tray_thread.daemon = True
    tray_thread.start()
    app.run()
