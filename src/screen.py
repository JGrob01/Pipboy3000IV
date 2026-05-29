class Screen:
    """Base class for all Pip-Boy screens/states."""

    def __init__(self, app):
        self.app = app

    def handle_event(self, event):
        pass

    def update(self, dt):
        pass

    def draw(self, surface):
        pass