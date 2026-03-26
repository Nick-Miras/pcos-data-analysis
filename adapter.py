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
    # TODO: Consider hair loss, weight gain as feature/s.



class DatasetAdapter(ABC):
    """
    A class to adapt the dataset for analysis and modeling.
    """

    def __init__(self, dataset: pd.DataFrame):
        self.dataset = dataset

    @abstractmethod
    def get_features(self) -> DatasetColumnNames:
        """
        Get the column names of the features in the dataset.

        Returns:
            DatasetColumnNames: The column names of the features in the dataset.
        """
        ...

    @abstractmethod
    def convert(self) -> pd.DataFrame:
        """
        Adapt the dataset for analysis and modeling.

        Returns:
            pd.DataFrame: The adapted dataset.
        """
        ...

    def replace_columns(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """
        Replace the column names of the dataset with the standardized column names.

        Args:
            dataframe (pd.DataFrame): The dataset to be adapted.
            features (DatasetColumnNames): The standardized column names.

        Returns:
            pd.DataFrame: The dataset with the replaced column names.
        """
        features = self.get_features()
        column_mapping = {value: key for key, value in features.__dict__.items()}
        return dataframe.rename(columns=column_mapping)


class LocalDatasetAdapter(DatasetAdapter):
    """
    A class to adapt the local dataset for analysis and modeling.
    """
    def get_features(self) -> DatasetColumnNames:
        return DatasetColumnNames(
            bmi="Body Mass Index (BMI)",
            age="Age",
            menstrual_irregularity="Menstrual Irregularities",
            infertility="Gravida",  # TODO: Transform data to binary feature based on whether the patient has been pregnant or not.
            has_pcos="Ultrasound Findings"
        )

    def convert(self) -> pd.DataFrame:
        dataframe = self.dataset.copy()
        features = self.get_features()
        filtered_dataframe = dataframe[[feature for feature in features.__dict__.values() if feature]]

        # Transform the 'Gravida' column to a binary feature for infertility based on whether the patient has been pregnant or not.
        filtered_dataframe[features.infertility] = filtered_dataframe[features.infertility].apply(lambda x: 1 if x == 'G1P0' or x == 'G3P2' else 0)
        # Transform the 'Menstrual Irregularities' column to a binary feature for menstrual irregularity.
        filtered_dataframe[features.menstrual_irregularity] = filtered_dataframe[features.menstrual_irregularity].apply(lambda x: 1 if x == "Irregular" else 0)
        # Transform the 'Ultrasound Findings' column to a binary feature for PCOS diagnosis.
        filtered_dataframe[features.has_pcos] = filtered_dataframe[features.has_pcos].apply(lambda x: 1 if x == "PCO" else 0)
        # obtain other data features from the 'Symptoms' column.
        filtered_dataframe["acne"] = dataframe["Symptoms"].apply(lambda x: 1 if isinstance(x, str) and ("acne" in x.lower() or "pimples" in x.lower()) else 0)
        filtered_dataframe["hirsutism"] = dataframe["Symptoms"].apply(lambda x: 1 if isinstance(x, str) and ("hirsutism" in x.lower() or "hair growth" in x.lower()) else 0) 
        filtered_dataframe["irregular_masses"] = dataframe["Symptoms"].apply(lambda x: 1 if isinstance(x, str) and ("irregular masses" in x.lower()) else 0) 
        # filtered_dataframe["weight_gain"] = dataframe["Symptoms"].apply(lambda x: 1 if isinstance(x, str) and ("weight gain" in x.lower()) else 0) 
        
        return self.replace_columns(filtered_dataframe)  # TODO: Implement the conversion logic.


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
        filtered_dataframe[features.menstrual_irregularity] = filtered_dataframe[features.menstrual_irregularity].map({2 : 0, 4 : 1, 5 : 1})
        return self.replace_columns(filtered_dataframe)


class Dataset3Adapter(DatasetAdapter):
    """
    A class to adapt the Data 3 for analysis and modeling.
    """

    def get_features(self) -> DatasetColumnNames:
        return DatasetColumnNames(
            bmi="BMI",
            age="Age",
            acne="Acne Severity",
            infertility="Fertility Concerns",
            menstrual_irregularity="Menstrual Regularity",
            has_pcos="Diagnosis",
            hirsutism="Hirsutism",  
        )

    def convert(self) -> pd.DataFrame:
        dataframe = self.dataset.copy()
        features = self.get_features()
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
