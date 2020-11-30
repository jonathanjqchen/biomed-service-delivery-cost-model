import pandas as pd
from abc import ABC, abstractmethod


def get_benefits_multiplier():
    """
    Parses for the benefits_multiplier inputted by the user in regional_staff_salaries.xlsx, staff salaries are
    multiplied by benefits_multiplier to obtain total_compensation.

    :return: Benefits multiplier as a float
    """

    # File path to regional_staff_salaries.xlsx
    regional_staff_salaries_file_path = "model_inputs/labour_reports/staff_salaries.xlsx"

    # Read benefits multiplier into dataframe
    benefits_multiplier_df = pd.read_excel(regional_staff_salaries_file_path,
                                           sheet_name="Benefits Multiplier",
                                           header=None,
                                           usecols="A:B",
                                           nrows=1)

    return benefits_multiplier_df.at[0, 1]


class Staff(ABC):
    benefits_multiplier = get_benefits_multiplier()

    def __init__(self):
        self.annual_salary = self.compute_annual_salary()
        self.total_compensation = self.compute_total_compensation()

    @abstractmethod
    def compute_annual_salary(self):
        pass

    def compute_total_compensation(self):
        return self.annual_salary * self.benefits_multiplier
