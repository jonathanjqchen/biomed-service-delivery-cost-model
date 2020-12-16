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

"""
########################################################################################################################
##################################### MODULE SCOPE FUNCTIONS BELOW #####################################################
########################################################################################################################
"""


def read_tech_staff_ref():
    """
    Reads data from "Tech Staff" sheet in staff_salaries.xlsx, which gives us information about the staffing level of
    techs at all the cost centres.

    :return: DataFrame with columns "cost_centre_name", "health_auth", "function", "level8", "level9", "level10",
             "level12".

             Note: The "levelx" columns contain a float indicating the number of techs of that level at the
             corresponding cost centre.
    """

    tech_staff_df = pd.read_excel(staff_salaries_file_path, sheet_name="Tech Staff")

    return tech_staff_df


def read_tech_vac_summary():
    """
    Reads into a dict the "level" and "avg_vac" columns from "Vacation Summary" sheet in tech_labour_hours.xlsx.

    :return: Dict in the following form:
                Key: level (int: 8, 9, 10, 12)
                Value: avg_vac (int)
    """

    vac_sum_df = pd.read_excel(tech_labour_hours_path, sheet_name="Vacation Summary")
    annual_vac_days_by_level_dict = vac_sum_df.set_index("level")["avg_vac"].to_dict()

    return annual_vac_days_by_level_dict


def read_hours_paid_per_year():
    """
    Reads in the number of hours for which techs get paid in a year from "General Summary" sheet of
    tech_labour_hours.xlsx.

    :return: Float representing number of hours for which a tech is paid in a year.
    """

    hours_paid_per_year = gen_sum_df["hours_paid_per_year"]

    return hours_paid_per_year


def read_semi_prod_days():
    """
    Reads in "semi_prod_days_per_year" from "General Summary" sheet of tech_labour_hours.xlsx.

    :return: Float representing number of days in a year less weekends, stats, and sick days.
    """

    semi_prod_days_per_year = gen_sum_df["semi_prod_days_per_year"]

    return semi_prod_days_per_year


def read_hours_per_day():
    """
    Reads in average hours worked per day from "General Summary" sheet of tech_labour_hours.xlsx.

    :return: Float representing average hours worked per day by a tech.
    """

    avg_hours_per_day = gen_sum_df["avg_hours_per_day"]

    return avg_hours_per_day


def read_tech_staff_salary_sched():
    """
    Reads data from "Tech Staff Salary Sched" sheet in staff_salaries.xlsx, which gives us information about tech staff
    hourly wage by hour and years of experience---function currently only looks at the "year6_hourly_wage" column.

    :return: Dict with the following format:
                Key: level (int: 8, 9, 10, 12)
                Value: year6_hourly_wage (float)
    """

    tech_staff_salary_df = pd.read_excel(staff_salaries_file_path, sheet_name="Tech Staff Salary Sched")
    tech_staff_salary_dict = tech_staff_salary_df.set_index("level")["year6_hourly_wage"].to_dict()

    return tech_staff_salary_dict


"""
########################################################################################################################
######################################## COSTCENTRE CLASS BELOW ########################################################
########################################################################################################################
"""


