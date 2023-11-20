class RuntimeState:
    def __init__(self):
        self._running = True

    def handle_signal(self, signum, frame):
        self._running = False

    def is_running(self):
        return self._running