from abc import ABC
from staff import Staff


class RegionalStaff(Staff, ABC):

    def __init__(self, name, title, min_salary, max_salary,
                 clinical_renal_responsibility, imaging_responsibility,
                 cc_responsibility_ref):

        """
        Initializes instance variables

        :param name: Staff's name
        :param title: Staff's title (i.e. engineer, director, etc.)
        :param min_salary: Staff's min annual salary
        :param max_salary: Staff's max annual salary
        :param clinical_renal_responsibility: String containing staff's clinical/renal HA oversight (e.g. "FHA, VCH")
        :param imaging_responsibility: String containing staff's imaging responsibilities (e.g. "FHA")
        :param cc_responsibility_ref: Nested dict with information about the cost centres associated with each
                                      HA-function combination. See BudgetReport.cost_centre_responsibility_dict.
        """

        # Staff's name
        self.name = name
        # Staff's title (i.e. engineer, director, manager, etc.)
        self.title = title
        # Staff's min annual salary
        self.min_annual_salary = min_salary
        # Staff's max annual salary
        self.max_annual_salary = max_salary
        # List of cost centres for which this staff has oversight
        self.cost_centre_responsibility = self.determine_cost_centre_resp(clinical_renal_responsibility,
                                                                          imaging_responsibility,
                                                                          cc_responsibility_ref)
        # Call super().__init__() before self.compute_oh_cost_per_cc() to get annual_salary and total_compensation
        super().__init__()
        # OH cost to assign per cost centre
        self.oh_cost_per_cc = self.compute_oh_cost_per_cc()

    def compute_annual_salary(self):
        """
        Computes regional staff's annual salary.

        :return: The average of the staff's maximum and minimum in their salary range.
        """

        return (self.max_annual_salary + self.min_annual_salary) / 2

    def determine_cost_centre_resp(self, clinical_renal_resp, imaging_resp, cc_responsibility_ref):
        """
        Determines the cost centres for which a regional staff has oversight.

        :param clinical_renal_resp: Single string containing comma-separated values, where each value is a HA that the
                                    regional staff in question has clinical/renal oversight.
        :param imaging_resp: Single string containing comma-separated values, where each value is a HA that the regional
                             staff in question has imaging oversight.
        :param cc_responsibility_ref: Nested dict with information about the cost centres associated with each
                                      HA-function combination. See BudgetReport.cost_centre_responsibility_dict.
        :return: List of cost centres for which a regional staff has oversight.
        """

        # The if-else blocks below take in a single string containing comma-separated values and returns a list of
        # strings containing each individual value. If a string isn't passed in, return 0 instead.
        #    E.g. Input "FHA, PHSA, PHC" will return ["FHA", "PHSA", "PHC"]

        if type(clinical_renal_resp) == str:
            clinical_renal_resp_list = clinical_renal_resp.split(", ")
        else:
            clinical_renal_resp_list = 0

        if type(imaging_resp) == str:
            imaging_resp_list = imaging_resp.split(", ")
        else:
            imaging_resp_list = 0

        # Store all cost centres associated with clinical_renal_resp_list and imaging_resp_list in
        # cc_responsibility_list

        cc_responsibility_list = []

        if clinical_renal_resp_list != 0:
            for health_auth in clinical_renal_resp_list:
                clinical = cc_responsibility_ref[health_auth]["clinical"]
                cc_responsibility_list += clinical
                renal = cc_responsibility_ref[health_auth]["renal"]
                cc_responsibility_list += renal

        if imaging_resp_list != 0:
            for health_auth in imaging_resp_list:
                imaging = cc_responsibility_ref[health_auth]["imaging"]
                cc_responsibility_list += imaging

        return cc_responsibility_list

    def compute_oh_cost_per_cc(self):
        """
        Computes the amount of the regional staff's salary to distribute to each cost centre's OH.

        :return: Float that takes the regional staff's total compensation and divides it by the number of cost centres
                 for which they have oversight.
        """

        return self.total_compensation/len(self.cost_centre_responsibility)






