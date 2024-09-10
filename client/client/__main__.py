from stats.utils import get_os

from guizero import App, PushButton, Text


def main():
    """
    Main function
    """
    app = App(title="Hello world")
    _ = Text(app, text="Welcome to the Hello world app!")
    __ = PushButton(
        app, text="Destroy")
    app.info("Info", "Loading...")
    app.display()


if __name__ in {"__main__", "__mp_main__"}:
    main()
