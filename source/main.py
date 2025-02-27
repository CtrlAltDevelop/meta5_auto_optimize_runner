from configparser import ConfigParser
import logging
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET
import csv
from typing import Any, Dict

from source.common.main_class import MainClass


class CaseSensitiveConfigParser(ConfigParser):
    # This class extends the ConfigParser class and likely provides functionality for parsing
    # configuration files with case sensitivity.
    def optionxform(self, option):
        """
        The `optionxform` function in Python simply returns the input `option` without any
        transformation.
        
        :param option: The `optionxform` method you provided seems to be a simple pass-through method
        that returns the input `option` parameter as is. If you have any specific questions or need
        further assistance related to this method or the `option` parameter, please feel free to ask!
        :return: The `optionxform` method is returning the `option` parameter as it is without any
        modification.
        """
        return option


# This class inherits from MainClass and is named Meta5AutoOptimizeRunner.
class Meta5AutoOptimizeRunner(MainClass):
    def __init__(self, base_path: Path, debug: bool = False):
        """
        The function initializes a class instance with specified base path and debug mode, creating
        directories for configurations, test data, and results, and reading settings from a
        configuration file.
        
        :param base_path: The `base_path` parameter is a Path object that represents the base directory
        path where your application or script is located. It is used to define the root directory for
        storing configuration files, test data, and result files within the application's directory
        structure
        :type base_path: Path
        :param debug: The `debug` parameter in the `__init__` method is a boolean flag that indicates
        whether the code should run in debug mode or not. When `debug` is set to `True`, it typically
        means that additional logging or debugging information will be displayed to help with
        troubleshooting and development. When, defaults to False
        :type debug: bool (optional)
        """
        super().__init__(base_path)
        self.debug: bool = debug
        self.config_path = base_path / "configs"
        self.data_path = base_path / "test_data"
        self.result_path = base_path / "results"

        self.config_path.mkdir(parents=True, exist_ok=True)
        self.result_path.mkdir(parents=True, exist_ok=True)

        self._config = CaseSensitiveConfigParser()
        self._config.read(base_path / "settings.ini", encoding="utf-8")

    def _validate_config(self) -> bool:
        """
        The function `_validate_config` checks if a specific key exists in a nested dictionary within
        the configuration and returns a boolean based on its presence.
        :return: The method `_validate_config` is returning a boolean value. It tries to access a
        specific key within the `TesterInputs` section of the configuration
        (`self._config['TesterInputs'][self._config['Tester']['ModeInputName']]`). If the key is found,
        it returns `True`. If the key is not found and a `KeyError` is raised, it prints an error
        message and
        """
        try:
            return bool(self._config['TesterInputs'][self._config['Tester']['ModeInputName']])
        except KeyError as error:
            print(f'ERROR, No option \"{self._config["Tester"]["ModeInputName"]}\" in section: "TesterInputs"')
            return False

    def __run__(self):
        if not self._validate_config():
            return

        if self.debug:
            _path = self.data_path / 'test_data'
        else:
            print("Select Report Optimizer file")
            _path = self._get_file_via_dialog(title=f"Report Optimizer file", filetypes=[("Report Optimizer", "*.csv")])

    def _remove_cache(self):
        """
        The function `_remove_cache` clears all files and directories within a specified folder path.
        :return: If the folder path does not exist or is not a directory, the function will return
        without performing any further actions. If the folder exists and is a directory, the function
        will attempt to clear the folder by removing all files and directories within it. Any errors
        encountered during the removal process will be logged, but the function will continue until all
        items in the folder have been processed. Finally, a log message
        """
        folder_path = Path(self._config['Meta']['DataFolderPath']) / 'Tester' / 'cache'
        if not folder_path.exists():
            logging.warning(f"The path {folder_path} does not exist.")
            return
        if not folder_path.is_dir():
            logging.warning(f"The path {folder_path} is not a directory.")
            return
        logging.info(f"Clearing folder: {folder_path}")
        for item in folder_path.iterdir():
            try:
                if item.is_file():
                    logging.info(f"Removing file: {item}")
                    item.unlink()
                elif item.is_dir():
                    logging.info(f"Removing directory: {item}")
                    shutil.rmtree(item)
            except Exception as e:
                logging.error(f"Failed to remove {item}: {e}")
        logging.info("Folder cleared successfully.")

    def _update_config(self, _config: ConfigParser, filename: str, inputs: Dict[str, Any], mode: str) -> ConfigParser:
        """
        The function `_update_config` updates a configuration file with specified values for different
        sections based on input parameters.
        
        :param _config: The `_config` parameter is a `ConfigParser` object that contains configuration
        settings for different sections such as "Account", "Tester", and "TesterInputs". These settings
        are used to update a new configuration with specific values for each section
        :type _config: ConfigParser
        :param filename: The `filename` parameter is a string that represents the path and filename for
        the HTML report file that will be generated by the program. In the provided code snippet, it is
        used to set the 'Report' key in the configuration file to specify the location where the report
        file will be saved
        :type filename: str
        :param inputs: The `_update_config` method takes in several parameters to update a configuration
        file. Here's a breakdown of the parameters:
        :type inputs: Dict[str, Any]
        :param mode: The `mode` parameter in the `_update_config` method is used to specify the mode
        input name in the configuration. This value is set in the "TesterInputs" section of the
        configuration file with the key being the mode input name and the value being the provided
        `mode` parameter
        :type mode: str
        :return: The function `_update_config` returns a `ConfigParser` object with updated
        configurations based on the input parameters `_config`, `filename`, `inputs`, and `mode`. The
        function updates the sections "Common", "Tester", and "TesterInputs" with values from the input
        `_config` and additional predefined key-value pairs. It also sets values from the `inputs`
        dictionary and the `mode`
        """
        config = CaseSensitiveConfigParser()
        config.add_section("Common")
        config.add_section("Tester")
        config.add_section("TesterInputs")

        for key, value in _config["Account"].items():
            config.set("Common", key, value)

        for key, value in _config["Tester"].items():
            config.set("Tester", key, value)

        for key, value in {
            # Optimization mode:
            # 0 = No optimization (single test)
            # 1 = Slow, complete optimization
            # 2 = Fast genetic-based optimization
            # 3 = All symbols selected in Market Watch
            # 4 = All symbols in the tester's symbol list
            'Optimization': '1',

            # The backtest model (how ticks are simulated):
            #  0 = Every tick
            #  1 = 1 minute OHLC
            #  2 = Open prices only
            'Model': '2',

            # Whether to enable/disable the use of custom dates:
            #  0 = Use the full available data
            #  1 = Use the FromDate/ToDate
            'Dates': '1',

            # Forward testing mode (split the test period):
            #  0 = No forward testing
            #  1 = Forward testing on 1/2 of the period
            #  2 = Forward testing on 1/3 of the period
            #  3 = Forward testing on 1/4 of the period
            #  4 = Custom
            'ForwardMode': '0',

            # Deposit currency (USD, EUR, etc.)
            'Currency': 'USD',

            # If 1, profits are shown in pips instead of currency. 0 means disabled.
            'ProfitInPips': '0',

            # Account leverage for the test (1:100, etc.)
            'Leverage': '100',

            # Execution mode:
            #  0 = Execution without delay
            #  1 = Execution with random delay
            'ExecutionMode': '0',

            # Optimization criterion:
            #  0 = Maximize balance
            #  1 = Maximize profit factor
            #  2 = Maximize expected payoff
            #  3 = Minimize drawdown
            'OptimizationCriterion': '0',

            # Whether to run a visual backtest (0 = no, 1 = yes)
            'Visual': '1',

            # Replace htm file if exist (0 = no, 1 = yes)
            # 0 = create new file
            # 1 = replace file if exist
            'ReplaceReport': '1',

            # close MetaTrader after test done (0 = no, 1 = yes)
            'ShutdownTerminal': '1',

            # path and filename for htm report file
            'Report': f'reports\\{filename}',
        }.items():
            config.set("Tester", key, value)

        for key, value in _config["TesterInputs"].items():
            config.set("TesterInputs", key, value)

        for key, value in inputs.items():
            config.set("TesterInputs", key, str(value))

        config.set('TesterInputs', self._config['Tester']['ModeInputName'], mode)
        return config

    def _xml_to_csv(self, xml_path: Path, output_path: Path):
        """
        The function `_xml_to_csv` converts data from an XML file to a CSV file based on specific
        worksheet and cell criteria.
        
        :param xml_path: The `xml_path` parameter is the path to the XML file that contains the data you
        want to convert to CSV format. This function parses the XML file to extract the data and convert
        it into a CSV file
        :type xml_path: Path
        :param output_path: The `output_path` parameter in the `_xml_to_csv` function is the path where
        the CSV file will be saved after converting the data from the XML file. It should be a `Path`
        object pointing to the location where you want to save the CSV file
        :type output_path: Path
        """
        SS_NS = 'urn:schemas-microsoft-com:office:spreadsheet'
        tree = ET.parse(xml_path)
        root = tree.getroot()
        worksheet = None
        for ws in root.findall('.//{%s}Worksheet' % SS_NS):
            if ws.get('{%s}Name' % SS_NS) == 'Tester Optimizator Results':
                worksheet = ws
                break
        if worksheet is None:
            raise ValueError("Worksheet 'Tester Optimizator Results' not found")
        table = worksheet.find('.//{%s}Table' % SS_NS)
        rows = table.findall('.//{%s}Row' % SS_NS)
        
        header_row = rows[0]
        header_cells = header_row.findall('.//{%s}Cell' % SS_NS)
        headers = [
            cell.find('{%s}Data' % SS_NS).text
            for cell in header_cells
            if cell.find('{%s}Data' % SS_NS) is not None
        ]
        
        data = []
        for row in rows[1:]:
            cells = row.findall('.//{%s}Cell' % SS_NS)
            row_data = [
                cell.find('{%s}Data' % SS_NS).text if cell.find('{%s}Data' % SS_NS) is not None else ''
                for cell in cells
            ]
            data.append(row_data)

        with open(output_path, 'w', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(headers)
            for row in data:
                writer.writerow(row)
