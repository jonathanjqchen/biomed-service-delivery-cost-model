from abc import ABC
from staff import Staff


class RegionalStaff(Staff, ABC):

    def __init__(self, name, title, min_salary, max_salary,
                 clinical_renal_responsibility, imaging_responsibility,
                 cc_responsibility_ref):
        # Staff's name
        self.name = name
        # Staff's title (i.e. engineer, director, manager, etc.)
        self.title = title
        # Staff's min annual salary
        self.min_annual_salary = min_salary
        # Staff's max annual salary
        self.max_annual_salary = max_salary
        # List of cost centre for which this staff has oversight
        self.cost_centre_responsibility = self.determine_cost_centre_resp(clinical_renal_responsibility,
                                                                          imaging_responsibility,
                                                                          cc_responsibility_ref)
        super().__init__()
        # Number of cost centres supported
        self.oh_cost_per_cc = self.compute_oh_cost_per_cc()

    def compute_annual_salary(self):
        return (self.max_annual_salary + self.min_annual_salary) / 2

    def determine_cost_centre_resp(self, clinical_renal_resp, imaging_resp, cc_responsibility_ref):
        """

        :param clinical_renal_resp:
        :param imaging_resp:
        :param cc_responsibility_ref:
        :return:
        """

        '''
        Takes in a string with comma separated values and returns a list of each individual value (i.e. a string that
        represents a health authority)
            E.g. "FHA, PHSA, PHC" will return ["FHA", "PHSA", "PHC"]
        '''
        if type(clinical_renal_resp) == str:
            clinical_renal_resp_list = clinical_renal_resp.split(", ")
        else:
            clinical_renal_resp_list = 0

        if type(imaging_resp) == str:
            imaging_resp_list = imaging_resp.split(", ")
        else:
            imaging_resp_list = 0

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
        return self.total_compensation/len(self.cost_centre_responsibility)






