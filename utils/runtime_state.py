class RuntimeState:
    def __init__(self):
        self.running = True

    def handle_signal(self, signum, frame):
        self.running = False
