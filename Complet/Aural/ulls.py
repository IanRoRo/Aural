import pygetwindow as gw
import time
from datetime import datetime
from pynput import mouse, keyboard


class AuralMonitor:
    def __init__(self):
        self.last_input_time = time.time()
        self.mouse_listener = mouse.Listener(
            on_move=self._reset_timer,
            on_click=self._reset_timer,
            on_scroll=self._reset_timer,
        )
        self.kb_listener = keyboard.Listener(on_press=self._reset_timer)
        self.mouse_listener.start()
        self.kb_listener.start()

    def _reset_timer(self, *args):
        self.last_input_time = time.time()

    def get_data(self):
        try:
            win = gw.getActiveWindow()
            title = win.title if win else "Escriptori"
        except Exception:
            title = "Desconegut"
        actiu = "SI" if (time.time() - self.last_input_time) < 120 else "NO"
        ara = datetime.now()
        return [
            ara.strftime("%Y-%m-%d"),
            ara.strftime("%H:%M:%S"),
            title,
            actiu,
        ]


if __name__ == "__main__":
    monitor = AuralMonitor()
    try:
        while True:
            dades = monitor.get_data()
            print(f"Registrat: {dades[2]}")
            time.sleep(5)
    except KeyboardInterrupt:
        print("Aturat")
