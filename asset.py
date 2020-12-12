class Asset:

    """
    This class handles all data and behaviour associated with the assets that are inputted by the user into the budget
    report
    """

    budget_report_input_file_path = "model_inputs/budget_report_input.xlsx"  # Path to budget report input file

    def __init__(self, model_num, name, qty, health_auth, site_code, shop_code, sites_cc_dict):
        """
        Initializes instance variables, calls strip() on strings to make sure there are no white spaces at the front or
        end when importing data from Excel
        :param name: Asset description
        :param qty: Quantity of assets being budgeted for
        :param health_auth: Health authority to which the asset belongs
        :param site_code: Three-letter site code
        :param shop_code: Shop code, for determining the function (clinical, renal imaging) of a device
        :param sites_cc_dict: Dictionary reference that shows corresponding cost centres for a given site
        """
        self.model_num = model_num
        self.name = name.strip()
        self.qty = qty
        self.health_auth = health_auth.strip()
        self.site_code = site_code.strip()
        self.shop_code = shop_code.strip()
        self.function = self.assign_function()
        self.cost_centre = self.assign_temp_cost_centre(sites_cc_dict).strip()
        self.avg_support_hours = 2

    def assign_function(self):
        """
        Assigns asset function (clinical, renal, imaging) based on the asset's shop code
        :return: String denoting the asset's function
        """
        if self.shop_code == "IMAG" or self.shop_code == "IMAG0" or self.shop_code == "IMAG1":
            return "imaging"
        elif self.shop_code == "REN" or self.shop_code == "FHA_R":
            return "renal"
        else:
            return "clinical"

    def assign_temp_cost_centre(self, sites_cc_dict):
        """
        Assigns a string representing the cost centre name to cost_centre instance variable; actual CostCentre object
        replaces this string once it has been instantiated and assign_permanent_cost_centre() is called
        :param sites_cc_dict: Dictionary reference that shows corresponding cost centres for a given site
        :return: String representing cost centre's name
        """

        if self.function == "clinical":
            index = 0   # Clinical cost centre is stored at index 0 of sites_cc_dict value list
        elif self.function == "renal":
            index = 1   # Renal cost centre is stored at index 1 of sites_cc_dict value list
        else:
            index = 2   # Imaging cost centre is stored at index 2 of sites_cc_dict value list

        # Store list of cost centres for corresponding site_code in cost_centres
        cost_centres = sites_cc_dict[self.site_code]

        # Check that cost centre we need is actually a string (i.e. not a NaN); if valid, return the cost centre
        if type(cost_centres[index]) == str:
            return cost_centres[index]
        # If not valid, try to return clinical cost centre
        elif index != 0 and type(cost_centres[0]) == str:
            return cost_centres[0]
        # If not valid, try to return imaging cost centre
        elif index != 2 and type(cost_centres[2]) == str:
            return cost_centres[2]
        # Else return renal cost centre
        else:
            return cost_centres[1]

    def assign_permanent_cost_centre(self, cost_centre):
        """
        Updates cost_centre instance variable to be an actual CostCentre object, not just a string
        :param cost_centre: CostCentre object
        """
        self.cost_centre = cost_centre
