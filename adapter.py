"""
Helper functions to adapt the dataset for analysis and modeling.
"""
import pandas as pd
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class DatasetColumnNames:
    """
    A class to store the column names of the dataset.
    """
    bmi: str
    age: str
    has_pcos: str
    hirsutism: str | None = None
    acne: str | None = None
    infertility: str | None = None
    menstrual_irregularity: str | None = None



class DatasetAdapter(ABC):
    """
    A class to adapt the dataset for analysis and modeling.
    """

    def __init__(self, dataset: pd.DataFrame):
        self.dataset = dataset

    @abstractmethod
    def convert(self) -> pd.DataFrame:
        """
        Adapt the dataset for analysis and modeling.

        Returns:
            pd.DataFrame: The adapted dataset.
        """
        ...

class LocalDatasetAdapter(DatasetAdapter):
    """
    A class to adapt the local dataset for analysis and modeling.
    """

    def convert(self) -> pd.DataFrame:
        dataframe = self.dataset.copy()
        features = DatasetColumnNames(
            bmi="Body Mass Index (BMI)",
            age="Age",
            menstrual_irregularity="Menstrual Irregularities",
            infertility="Gravida",  # TODO: Transform data to binary feature based on whether the patient has been pregnant or not.
        )
        return dataframe  # TODO: Implement the conversion logic.
    

class Dataset1Adapter(DatasetAdapter):
    """
    A class to adapt the Data 1 for analysis and modeling.
    """

    def get_features(self) -> DatasetColumnNames:
        return DatasetColumnNames(
            bmi="BMI",
            age="Age (yrs)",
            acne="Pimples(Y/N)",
            infertility="Pregnant(Y/N)",  # TODO: Deterrmine if this is a good proxy for infertility.
            has_pcos="PCOS (Y/N)",
            hirsutism="hair growth(Y/N)",
            menstrual_irregularity="Cycle(R/I)",  # SWAN or NHANES Values
        )

    def convert(self) -> pd.DataFrame:
        dataframe = self.dataset.copy()
        features = self.get_features()
        filtered_dataframe = dataframe[features.__dict__.values()]
        # convert SWAN/NHANES values to binary feature for menstrual irregularity.
        # filtered_dataframe[features.menstrual_irregularity] = filtered_dataframe[features.menstrual_irregularity].map({2 : 0, 4 : 1})
        return filtered_dataframe  # TODO: Implement the conversion logic.


class Dataset3Adapter(DatasetAdapter):
    """
    A class to adapt the Data 3 for analysis and modeling.
    """

    def convert(self) -> pd.DataFrame:
        dataframe = self.dataset.copy()
        features = DatasetColumnNames(
            bmi="BMI",
            age="Age",
            acne="Acne Severity",
            infertility="Fertility Concerns",
            menstrual_irregularity="Menstrual Regularity",
            has_pcos="Diagnosis",
            hirsutism="Hirsutism",  
        )
        filtered_dataframe = dataframe[features.__dict__.values()]
        ## map values
        # Menstrual Irregularity: Regular = 0, Irregular = 1
        filtered_dataframe[features.menstrual_irregularity] = filtered_dataframe[features.menstrual_irregularity].map({"Regular": 0, "Irregular": 1})
        # Fertility Concerns: No = 0, Yes = 1
        filtered_dataframe[features.infertility] = filtered_dataframe[features.infertility].map({"No": 0, "Yes": 1})
        # Acne Severity: None, Mild = 0, Moderate, Severe = 1
        filtered_dataframe[features.acne] = filtered_dataframe[features.acne].map({"None": 0, "Mild": 0, "Moderate": 1, "Severe": 1})
        # Hirsutism: No = 0, Yes = 1
        filtered_dataframe[features.hirsutism] = filtered_dataframe[features.hirsutism].map({"No": 0, "Yes": 1})
        # Diagnosis (PCOS): No = 0, Yes = 1
        filtered_dataframe[features.has_pcos] = filtered_dataframe[features.has_pcos].map({"No": 0, "Yes": 1}) 
        return filtered_dataframe
