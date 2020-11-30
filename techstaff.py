from abc import ABC
from staff import Staff


class TechStaff(Staff, ABC):

    def __init__(self, level, qty, hourly_wage, hours_paid_per_year, cost_centre):
        self.level = level
        self.qty = qty
        self.hourly_wage = hourly_wage
        self.hours_paid_per_year = hours_paid_per_year
        self.cost_centre = cost_centre
        super().__init__()

    def compute_annual_salary(self):
        return self.qty * self.hourly_wage * self.hours_paid_per_year
