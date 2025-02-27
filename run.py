from pathlib import Path

from source.main import Meta5AutoOptimizeRunner


if __name__ == '__main__':
    """
    The main entry point of the application.
    """
    app = Meta5AutoOptimizeRunner(Path.cwd())
    app.safe_run()
