import datetime
import re
import json
from typing import TextIO


class Experiment:
    # The names of the experiments, only present inside log files
    experiment_keywords = ['bragg']
    # The name of the csv and log files with the extension
    file_name: str

    # Start and end of the experiment
    init_time: datetime.datetime
    end_time: datetime.datetime

    # Total number of layers in the experiment.
    # Configuration steps not included as layers
    n_layers: int = 0

    # The keyword among the experiment keywords that fits the given file. Ex: A1417 is 'bragg'
    experiment_keyword: str
    # The code of the experiment (ex: A1717)
    code: str

    # Ordered : first step starts first
    step_list: list
    last_step_number: int
    label: float

    def __init__(self, log_file_name: str, experiment_keyword: str, file_path: str):
        self.file_name = log_file_name[:-4]
        self.step_list = []
        self.experiment_keyword = experiment_keyword
        self.code = self.get_experiment_code()
        self.label = self.get_experiment_label()
        self.last_step_number = Experiment.get_last_step_number(file_path)

    def get_step_index_for_rel_time(self, rel_time: float, previous_index: int):
        previous_step: Step = self.step_list[previous_index]
        
        # If this rel_time still corresponds to same step
        if previous_step.rel_start < rel_time < previous_step.rel_end:
            return previous_index
        # Try to find the corresponding step
        else:
            n_try: int = 5
            i = previous_index + 1
            while n_try > 0:
                try:
                    step: Step = self.step_list[i]
                except IndexError:
                    return
                # print(f"{step.rel_start} < {rel_time} < {step.rel_end}")
                if step.rel_start <= rel_time <= step.rel_end:
                    return i
                n_try -= 1
                i += 1

            raise ValueError(
                f"Problème d'index d'étape : {rel_time} "
                f"pas présent après {previous_step}"
            )
    
    @classmethod
    def get_last_step_number(cls, file_name: str):
        with open(file_name, 'r', encoding='utf-8', errors='replace') as f:
            txt: str = f.read()
            last_digits: str = re.findall(r'(\d{4})(?=\|)', txt)[-1]
            return int(last_digits)

    def __str__(self) -> str:
        return self.code

    def print_experiment(self):
        print(str(vars(self)).encode('utf-8'))
        for step in self.step_list:
            print(str(vars(step)).encode('utf-8'))

    def get_experiment_keyword(self) -> str:
        """Returns the string like 'Bragg' to identify and group experiments"""

        for e in self.experiment_keywords:
            if e in self.file_name:
                return e

    def get_experiment_code(self) -> str:
        """Returns the string like 'A1417'"""
        str_match = re.search(r'[A-Z]\d{4}', self.file_name)
        if str_match:
            return str_match.group(0)

        else:
            return input(
                f"File <{self.file_name}> belongs to {self.experiment_keyword} "
                "yet has no experiment code with format like 'A1420'\nPlease enter the experiment code: "
            )

    def get_experiment_label(self) -> float:
        labels_file = open('labels.json', 'r')
        labels_json = json.load(labels_file)
        try:
            return labels_json[self.code]
        except KeyError:
            return float(input(f'Please enter the label for experiment {self.code}: '))

    @classmethod
    def is_relevant_experiment(cls, f: TextIO) -> bool:
        """
        Returns True if any experiment keyword is found.
        """

        result = re.search(r'Loop #\d/\d', f.read())

        f.seek(0)  # Put the cursor back to the beginning so we can read again
        return result is not None

    @classmethod
    def find_relevant_experiment(cls, f: TextIO) -> str:
        """
        If the file is relevant, returns the name of the experiment it is part of.
        Else, returns "".
        """
        file_text = f.read().lower()
        for keyword in Experiment.experiment_keywords:
            if keyword in file_text:
                f.seek(0)
                return keyword


class Step:
    # The label is linked to the experiment
    experiment: Experiment
    # Ex: 0008| 2021/09/24 05:54:07,850| 76.47nm GaAs
    line: str
    line_index: int

    step_number: int

    start: datetime.datetime
    end: datetime.datetime

    rel_start: float = -1
    rel_end: float = -1
    
    curvature: list[tuple[float, float]]
    wafer_temperature: list[tuple[float, float]]
    roughness: list[tuple[float, float]]
    reflectivity: dict[float, list[tuple[float, float]]]

    def __init__(self, experiment: Experiment, line: str, line_index: int):
        self.experiment = experiment
        self.line = line
        self.line_index = line_index

        self.start = Step.get_timestamp(self.line)
        self.step_number = Step.get_step_number(self.line)
        
        self.curvature = []
        self.wafer_temperature = []
        self.roughness = []
        self.reflectivity = {}
    
    def __str__(self):
        return f"{self.experiment} step n°{self.step_number}"
        
    @classmethod
    def get_step_number(cls, line: str) -> int:
        try:
            return int(re.search(r'\d{4}(?=\|)', line).group(0))
        except AttributeError:
            return 0

    @classmethod
    def is_layer(cls, line: str) -> bool:
        # If we can find '| 278.89nm' or '| 278.89 nm' inside the line then it is a layer line
        return re.search(r'(?<=\| )[+-]?([0-9]*[.])?[0-9]+(?= ?nm)', line) is not None

    @classmethod
    def get_timestamp(cls, line: str) -> datetime.datetime:
        # OwO wat are u doing step data?
        timestamp_str = re.search(r'\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2},\d{3}', line).group(0)
        return datetime.datetime.strptime(timestamp_str, '%Y/%m/%d %H:%M:%S,%f')

    @classmethod
    def identify_line(cls, line: str) -> str:
        """
        Takes a line in lower case and finds what type of line was given.
        """
        # List of (possible_keywords, name)
        step_list: list[tuple[list[str], str]] = [
            (['starting recipe', 'with priority'], 'start'),
            (['mont', 'pour', 'ox'], 'montée déox'),
            (['descente tampon'], 'descente tampon'),
            (['fin tampon'], 'fin tampon'),
            (['tampon'], 'tampon'),  # Must be after the 'descente' and 'fin' or false positive
            (['loop #'], 'loop'),
            (['descente'], 'descente'),
            (['wait'], 'wait'),
            (['end'], 'end')
        ]

        if Step.is_layer(line):
            return 'layer'
        else:
            for step_kwrd in step_list:
                if all(e in line for e in step_kwrd[0]):
                    return step_kwrd[1]

        # Find second occurence of | and return what's next
        return line.strip().split('|')[2]


class OtherStep(Step):
    step_type: str

    def __init__(self, experiment: Experiment, line: str, line_index: int, line_type: str):
        super(OtherStep, self).__init__(experiment, line, line_index)

        self.step_type = line_type


class Layer(Step):
    # Ex: GaAs
    element: str

    # Percentage of the element (100% if only element)
    percentage: float

    # Size of the layer in nanometers (ex: 76.47)
    size: float

    def __init__(self, experiment: Experiment, line: str, line_index: int):
        super(Layer, self).__init__(experiment, line, line_index)

        self.extract_layer_data()

    def extract_layer_data(self):

        # Find a word preceded by 'nm '
        self.element = re.search(r'(?<=nm )\w*', self.line).group(0)

        # Get a float followed by 'nm' or ' nm'
        self.size = float(re.search(r'[+-]?([0-9]*[.])?[0-9]+(?= ?nm)', self.line).group(0))

        # Get a float followed by '%'. If no percentage is found, returns 100
        percentage_match = re.search(r'[+-]?([0-9]*[.])?[0-9]+(?=%)', self.line)
        if percentage_match is None:
            self.percentage = 100
        else:
            self.percentage = float(percentage_match.group(0))
