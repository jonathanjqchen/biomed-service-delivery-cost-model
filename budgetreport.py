import pandas as pd
import xlsxwriter
import os
from asset import Asset
from costcentre import CostCentre
from regionalstaff import RegionalStaff

pd.set_option("display.expand_frame_repr", False)


def read_sites_cost_centres_reference():
    """
    Pulls data from cost_centres_and_sites_reference.xlsx into a dictionary so that we can find the corresponding cost
    centres for a given site
    :return: Dictionary with key: "site" and value: ["clinical cost centre", "renal cost centre", "imaging cost centre]
    """

    # File path to cost_centres_and_sites_reference.xlsx
    sites_cc_file_path = "model_inputs/cost_centres_and_sites/cost_centres_and_sites_reference.xlsx"

    # Read into df the "site", "clinical_cost_centre", "renal_cost_centre", "imaging_cost_centre" fields
    sites_cc_df = pd.read_excel(sites_cc_file_path, sheet_name="Sites", usecols="A, D:F")

    # Convert dataframe into dictionary
    sites_cc_dict = sites_cc_df.set_index("site_code").T.to_dict("list")

    return sites_cc_dict


def read_cc_responsibility_reference():
    """

    :return: Nested dictionary in the form {"HA1": {"function1": ["cost_centre1, cost_centre2"]
                                                    "function2": ["cost_centre1"]
                                                    "function3": ["cost_centre1, cost_centre2, cost_centre3"]
                                            "HA2": ... }
    """

    # File path to cost_centres_and_sites_reference.xlsx
    sites_cc_file_path = "model_inputs/cost_centres_and_sites/cost_centres_and_sites_reference.xlsx"

    cc_responsibility_df = pd.read_excel(sites_cc_file_path, sheet_name="Cost Centres", usecols="B:D")

    health_auth = cc_responsibility_df["health_authority"].unique()
    function = cc_responsibility_df["function"].unique()
    cc_responsibility_dict = {health_auth[0]: {function[0]: [], function[1]: [], function[2]: []},
                              health_auth[1]: {function[0]: [], function[1]: [], function[2]: []},
                              health_auth[2]: {function[0]: [], function[1]: [], function[2]: []},
                              health_auth[3]: {function[0]: [], function[1]: [], function[2]: []}}

    for ha in health_auth:
        for func in function:
            temp_df = cc_responsibility_df.loc[(cc_responsibility_df["health_authority"] == ha) &
                                               (cc_responsibility_df["function"] == func)]
            temp_list = temp_df["cost_centre_name"].to_list()
            cc_responsibility_dict[ha][func] = temp_list

    return cc_responsibility_dict


