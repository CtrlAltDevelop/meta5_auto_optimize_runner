import sys
import logging
from typing import Iterable, Optional, Tuple
import warnings
from contextlib import contextmanager
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime
from tkinter import Tk, filedialog


class MainClass:
    def __init__(self, base_path: Path):
        """
        The function initializes a class instance with a base path, sets up logging, and filters out
        UserWarning messages related to openpyxl module.
        
        :param base_path: The `base_path` parameter is a Path object that represents the base directory
        where your logs will be stored. It is used to set up the logging configuration for your
        application
        :type base_path: Path
        """
        self.base_path = base_path
        self.__logs_dir = self.base_path / 'logs'
        self.__ensure_logs_directory__()
        self.__logger = None
        self.__setup_logging__()
        warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

    @contextmanager
    def _tkinter_root(self):
        """
        The function creates a hidden Tkinter root window and yields it for use, ensuring it is
        destroyed after use.
        """
        root = Tk()
        try:
            root.withdraw()
            yield root
        finally:
            root.destroy()

    def __ensure_logs_directory__(self):
        """
        The function `__ensure_logs_directory__` attempts to create a logs directory and handles
        exceptions if the creation fails.
        """
        try:
            self.__logs_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f'Failed to create logs directory at {self.__logs_dir}: {e}')
            sys.exit(1)

    def __setup_logging__(self):
        """
        The function sets up logging configuration to capture and handle ERROR and CRITICAL logs in a
        custom logger with both file and console handlers.
        """
        # Create a custom logger
        self.__logger = logging.getLogger(__name__)
        self.__logger.setLevel(logging.ERROR)  # Capture only ERROR and CRITICAL logs

        # Formatter for logs
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # Generate log file name with today's date
        today_str = datetime.now().strftime('%Y-%m-%d')
        error_log_filename = f'{today_str}.log'
        error_log_path = self.__logs_dir / error_log_filename

        # Error log handler with rotation
        error_handler = RotatingFileHandler(error_log_path, maxBytes=5 * 1024 * 1024, backupCount=5)
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)

        # Console handler for real-time error feedback
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.ERROR)
        console_handler.setFormatter(formatter)

        # Add handlers to the logger
        self.__logger.addHandler(error_handler)
        self.__logger.addHandler(console_handler)

    def __run__(self):
        """
        The `__run__` method is a placeholder in Python that is meant to be overridden with the actual
        logic of the application.
        """
        pass

    def safe_run(self):
        """
        The `safe_run` function logs the start and end of an application's execution, handles
        exceptions, and prompts the user to exit if the application is packaged with PyInstaller.
        """
        try:
            self.__logger.debug('Application has started running.')
            self.__run__()
            self.__logger.debug('Application has finished running.')
        except Exception as e:
            self.__logger.exception('An unexpected error occurred:')
            log_file = self.__logs_dir / f'{datetime.now().strftime('%Y-%m-%d')}.log'
            print(f'\nAn error has occurred. Please check "{log_file}" for more details.\n')
        finally:
            if hasattr(sys, '_MEIPASS'):
                input('Press Enter to exit.')
    
    def _get_file_via_dialog(self, title: str, filetypes: Iterable[Tuple[str, str]], optional: bool = False) -> Optional[Path]:
        """
        This function opens a file dialog window in Python and returns the selected file path as a Path
        object, or None if no file is selected.
        
        :param title: The `title` parameter is a string that represents the title of the file dialog
        window that will be displayed to the user when they are prompted to select a file. It typically
        describes the purpose of selecting the file, such as "Select a File" or "Choose a Document"
        :type title: str
        :param filetypes: The `filetypes` parameter in the `_get_file_via_dialog` method is expected to
        be an iterable of tuples, where each tuple contains two strings. The first string in the tuple
        represents the description of the file type (e.g., "Text Files"), and the second string
        represents the file extension
        :type filetypes: Iterable[Tuple[str, str]]
        :param optional: The `optional` parameter in the `_get_file_via_dialog` method is a boolean flag
        that indicates whether selecting a file is optional or required. If `optional` is set to `True`,
        it means that the user can choose not to select a file and the method will return `None` in,
        defaults to False
        :type optional: bool (optional)
        :return: The function `_get_file_via_dialog` returns an optional `Path` object. If a file is
        selected via the file dialog, it returns the `Path` object representing the selected file. If no
        file is selected and the selection is not optional, it raises a `FileNotFoundError`. If no file
        is selected and the selection is optional, it returns `None`.
        """
        logging.debug(f"Opening file dialog: {title}")
        with self._tkinter_root():
            file = filedialog.askopenfile(title=title, filetypes=filetypes, initialdir=self.base_path)
            if not file and not optional:
                logging.error(f"{title} not selected.")
                raise FileNotFoundError(f"{title} not selected.")
            if file:
                selected_path = Path(file.name)
                logging.debug(f"File selected: {selected_path}")
                return selected_path
            return None

    def _get_folder_via_dialog(self, title: str, optional: bool = False) -> Optional[Path]:
        """
        This function opens a folder selection dialog using tkinter in Python and returns the selected
        folder path as a Path object or None.
        
        :param title: The `title` parameter is a string that represents the title of the folder dialog
        that will be displayed to the user when they are prompted to select a folder
        :type title: str
        :param optional: The `optional` parameter in the `_get_folder_via_dialog` method is a boolean
        flag that indicates whether selecting a folder is optional or required. If `optional` is set to
        `True`, the user can choose to not select a folder and the method will return `None`. If
        `optional`, defaults to False
        :type optional: bool (optional)
        :return: The function `_get_folder_via_dialog` returns an optional `Path` object. It returns the
        selected folder path as a `Path` object if a folder is selected via the dialog. If no folder is
        selected and the selection is not optional, it raises a `FileNotFoundError`. If no folder is
        selected but the selection is optional, it returns `None`.
        """
        logging.debug(f"Opening folder dialog: {title}")
        with self._tkinter_root():
            folder = filedialog.askdirectory(title=title, initialdir=self.base_path)
            if not folder and not optional:
                logging.error(f"{title} not selected.")
                raise FileNotFoundError(f"{title} not selected.")
            if folder:
                selected_path = Path(folder)
                logging.debug(f"Folder selected: {selected_path}")
                return selected_path
            return None
