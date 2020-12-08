import pandas as pd
import math
import statistics
from techstaff import TechStaff

# File path to tech_labour_hours.xlsx
tech_labour_hours_path = "model_inputs/labour_reports/tech_labour_hours.xlsx"

# Read "General Summary" into a dataframe
gen_sum_df = pd.read_excel(tech_labour_hours_path, sheet_name="General Summary")

# File path to staff_salaries.xlsx
staff_salaries_file_path = "model_inputs/labour_reports/staff_salaries.xlsx"


def read_tech_staff_ref():

    # Read tech staff data into a dataframe
    tech_staff_df = pd.read_excel(staff_salaries_file_path, sheet_name="Tech Staff")

    return tech_staff_df


def read_tech_vac_summary():

    # Read "Vacation Summary" into a dataframe
    vac_sum_df = pd.read_excel(tech_labour_hours_path, sheet_name="Vacation Summary")

    # Dictionary with key: "level" and value: "avg_vac"
    annual_vac_days_by_level_dict = vac_sum_df.set_index("level")["avg_vac"].to_dict()

    return annual_vac_days_by_level_dict


def read_hours_paid_per_year():

    # Number of hours techs are paid for in a year
    hours_paid_per_year = gen_sum_df["hours_paid_per_year"]

    return hours_paid_per_year


def read_semi_prod_days():

    # semi_prod_days_per_year is the number of days in a year less weekends, stats, and sick days
    semi_prod_days_per_year = gen_sum_df["semi_prod_days_per_year"]

    return semi_prod_days_per_year


def read_hours_per_day():

    # avg_hours_per_day is the average number of hours worked by a tech in a day
    avg_hours_per_day = gen_sum_df["avg_hours_per_day"]

    return avg_hours_per_day


def read_tech_staff_salary_sched():

    # Read "Tech Staff Salary Sched" into dataframe, use year6_hourly_wage
    tech_staff_salary_df = pd.read_excel(staff_salaries_file_path, sheet_name="Tech Staff Salary Sched")
    tech_staff_salary_dict = tech_staff_salary_df.set_index("level")["year6_hourly_wage"].to_dict()

    return tech_staff_salary_dict


class CostCentre:

    regional_staff = None
    tech_staff_df = read_tech_staff_ref()
    tech_staff_salary_dict = read_tech_staff_salary_sched()
    hours_paid_per_year = read_hours_paid_per_year()
    OH_TECH_TIME_PERCENTAGE = 0.3
    financial_reports_folder_path = "model_inputs/financial_reports/"
    hours_worked_per_day = read_hours_per_day()
    semi_prod_days_per_year = read_semi_prod_days()
    annual_vac_days_by_level = read_tech_vac_summary()

    def __init__(self, asset, budget_report):
        self.name = asset.cost_centre
        self.assets = [asset]
        self.health_auth = asset.health_auth
        self.function = asset.function
        CostCentre.regional_staff = self.get_regional_staff_objects(budget_report)
        self.regional_staff_oh = self.compute_regional_staff_oh(self.regional_staff)
        self.tech_staff = self.create_tech_staff_objects()
        self.tech_staff_oh = self.compute_tech_staff_oh()
        self.non_labour_oh = self.compute_non_labour_oh()
        self.pohr = self.compute_pohr()
        self.weighted_avg_tech_hourly_wage = self.compute_weighted_avg_tech_hourly_wage()

    def compute_regional_staff_oh(self, regional_staff):

        total_oh = 0

        for staff in regional_staff:
            if self.name in staff.cost_centre_responsibility:
                total_oh += staff.oh_cost_per_cc

        return total_oh

    def get_regional_staff_objects(self, budget_report):
        return budget_report.create_regional_staff_objects()

    def create_tech_staff_objects(self):

        # Pull row from dataframe with information relevant to this cost centre
        tech_staff_df = self.tech_staff_df[self.tech_staff_df["cost_centre_name"] == self.name]

        '''
        List of qty of level x techs, where x is:
            - 8 at tech_level_qty[0]
            - 9 at tech_level_qty[1]
            - 10 at tech_level_qty[2]
            - 12 at tech_level_qty[3]
        '''
        tech_level_qty = tech_staff_df[["level8", "level9", "level10", "level12"]].values.tolist()[0]

        tech_staff = []

        for qty in tech_level_qty:
            if qty != 0 and not math.isnan(qty):

                # Create level 8 techs
                if tech_level_qty.index(qty) == 0:
                    tech_staff.append(TechStaff(8,
                                                qty,
                                                self.tech_staff_salary_dict.get(8),
                                                self.hours_paid_per_year,
                                                self))

                # Create level 9 techs
                if tech_level_qty.index(qty) == 1:
                    tech_staff.append(TechStaff(9,
                                                qty,
                                                self.tech_staff_salary_dict.get(9),
                                                self.hours_paid_per_year,
                                                self))

                # Create level 10 techs
                if tech_level_qty.index(qty) == 2:
                    tech_staff.append(TechStaff(10,
                                                qty,
                                                self.tech_staff_salary_dict.get(10),
                                                self.hours_paid_per_year,
                                                self))

                # Create level 12 techs
                if tech_level_qty.index(qty) == 3:
                    tech_staff.append(TechStaff(12,
                                                qty,
                                                self.tech_staff_salary_dict.get(12),
                                                self.hours_paid_per_year,
                                                self))

        return tech_staff

    def compute_tech_staff_oh(self):

        total_tech_labour_cost = 0

        for staff in self.tech_staff:
            total_tech_labour_cost += staff.total_compensation

        return self.OH_TECH_TIME_PERCENTAGE * total_tech_labour_cost

    def compute_non_labour_oh(self):

        file_path = self.financial_reports_folder_path + \
                    "{function}/{health_auth}.xlsx".format(function=self.function, health_auth=self.health_auth)

        financials_df = pd.read_excel(file_path, sheet_name=self.name)

        actual_historical_non_labour_oh = financials_df["actual_partial_oh"].tolist()
        budgeted_historical_non_labour_oh = financials_df["budgeted_partial_oh"].tolist()

        max_historical_non_labour_oh = []
        index = 0
        while index < len(actual_historical_non_labour_oh):
            if actual_historical_non_labour_oh[index] > budgeted_historical_non_labour_oh[index]:
                max_historical_non_labour_oh.append(actual_historical_non_labour_oh[index])
            else:
                max_historical_non_labour_oh.append(budgeted_historical_non_labour_oh[index])
            index += 1

        mean_max_historical_non_labour_oh = statistics.fmean(max_historical_non_labour_oh)

        return mean_max_historical_non_labour_oh

    def compute_pohr(self):

        annual_labour_hours = 0

        for staff in self.tech_staff:
            days_per_staff = self.semi_prod_days_per_year - self.annual_vac_days_by_level.get(staff.level)
            annual_labour_hours += (staff.qty * days_per_staff * self.hours_worked_per_day)

        total_oh = self.non_labour_oh + self.regional_staff_oh + self.tech_staff_oh

        return total_oh / (0.8 * annual_labour_hours)

    def compute_weighted_avg_tech_hourly_wage(self):

        total_num_staff = 0
        weighted_avg_hourly_wage = 0

        for staff in self.tech_staff:
            total_num_staff += staff.qty

        if total_num_staff > 0:
            for staff in self.tech_staff:
                weighted_avg_hourly_wage += self.tech_staff_salary_dict.get(staff.level) * (staff.qty / total_num_staff)

        return weighted_avg_hourly_wage