class BudgetReport:
    """
    This class handles all data and behaviour associated with the budget report input and budget report output Excel
    files
    """
    # Path to budget report input file
    budget_report_input_file_path = "model_inputs/budget_report_input.xlsx"
    # Dict with sites and corresponding cost centres
    sites_cost_centre_dict = read_sites_cost_centres_reference()
    # Dict with HA and corresponding cost centres
    cost_centre_responsibility_dict = read_cc_responsibility_reference()

    # Number of rows to skip in budget report input file to get to asset details
    # SKIP_ROWS = 4

    def __init__(self):
        """
        Initialize instance variables
        """

        # self.recompute_oh = self.assign_recompute_oh()
        # Dictionary with key: "cost centre string" and value: CostCentre object
        self.cost_centres = {}

    # def assign_recompute_oh(self):
    #     """
    #     Pulls corresponding cell values in budget report input file to determine if user has updated financial reports
    #     or labour reports
    #     :return: Boolean indicating whether or not OH should be recomputed
    #     """
    #
    #     # Read user responses into a dataframe
    #     df = pd.read_excel(self.budget_report_input_file_path, header=None, usecols="A:B")
    #
    #     # If either the financial reports or labour reports have been updated, then rerun OH computation, else don't
    #     if df.at[0, 1].lower() == "y" or df.at[1, 1].lower() == "y":
    #         return True
    #     else:
    #         return False

    def create_asset_objects(self):
        """
        Pulls asset details inputted by user into budget report input file and creates an Asset object for each row of
        asset details entered
        :return: List of Asset objects that correspond to input entered by user into budget report input file
        """

        # Read asset details into dataframe
        df = pd.read_excel(self.budget_report_input_file_path, sheet_name="User Input")

        '''
        Convert dataframe into dictionary...
        Key: "df index"
        Value: ["asset_description", "quantity", "health_auth", "site_code", "shop_code"]
        '''
        # assets_dict = df.set_index("asset_description").T.to_dict("list")
        assets_dict = df.T.to_dict("list")

        assets = []

        # Iterate through dictionary, create Asset object for each entry, and append to assets list
        for asset, details in assets_dict.items():
            assets.append(Asset(details[0],  # asset_description
                                details[1],  # quantity
                                details[2],  # health_auth
                                details[3],  # site_code
                                details[4],  # shop_code
                                self.sites_cost_centre_dict))

        return assets

    def create_cost_centre_objects(self, assets, budget_report):
        """

        :param assets:
        :param budget_report:
        :return:
        """
        for asset in assets:
            '''
            If the asset's cost centre already exists in the cost_centres dictionary, append the asset to the CostCentre
            object's list of assets.
            
            If the asset's cost centre doesn't already exist in the cost_centres dictionary, create the CostCentre
            object and then add it to the dictionary (asset is added to the CostCentre object by default)
            '''
            if asset.cost_centre in self.cost_centres:
                self.cost_centres.get(asset.cost_centre).assets.append(asset)
            else:
                self.cost_centres[asset.cost_centre] = CostCentre(asset, budget_report)

            # Get the most recently inserted key into cost_centres dictionary (i.e. a cost centre string)
            last_key_inserted = list(self.cost_centres.keys())[-1]

            # Fulfill cost centre-asset bidirectional relationship by assigning a CostCentre object to the asset
            asset.assign_permanent_cost_centre(self.cost_centres.get(last_key_inserted))

    def create_regional_staff_objects(self):

        # File path to regional_staff_salaries.xlsx
        regional_staff_salaries_file_path = "model_inputs/labour_reports/staff_salaries.xlsx"

        # Read regional staff data into dataframe
        regional_staff_df = pd.read_excel(regional_staff_salaries_file_path, sheet_name="Regional Staff")

        # Convert dataframe into dictionary with key: "name", and values: ["all other fields"]
        regional_staff_dict = regional_staff_df.set_index("name").T.to_dict("list")

        regional_staff = []

        for staff_name, staff_details in regional_staff_dict.items():
            regional_staff.append(RegionalStaff(staff_name,  # Staff name
                                                staff_details[0],  # Staff title (i.e. Director, engineer, etc.)
                                                staff_details[2],  # Min salary
                                                staff_details[3],  # Max salary
                                                staff_details[4],  # Clinical and renal responsibilities
                                                staff_details[5],  # Imaging responsibilities
                                                self.cost_centre_responsibility_dict)
                                  )

        return regional_staff

    def compute_asset_support_hours(self):

        # File path to asset_support_hours_reference.xlsx
        asset_support_hours_file_path = "model_inputs/wo_reports/asset_support_hours_reference.xlsx"

        asset_support_hours_df = pd.read_excel(asset_support_hours_file_path)
        asset_support_hours_df = asset_support_hours_df[["asset_description",
                                                         "model_number",
                                                         "avg_support_hour_per_model",
                                                         "count_asset"]]

        for key in self.cost_centres:
            cost_centre = self.cost_centres.get(key)
            asset_objects = cost_centre.assets
            for asset in asset_objects:
                # Create df with rows containing current asset only
                filtered_asset_df = asset_support_hours_df[asset_support_hours_df["asset_description"] == asset.name]
                # Group df by model number and summarize by average support hour and count of that model
                asset_model_num_df = filtered_asset_df.set_index("model_number").groupby("model_number").agg(
                    {"avg_support_hour_per_model": "mean", "count_asset": "sum"})
                # Product portion of weighted average computation
                asset_model_num_df["weight"] = asset_model_num_df["avg_support_hour_per_model"] * (
                            asset_model_num_df["count_asset"] / asset_model_num_df["count_asset"].sum())
                # Compute weighted average support hours for current asset
                asset.avg_support_hours = asset_model_num_df["weight"].sum()

    def write_output_to_excel(self):

        dir_path = os.getcwd()
        budget_output_file_path = r"{dir_path}\model_outputs\budget_report_output.xlsx".format(dir_path=dir_path)

        workbook = xlsxwriter.Workbook(budget_output_file_path)

        # Formatting
        sheet_title = workbook.add_format({"bold": True})
        heading = workbook.add_format({"bold": True, "font_color": "white", "bg_color": "#244062", "border": True})
        cell_borders = workbook.add_format({"border": True})
        cell_borders_and_currency = workbook.add_format({"border": True, "num_format": "$#,##0.00"})
        currency = workbook.add_format({"num_format": "$#,##0.00"})
        decimal_hundredth = workbook.add_format({"num_format": "#,##0.00"})
        total_cost_to_service = workbook.add_format({"font_color": "white", "bg_color": "#6699CC"})

        # One worksheet per cost centre
        for key in self.cost_centres:
            cost_centre = self.cost_centres.get(key)
            worksheet = workbook.add_worksheet(cost_centre.name)

            # Title
            worksheet.write("A1",
                            "{name}: Annual Service Delivery Costs for Net New Equipment".format(name=cost_centre.name),
                            sheet_title)

            # OH output

            total_oh = cost_centre.regional_staff_oh + cost_centre.tech_staff_oh + cost_centre.non_labour_oh

            oh_headers = ["POHR", "Total OH", "Non-labour OH", "Tech Staff OH", "Regional Staff OH"]
            oh_values = [cost_centre.pohr,
                         total_oh,
                         cost_centre.non_labour_oh,
                         cost_centre.tech_staff_oh,
                         cost_centre.regional_staff_oh]

            oh_row = 2
            oh_header_col = 0
            oh_values_col = 1

            worksheet.write_column(oh_row, oh_header_col, oh_headers, heading)
            worksheet.write_column(oh_row, oh_values_col, oh_values, cell_borders_and_currency)

            # Asset output

            asset_output_headers = ["Health Authority",
                                    "Shop",
                                    "Site",
                                    "Asset Description",
                                    "Qty",
                                    "Annual Support Hours per Asset",
                                    "Maintenance Expense per Asset",
                                    "Cost to Service per Asset",
                                    "Total Cost to Service"]

            asset_row = 8
            asset_col = 0

            worksheet.write_row(asset_row, asset_col, asset_output_headers, heading)

            for asset in cost_centre.assets:
                asset_row += 1

                maintenance_exp = cost_centre.weighted_avg_tech_hourly_wage * asset.avg_support_hours
                per_asset_cost = cost_centre.pohr * asset.avg_support_hours + maintenance_exp

                row_data = [asset.health_auth,
                            asset.shop_code,
                            asset.site_code,
                            asset.name,
                            asset.qty,
                            asset.avg_support_hours,
                            maintenance_exp,
                            per_asset_cost,
                            asset.qty * per_asset_cost
                            ]

                worksheet.write_row(asset_row, asset_col, row_data, cell_borders)

                worksheet.set_column(0, 0, 17)  # Col A
                worksheet.set_column(1, 2, 15)  # Col B, C
                worksheet.set_column(3, 3, 70)  # Col D
                worksheet.set_column(4, 4, 7)  # Col E
                worksheet.set_column(5, 7, 30)  # Col F, G, H
                worksheet.set_column(8, 8, 24)  # Col I

                worksheet.conditional_format("G10:I1000", {"type": "no_blanks",
                                                           "format": currency})

                worksheet.conditional_format("F10:F1000", {"type": "no_blanks",
                                                           "format": decimal_hundredth})

                worksheet.conditional_format("I9:I1000", {"type": "no_blanks",
                                                          "format": total_cost_to_service})

        workbook.close()
