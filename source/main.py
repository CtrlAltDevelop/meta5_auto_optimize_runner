import subprocess
from configparser import ConfigParser
import logging
from datetime import datetime
from pathlib import Path
import shutil
import csv
from tqdm import tqdm
from typing import Any, Dict
import xml.etree.ElementTree as ET

from source.common.main_class import MainClass


class CaseSensitiveConfigParser(ConfigParser):
    # This class extends the ConfigParser class and likely provides functionality for parsing
    # configuration files with case sensitivity.
    def optionxform(self, optionstr):
        """
        The `optionxform` function simply returns the input `optionstr` without any modifications.
        
        :param optionstr: The `optionxform` method you provided simply returns the `optionstr` parameter
        as is without any modification. This means that whatever value is passed to `optionstr` will be
        returned unchanged by the method
        :return: The `optionstr` parameter is being returned as is, without any modifications.
        """
        return optionstr


class Meta5AutoOptimizeRunner(MainClass):
    def __init__(self, base_path: Path, debug: bool = True):
        super().__init__(base_path)
        self.debug: bool = debug
        self.config_path = base_path / "configs"
        self.data_path = base_path / "test_data"
        self.result_path = base_path / "results"

        self.config_path.mkdir(parents=True, exist_ok=True)
        self.result_path.mkdir(parents=True, exist_ok=True)

        self._config = CaseSensitiveConfigParser()
        self._config.read(base_path / "settings.ini", encoding="utf-8")

    def __run__(self):
        if self.debug:
            _path = self.data_path / 'test_data'
        else:
            print("Select Report Optimizer file")
            _path = self._get_folder_via_dialog('Select folder with Set Input files')

        data_path = Path(self._config['Meta']['DataFolderPath']) / 'optimizes'
        data_path.mkdir(parents=True, exist_ok=True)
        print([e for e in _path.glob('*.set')])
        for file in tqdm(_path.glob('*.set'), desc='Run Strategy Optimizer'):
            filename = f'Res{file.name}_{int(datetime.now().timestamp())}'
            _config = self._update_config(self._config, filename, self._process_set_file(file))
            _config_path = self.config_path / f'{filename}.ini'
            with open(_config_path, mode="w", encoding="utf-8") as ini_file:
                _config.write(ini_file)
            with open(self.config_path / f'{filename}.set', mode="w", encoding="utf-8") as set_file:
                set_file.write('\n'.join([f"{key}={value}" for key, value in _config['TesterInputs'].items()]))
            subprocess.run([self._config['Meta']['TerminalPath'], f"/config:{_config_path}"])
            self._xml_to_csv(data_path / f'{filename}.htm', self.result_path / f'{filename}.xlsx')

    @staticmethod
    def _process_set_file(_config: Path) -> Dict[str, Any]:
        settings_dict = {}
        try:
            with open(_config, 'r', encoding='utf-16') as file:
                for line in file:
                    line = line.strip()
                    if line and not line.startswith(';') and '=' in line:
                        key, value = line.split('=', 1)
                        settings_dict[key.strip()] = value.strip()

        except FileNotFoundError:
            print(f"Error: File '{_config}' not found")
        except Exception as e:
            print(f"Error reading file: {e}")
        return settings_dict

    def _remove_cache(self):
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

    def _update_config(self, _config: ConfigParser, filename: str, inputs: Dict[str, Any]) -> ConfigParser:
        config = CaseSensitiveConfigParser()
        config.add_section("Common")
        config.add_section("Tester")
        config.add_section("TesterInputs")

        for key, value in _config["Account"].items():
            config.set("Common", key, value)

        for key, value in _config["Tester"].items():
            config.set("Tester", key, value)

        for key, value in {
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

            # Whether to run a visual backtest (0 = no, 1 = yes)
            'Visual': '0',

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