class CostCentre:
    """
    This class handles data and behaviour specific to each cost centre. This includes information about staffing levels
    in the cost centre, the amount of OH incurred, etc.
    """

    # Updated in __init__ to store list of RegionalStaff objects
    regional_staff = None

    # DataFrame with information about staffing levels at each cost centre
    tech_staff_df = read_tech_staff_ref()

    # Dict with tech staff hourly wages by level
    tech_staff_salary_dict = read_tech_staff_salary_sched()

    # Number of hours techs get paid for each year
    hours_paid_per_year = read_hours_paid_per_year()

    # % of time that techs spend doing non-device related work (i.e. attending meetings, assisting clinical staff, etc.)
    OH_TECH_TIME_PERCENTAGE = 0.35

    # Path to directory containing financial reports
    financial_reports_folder_path = "model_inputs/financial_reports/"

    # Average number of hours a tech works in a day
    hours_worked_per_day = read_hours_per_day()

    # Number of days in a year less weekends, stat holidays, and average annual sick days
    semi_prod_days_per_year = read_semi_prod_days()

    # Average number of vacation days granted to a tech by level
    annual_vac_days_by_level = read_tech_vac_summary()

    def __init__(self, asset, budget_report):
        """
        :param asset: Asset object used to initialize the list of Asset objects associated with this cost centre
        :param budget_report: BudgetReport object
        """
        # Cost centre name
        self.name = asset.cost_centre
        # List of asset objects in this cost centre
        self.assets = [asset]
        # Health authority under which this cost centre falls
        self.health_auth = asset.health_auth
        # Function of this cost centre (clinical, renal, imaging)
        self.function = asset.function
        # List of all RegionalStaff objects
        CostCentre.regional_staff = self.get_regional_staff_objects(budget_report)
        # Contribution to cost centre OH from regional staff total compensation
        self.regional_staff_oh = self.compute_regional_staff_oh(self.regional_staff)
        # List of TechStaff objects
        self.tech_staff = self.create_tech_staff_objects()
        # Contribution to cost centre OH from tech staff total compensation
        self.tech_staff_oh = self.compute_tech_staff_oh()
        # Contribution to cost centre OH from non-labour accounts in financial reports
        self.non_labour_oh = self.compute_non_labour_oh()
        # Predetermined overhead rate
        self.pohr = self.compute_pohr()
        # Weighted average hourly tech wage
        self.weighted_avg_tech_hourly_wage = self.compute_weighted_avg_tech_hourly_wage()

    def compute_regional_staff_oh(self, regional_staff):
        """
        Iterates through each regional staff and checks to see if this cost centre is overseen by them. If it is, then
        add the staff's oh_cost_per_cc to this cost centre's regional staff OH.

        :return: Regional staff OH for this cost centre.
        """

        total_oh = 0

        for staff in regional_staff:
            if self.name in staff.cost_centre_responsibility:
                total_oh += staff.oh_cost_per_cc

        return total_oh

    def get_regional_staff_objects(self, budget_report):
        """
        Function call to create RegionalStaff objects.

        :return: List of RegionalStaff objects.
        """

        return budget_report.create_regional_staff_objects()

    def create_tech_staff_objects(self):
        """
        Reads "Tech Staff" worksheet from staff_salaries.xlsx to pull the row corresponding to this cost centre. Creates
        tech staff objects using pulled data.

        :return: List of TechStaff objects (Maximum 4 objects, one for each level. Each TechStaff object will have a
                 "qty" field that indicates the number of staff of that level working at the cost centre.)
        """

        # Pull row from df with information relevant to this cost centre
        tech_staff_df = self.tech_staff_df[self.tech_staff_df["cost_centre_name"] == self.name]

        # Create a list of floats indicating the quantity of techs for each level:
        #      - Level 8 techs at tech_level_qty[0]
        #      - Level 9 techs at tech_level_qty[1]
        #      - Level 10 techs at tech_level_qty[2]
        #      - Level 12 techs at tech_level_qty[3]
        tech_level_qty = tech_staff_df[["level8", "level9", "level10", "level12"]].values.tolist()[0]

        # Create TechStaff objects and append them to tech_staff
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
        """
        Iterates through TechStaff objects assigned to this cost centre and adds their OH contribution to this cost
        centre's tech staff OH cost.

        :return: Tech staff OH for this cost centre.
        """

        total_tech_labour_cost = 0

        for staff in self.tech_staff:
            total_tech_labour_cost += staff.total_compensation

        return self.OH_TECH_TIME_PERCENTAGE * total_tech_labour_cost

    def compute_non_labour_oh(self):
        """
        Compute an estimated non-labour OH for this cost centre based on historical OH amounts from previous years.

        :return: Non-labour OH for this cost centre.
        """

        # Find the appropriate financial report Excel workbook and worksheet to parse
        file_path = self.financial_reports_folder_path + "{function}/{health_auth}.xlsx".format(function=self.function, health_auth=self.health_auth)
        financials_df = pd.read_excel(file_path, sheet_name=self.name)

        # Pull actual and budgeted partial OH for each fiscal year into a list
        # For clinical and renal cost centres, partial OH is total expenses less labour expense.
        # For imaging cost centres, partial OH is total expenses less labour and contracts expense.
        actual_historical_non_labour_oh = financials_df["actual_partial_oh"].tolist()
        budgeted_historical_non_labour_oh = financials_df["budgeted_partial_oh"].tolist()

        # Create a list max_historical_non_labour_oh that contains the larger OH value out of actual and budgeted
        # partial OH for each fiscal year
        max_historical_non_labour_oh = []
        index = 0

        while index < len(actual_historical_non_labour_oh):
            if actual_historical_non_labour_oh[index] > budgeted_historical_non_labour_oh[index]:
                max_historical_non_labour_oh.append(actual_historical_non_labour_oh[index])
            else:
                max_historical_non_labour_oh.append(budgeted_historical_non_labour_oh[index])
            index += 1

        # Compute the mean OH of max_historical_non_labour_oh
        mean_max_historical_non_labour_oh = statistics.fmean(max_historical_non_labour_oh)

        return mean_max_historical_non_labour_oh

    def compute_pohr(self):
        """
        Compute POHR for this cost centre by taking the estimated annual OH for this cost centre and dividing it by the
        estimated annual tech labour hours for this cost centre.

        :return: Pre-determined overhead rate for this cost centre.
        """

        annual_labour_hours = 0

        for staff in self.tech_staff:
            days_per_staff = self.semi_prod_days_per_year - self.annual_vac_days_by_level.get(staff.level)
            annual_labour_hours += (staff.qty * days_per_staff * self.hours_worked_per_day)

        total_oh = self.non_labour_oh + self.regional_staff_oh + self.tech_staff_oh

        # Take 80% of annual labour hours because 80% is the standard productivity rate cited in literature after
        # accounting for idle time
        return total_oh / (0.8 * annual_labour_hours)

    def compute_weighted_avg_tech_hourly_wage(self):
        """
        Compute weighted average hourly wage for techs at this cost centre based on the number of techs of each level
        and the wages they earn.

        :return: A float computed by computing the following for each TechStaff object:
                    Hourly wage for staff at this level * (Num staff at this level / Total num staff)
        """

        total_num_staff = 0
        weighted_avg_hourly_wage = 0

        for staff in self.tech_staff:
            total_num_staff += staff.qty

        if total_num_staff > 0:
            for staff in self.tech_staff:
                weighted_avg_hourly_wage += self.tech_staff_salary_dict.get(staff.level) * (staff.qty / total_num_staff)

        return weighted_avg_hourly_wage
