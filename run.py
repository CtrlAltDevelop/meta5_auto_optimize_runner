import warnings
from pathlib import Path

from source.main import Meta5AutoOptimizeRunner


if __name__ == '__main__':
    """
    The main entry point of the application.
    """
    warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

    app = Meta5AutoOptimizeRunner(Path.cwd())
    app.safe_run()
