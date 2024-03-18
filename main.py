from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.properties import ObjectProperty, BooleanProperty
from kivy.lang import Builder
from color_detector import ColorDetector

# Load the KV file
Builder.load_file('pirate_little_helper.kv')

class MainWindow(BoxLayout):
    log_layout = ObjectProperty()
    paused = BooleanProperty(True)  # Initialize as True to prevent auto-starting

    def update_log(self, message):
        new_log_entry = Label(
            text=message,
            size_hint_y=None,
            height=30,
            markup=True,
            color=(1, 1, 1, 1)
        )
        self.log_layout.add_widget(new_log_entry)
        self.log_layout.height += new_log_entry.height

    def start(self):
        # Avoid re-scheduling if it's already started
        if self.paused:
            self.paused = False
            self.update_log("Started")
            # Use get_running_app to correctly access the Application instance
            app = App.get_running_app()
            Clock.schedule_interval(app.update_detection, 2)

    def stop(self):
        # Avoid stopping if it's already stopped
        if not self.paused:
            self.paused = True
            self.update_log("Stopped")
            # Again, use get_running_app for accessing the Application instance for unscheduling
            app = App.get_running_app()
            Clock.unschedule(app.update_detection)

class Application(App):
    def build(self):
        colors_dict = {'blue': (1, 1, 192), 'red': (175, 1, 1), 'green': (0, 191, 1)}
        self.detector = ColorDetector(window_title='Entropia Universe Client (64 bit) [Space]', colors_dict=colors_dict)
        self.main_window = MainWindow()
        return self.main_window

    def update_detection(self, dt):
        # Make sure this still checks for 'paused' as a safety, though it should be managed via scheduling now
        if not self.main_window.paused:
            pixel_counts = self.detector.detect_and_alert()
            if pixel_counts is not None:
                formatted_counts = self.format_pixel_counts(pixel_counts)
                self.main_window.update_log(f"Pixel counts for each color: {formatted_counts}")

    def format_pixel_counts(self, pixel_counts):
        formatted_counts = "{"
        for color, count in pixel_counts.items():
            hex_color = '0000ff' if color == 'blue' else 'ff0000' if color == 'red' else '00bf01'
            formatted_counts += f"[color={hex_color}]{color}[/color]: {count}, "
        formatted_counts = formatted_counts.rstrip(', ') + "}"
        return formatted_counts

if __name__ == '__main__':
    Application().run()