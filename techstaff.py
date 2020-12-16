from abc import ABC
from staff import Staff


class TechStaff(Staff, ABC):

    def __init__(self, level, qty, hourly_wage, hours_paid_per_year, cost_centre):
        """
        Initializes instance variables

        :param level: Tech staff level
        :param qty: Quantity of staff of this level at the cost centre that called __init__()
        :param hourly_wage: Hourly wage of staff at this level
        :param hours_paid_per_year: The total hours that a tech staff is paid in a year
        :param cost_centre: The cost centre to which this TechStaff object belongs
        """
        self.level = level
        self.qty = qty
        self.hourly_wage = hourly_wage
        self.hours_paid_per_year = hours_paid_per_year
        self.cost_centre = cost_centre
        super().__init__()

    def compute_annual_salary(self):
        """
        Compute total annual salary for this TechStaff object (i.e. all the staff at this level represented by this
        single object)

        :return: Float = quantity of tech staff at this level * hourly wage * hours paid per year
        """
        return self.qty * self.hourly_wage * self.hours_paid_per_year
