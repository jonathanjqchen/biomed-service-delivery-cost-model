import pandas as pd
import xlsxwriter
import os
from asset import Asset
from costcentre import CostCentre
from regionalstaff import RegionalStaff

pd.set_option("display.expand_frame_repr", False)


"""
########################################################################################################################
##################################### MODULE SCOPE FUNCTIONS BELOW #####################################################
########################################################################################################################
"""


def read_sites_cost_centres_reference():
    """
    Pulls data from cost_centres_and_sites_reference.xlsx into a dictionary so that we can find the corresponding cost
    centres for a given site

    :return: Dictionary with key: "site" and value: ["clinical cost centre", "renal cost centre", "imaging cost centre"]
    """

    # File path to cost_centres_and_sites_reference.xlsx
    sites_cc_file_path = "model_inputs/cost_centres_and_sites/cost_centres_and_sites_reference.xlsx"

    # Read into df the "site", "clinical_cost_centre", "renal_cost_centre", "imaging_cost_centre" fields
    sites_cc_df = pd.read_excel(sites_cc_file_path,
                                sheet_name="Sites",
                                usecols=["site_code",
                                         "clinical_cost_centre",
                                         "renal_cost_centre",
                                         "imaging_cost_centre"])

    # Convert dataframe into dictionary
    sites_cc_dict = sites_cc_df.set_index("site_code").T.to_dict("list")

    return sites_cc_dict


def read_cc_responsibility_reference():
    """
    Parses "Cost Centres" sheet in cost_centres_and_sites_reference.xlsx and creates a nested dictionary that gives us a
    list of cost centres for each HA-function combination, where "function" refers to the type of asset (i.e. clinical,
    renal, imaging).

    :return: Nested dictionary in the form {"HA1": {"function1": ["cost_centre1, cost_centre2"]
                                                    "function2": ["cost_centre1"]
                                                    "function3": ["cost_centre1, cost_centre2, cost_centre3"]
                                            "HA2": ... }
    """

    # File path to cost_centres_and_sites_reference.xlsx
    sites_cc_file_path = "model_inputs/cost_centres_and_sites/cost_centres_and_sites_reference.xlsx"

    # Read into df the "cost_centre_name", "health_authority", "function" fields
    cc_responsibility_df = pd.read_excel(sites_cc_file_path,
                                         sheet_name="Cost Centres",
                                         usecols=["cost_centre_name",
                                                  "health_authority",
                                                  "function"])

    # Get unique HA and function values from cc_responsibility_df and store in numpy array
    health_auth = cc_responsibility_df["health_authority"].unique()
    function = cc_responsibility_df["function"].unique()

    # Initialize a partially filled nested dictionary
    cc_responsibility_dict = {health_auth[0]: {function[0]: [], function[1]: [], function[2]: []},
                              health_auth[1]: {function[0]: [], function[1]: [], function[2]: []},
                              health_auth[2]: {function[0]: [], function[1]: [], function[2]: []},
                              health_auth[3]: {function[0]: [], function[1]: [], function[2]: []}}

    # Populate cc_responsibility_dict with the cost centres for each HA-function combination
    for ha in health_auth:
        for func in function:
            temp_df = cc_responsibility_df.loc[(cc_responsibility_df["health_authority"] == ha) &
                                               (cc_responsibility_df["function"] == func)]
            temp_list = temp_df["cost_centre_name"].to_list()
            cc_responsibility_dict[ha][func] = temp_list

    return cc_responsibility_dict


"""
########################################################################################################################
######################################## BUDGETREPORT CLASS BELOW ######################################################
########################################################################################################################
"""


class BudgetReport:
    """
    This class handles all data and behaviour associated with the budget report input and budget report output Excel
    files.
    """

    # Path to budget report input file
    budget_report_input_file_path = "model_inputs/budget_report_input.xlsx"
    # Dict with sites and their corresponding cost centres
    sites_cost_centre_dict = read_sites_cost_centres_reference()
    # Nested dict with HA, asset function, and their corresponding cost centres
    cost_centre_responsibility_dict = read_cc_responsibility_reference()

    def __init__(self):
        """
        Initialize instance variables.
        """

        # Dictionary with key: "cost centre name" and value: CostCentre object
        self.cost_centres = {}
        # Current row to which we are writing in the "Summary" worksheet in budget_report_output.xlsx
        self.summary_row = 2

    def create_asset_objects(self):
        """
        Pulls asset details inputted by user into budget_report_input.xlsx and creates an Asset object for each row of
        asset details entered.

        :return: List of Asset objects that correspond to input entered by user into budget_report_input.xlsx
        """

        # Read asset details into dataframe
        df = pd.read_excel(self.budget_report_input_file_path, sheet_name="User Input")

        # Convert dataframe into dictionary
        #   Key: "df index"
        #   Value: ["model_num", "asset_description", "quantity", "health_auth", "site_code", "shop_code"]
        assets_dict = df.T.to_dict("list")

        # Iterate through assets_dict, create Asset object for each value, and append to assets list
        assets = []

        for asset, details in assets_dict.items():
            assets.append(Asset(details[0],  # model_num
                                details[1],  # asset_description
                                details[2],  # quantity
                                details[3],  # health_auth
                                details[4],  # site_code
                                details[5],  # shop_code
                                self.sites_cost_centre_dict))

        return assets

    def create_cost_centre_objects(self, assets, budget_report):
        """
        Creates CostCentre objects associated with the asset inputs to the model. CostCentre objects are added to
        BudgetReport's cost_centres dictionary instance variable. The dictionary takes the form:

                Key: "Cost centre name"
                Value: CostCentre object

        :param assets: List of Asset objects
        :param budget_report: BudgetReport object
        :return: None
        """

        # Iterate through each asset inputted by the user
        for asset in assets:
            '''
            If the asset's cost centre already exists in the cost_centres dictionary, append the asset to the CostCentre
            object's list of assets.
            
            If the asset's cost centre doesn't already exist in the cost_centres dictionary, create the CostCentre
            object and then add it to the dictionary (asset is added to the CostCentre object by default in __init__())
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
        """
        Reads in data on regional staff from "Regional Staff" worksheet in staff_salaries.xlsx and uses data to create
        RegionalStaff objects.

        :return: List of RegionalStaff objects
        """

        # File path to regional_staff_salaries.xlsx
        regional_staff_salaries_file_path = "model_inputs/labour_reports/staff_salaries.xlsx"

        # Read regional staff data into dataframe
        regional_staff_df = pd.read_excel(regional_staff_salaries_file_path, sheet_name="Regional Staff")

        # Convert dataframe into dictionary with key: "name", and values: ["all other fields"]
        regional_staff_dict = regional_staff_df.set_index("name").T.to_dict("list")

        regional_staff = []

        # Iterate through dictionary of regional staff details and create RegionalStaff objects
        for staff_name, staff_details in regional_staff_dict.items():
            regional_staff.append(RegionalStaff(staff_name,        # Staff name
                                                staff_details[0],  # Staff title (i.e. Director, engineer, etc.)
                                                staff_details[2],  # Min salary
                                                staff_details[3],  # Max salary
                                                staff_details[4],  # Clinical and renal responsibilities
                                                staff_details[5],  # Imaging responsibilities
                                                self.cost_centre_responsibility_dict)
                                  )

        return regional_staff

    def compute_asset_support_hours(self):
        """
        Iterates through each asset inputted by the user and reads from "asset_support_hours_reference.xlsx" the average
        work order hours spent on each model of an asset and stores this float in the asset's avg_support_hours field.

        :return: None
        """

        # File path to asset_support_hours_reference.xlsx
        asset_support_hours_file_path = "model_inputs/wo_reports/asset_support_hours_reference.xlsx"
        # Read data into df and index the relevant columns
        asset_support_hours_df = pd.read_excel(asset_support_hours_file_path)
        asset_support_hours_df = asset_support_hours_df[["asset_description",
                                                         "model_number",
                                                         "avg_support_hour_per_model",
                                                         "count_asset"]]

        # Loop through all the assets that were inputted by the user
        for key in self.cost_centres:
            cost_centre = self.cost_centres.get(key)
            asset_objects = cost_centre.assets
            for asset in asset_objects:
                # Filter asset_support_hours_df with rows that only contain model # of current asset
                filtered_model_df = asset_support_hours_df[asset_support_hours_df["model_number"] == asset.model_num]

                # If model number exists in the df, compute average support hours for current model
                if not filtered_model_df.empty:
                    asset.avg_support_hours = filtered_model_df["avg_support_hour_per_model"].mean()

                # If model number doesn't exist in df, compute weighted average support hours for current asset
                else:
                    # Create df with rows that only contain the asset_description of current asset
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
        """
        Write cost model output to an excel file in /model_outputs/budget_report_output.xlsx. Run the model to see
        sample output.

        Read the docs for more information on how to use xlsxwriter: https://xlsxwriter.readthedocs.io/

        :return: None
        """

        dir_path = os.getcwd()
        budget_output_file_path = r"{dir_path}\model_outputs\budget_report_output.xlsx".format(dir_path=dir_path)
        workbook = xlsxwriter.Workbook(budget_output_file_path)

        # Formatting
        title = workbook.add_format({"bold": True})
        heading = workbook.add_format({"bold": True, "font_color": "white", "bg_color": "#244062", "border": True})
        cell_borders = workbook.add_format({"border": True})
        cell_borders_and_currency = workbook.add_format({"border": True, "num_format": "$#,##0.00"})
        currency = workbook.add_format({"num_format": "$#,##0.00"})
        decimal_hundredth = workbook.add_format({"num_format": "#,##0.00"})
        total_cost_to_service = workbook.add_format({"font_color": "white",
                                                     "bg_color": "#538dd5",
                                                     "border": True,
                                                     "bold": True})

        # Add summary worksheet that summarizes the budget outputs for each cost centre
        summary_sheet = workbook.add_worksheet("Summary")
        summary_sheet.set_column(0, 1, 20)  # Col A, B

        # Loop through each cost centre for which we are budgeting
        for key in self.cost_centres:

            # Call helper function to write:
            #       - OH: Total OH, non-labour OH, tech staff OH, regional staff OH
            #       - Rates: POHR, tech wage per hour
            self.write_cost_centre_output(cell_borders, cell_borders_and_currency, currency, decimal_hundredth, heading,
                                          key, title, total_cost_to_service, workbook, summary_sheet)

        # Write total cost for all cost centres to "Summary" worksheet
        summary_sheet.write(0, 0, "Total Cost", total_cost_to_service)
        summary_sheet.write_formula(0,
                                    1,
                                    "=SUM(B3:B{last_row})".format(last_row=self.summary_row),
                                    cell_borders_and_currency)

        # Output will only be written if workbook.close() is called
        workbook.close()

    def write_cost_centre_output(self, cell_borders, cell_borders_and_currency, currency, decimal_hundredth, heading,
                                 key, title, total_cost_to_service, workbook, summary_sheet):
        """
        Writes title, OH, and rates output to a worksheet in budget_report_output.xlsx for the given cost_centre. See
        "# Formatting" in BudgetReport.write_output_to_excel() for more information on formatting variables passed as
        arguments to this method.

        :param cell_borders: Formatting variable
        :param cell_borders_and_currency: Formatting variable
        :param currency: Formatting variable
        :param decimal_hundredth: Formatting variable
        :param heading: Formatting variable
        :param key: Cost centre name as a string
        :param title: Formatting variable
        :param total_cost_to_service: Formatting variable
        :param workbook: xlsxwriter object representing budget_report_output.xlsx
        :param summary_sheet: Summary worksheet that summarizes the budget outputs for each cost centre
        :return: None
        """

        # Create a new worksheet for each cost centre
        cost_centre = self.cost_centres.get(key)
        worksheet = workbook.add_worksheet(cost_centre.name)

        # Title
        worksheet.write("A1",
                        "{name}: Annual Service Delivery Costs for Net New Equipment".format(name=cost_centre.name),
                        title)
        # OH output
        worksheet.write("A3", "OH Information", title)
        total_oh = cost_centre.regional_staff_oh + cost_centre.tech_staff_oh + cost_centre.non_labour_oh
        oh_headers = ["Total OH", "Non-labour OH", "Tech Staff OH", "Regional Staff OH"]
        oh_values = [total_oh,
                     cost_centre.non_labour_oh,
                     cost_centre.tech_staff_oh,
                     cost_centre.regional_staff_oh]
        title_row = 3
        title_col = 0
        values_col = 1
        worksheet.write_column(title_row, title_col, oh_headers, heading)
        worksheet.write_column(title_row, values_col, oh_values, cell_borders_and_currency)

        # Rates output
        worksheet.write("A9", "Rates", title)
        rates_headers = ["POHR", "Tech $/hr"]
        rates_values = [cost_centre.pohr,
                        cost_centre.weighted_avg_tech_hourly_wage]
        title_row = 9
        worksheet.write_column(title_row, title_col, rates_headers, heading)
        worksheet.write_column(title_row, values_col, rates_values, cell_borders_and_currency)

        # Call helper functions to write asset output (support hours per asset, cost to service, etc.) because the
        # output is slightly different for imaging vs. clinical and renal assets
        if cost_centre.function == "imaging":
            self.write_imag_asset_output(cell_borders, cost_centre, currency, decimal_hundredth, heading,
                                         total_cost_to_service, worksheet, title, cell_borders_and_currency,
                                         summary_sheet)
        else:
            self.write_asset_output(cell_borders, cost_centre, currency, decimal_hundredth, heading,
                                    total_cost_to_service, worksheet, title, cell_borders_and_currency, summary_sheet)

    def write_imag_asset_output(self, cell_borders, cost_centre, currency, decimal_hundredth, heading,
                                total_cost_to_service, worksheet, title, cell_borders_and_currency, summary_sheet):
        """
        Write asset output for imaging cost centres.

        :param cell_borders: Formatting variable
        :param cost_centre: CostCentre object for which we are writing output
        :param currency: Formatting variable
        :param decimal_hundredth: Formatting variable
        :param heading: Formatting variable
        :param total_cost_to_service: Formatting variable
        :param worksheet: xlsx object representing current worksheet to which we are writing
        :param title: Formatting variable
        :param cell_borders_and_currency: Formatting variable
        :param summary_sheet: Summary worksheet that summarizes the budget outputs for each cost centre
        :return: None
        """

        # Asset output headings
        asset_output_headers = ["Health Authority",
                                "Shop",
                                "Site",
                                "Model Number",
                                "Asset Description",
                                "Qty",
                                "Annual Support Hours per Asset",
                                "OH Cost per Asset",
                                "WO Cost per Asset",
                                "Service Contract Cost per Asset",
                                "Cost to Service per Asset",
                                "Total Cost to Service"]

        asset_row = 15
        asset_col = 0

        worksheet.write_row(asset_row, asset_col, asset_output_headers, heading)

        # Asset output details
        for asset in cost_centre.assets:

            # Start at new row
            asset_row += 1

            # Store asset details in a list
            row_data = [asset.health_auth,
                        asset.shop_code,
                        asset.site_code,
                        asset.model_num,
                        asset.name,
                        asset.qty,
                        asset.avg_support_hours
                        ]

            # Write asset details from row_data list to the row
            worksheet.write_row(asset_row, asset_col, row_data, cell_borders)

            # Set column widths
            worksheet.set_column(0, 0, 17)    # Col A
            worksheet.set_column(1, 3, 15)    # Col B, C, D
            worksheet.set_column(4, 4, 70)    # Col E
            worksheet.set_column(5, 5, 7)     # Col F
            worksheet.set_column(6, 6, 30)    # Col G
            worksheet.set_column(7, 8, 23)    # Col H, I
            worksheet.set_column(9, 9, 30)    # Col J
            worksheet.set_column(10, 10, 23)  # Col K
            worksheet.set_column(11, 11, 20)  # Col L

            # Formatting for specific columns
            worksheet.conditional_format("H10:L1000000", {"type": "no_blanks",
                                                          "format": currency})

            worksheet.conditional_format("G10:G1000000", {"type": "no_blanks",
                                                          "format": decimal_hundredth})

            worksheet.conditional_format("L9:L1000000", {"type": "no_blanks",
                                                         "format": total_cost_to_service})

        '''
        Write formulas in cells for:
           - OH Cost Per Asset
           - Direct Cost Per Asset
           - Service Contract Cost Per Asset
           - Cost to Service Per Asset
           - Total Cost to Service
        
        for loop explanation:
            - Start at row 15 because it is the first row after the headers
            - asset_row is the last row that was written to, but we need to add 2 to it because it is based on 
              zero-based indexing (+1) and second arg in Python range() function is not inclusive (+1) 
        '''

        for row in range(17, asset_row + 2):
            # Cell containing WO hours for current row
            wo_hours_cell = "G" + str(row)
            # Formula for OH Cost Per Asset = POHR (B10) * WO hours
            worksheet.write_formula(row - 1, 7, "=B10*{wo_hours}".format(wo_hours=wo_hours_cell), cell_borders)
            # Formula for Direct Cost Per Asset = Tech $/hr (B11) * WO hours
            worksheet.write_formula(row - 1, 8, "=B11*{wo_hours}".format(wo_hours=wo_hours_cell), cell_borders)
            # Write 0 as dummy value for each row under Service Contract Cost Per Asset
            worksheet.write(row - 1, 9, 0, cell_borders)

            # Formula for Cost to Service Per Asset = OH Costs + Direct Costs + Service Contract Costs
            oh_cost_cell = "H" + str(row)
            direct_cost_cell = "I" + str(row)
            service_contract_cell = "J" + str(row)
            worksheet.write_formula(row - 1,
                                    10,
                                    "=SUM({oh}, {wo}, {contract})".format(oh=oh_cost_cell,
                                                                          wo=direct_cost_cell,
                                                                          contract=service_contract_cell),
                                    cell_borders)

            # Formula for Total Cost to Service = Qty * Cost to Service Per Asset
            qty_cell = "F" + str(row)
            per_asset_cost = "K" + str(row)
            worksheet.write_formula(row - 1, 11, "{unit_cost}*{qty}".format(unit_cost=per_asset_cost, qty=qty_cell),
                                    cell_borders)

        # Sum up total costs and write to cell B14
        worksheet.write("A13", "Total", title)
        worksheet.write(13, 0, "Net Cost to Service", total_cost_to_service)
        last_row_cell = "L{row}".format(row=asset_row+1)
        worksheet.write_formula(13,
                                1,
                                "=SUM({start}:{end})".format(start="L17", end=last_row_cell),
                                cell_borders_and_currency)

        # Write total cost for the cost centre to the "Summary" worksheet
        summary_sheet.write(self.summary_row, 0, cost_centre.name, heading)
        total_cost_reference = "{cc_name}!B14".format(cc_name=cost_centre.name)
        summary_sheet.write_formula(self.summary_row,
                                    1,
                                    "={formula}".format(formula=total_cost_reference),
                                    cell_borders_and_currency)
        self.summary_row += 1

    def write_asset_output(self, cell_borders, cost_centre, currency, decimal_hundredth, heading, total_cost_to_service,
                           worksheet, title, cell_borders_and_currency, summary_sheet):
        """
        Write asset output for clinical/renal cost centres.

        :param cell_borders: Formatting variable
        :param cost_centre: CostCentre object for which we are writing output
        :param currency: Formatting variable
        :param decimal_hundredth: Formatting variable
        :param heading: Formatting variable
        :param total_cost_to_service: Formatting variable
        :param worksheet: xlsx object representing current worksheet to which we are writing
        :param title: Formatting variable
        :param cell_borders_and_currency: Formatting variable
        :param summary_sheet: Summary worksheet that summarizes the budget outputs for each cost centre
        :return: None
        """

        # Asset output headings
        asset_output_headers = ["Health Authority",
                                "Shop",
                                "Site",
                                "Model Number",
                                "Asset Description",
                                "Qty",
                                "Annual Support Hours per Asset",
                                "OH Cost per Asset",
                                "Direct Cost per Asset",
                                "Cost to Service per Asset",
                                "Total Cost to Service"]
        asset_row = 15
        asset_col = 0
        worksheet.write_row(asset_row, asset_col, asset_output_headers, heading)

        # Asset output details
        for asset in cost_centre.assets:

            # Start at new row
            asset_row += 1

            # Store asset details in a list
            row_data = [asset.health_auth,
                        asset.shop_code,
                        asset.site_code,
                        asset.model_num,
                        asset.name,
                        asset.qty,
                        asset.avg_support_hours
                        ]

            # Write asset details from row_data list to the row
            worksheet.write_row(asset_row, asset_col, row_data, cell_borders)

            # Set column widths
            worksheet.set_column(0, 0, 17)    # Col A
            worksheet.set_column(1, 3, 15)    # Col B, C, D
            worksheet.set_column(4, 4, 70)    # Col E
            worksheet.set_column(5, 5, 7)     # Col F
            worksheet.set_column(6, 6, 30)    # Col G
            worksheet.set_column(7, 9, 23)    # Col H, I, J
            worksheet.set_column(10, 10, 20)  # Col K

            # Formatting for specific columns
            worksheet.conditional_format("H10:K1000000", {"type": "no_blanks",
                                                          "format": currency})

            worksheet.conditional_format("G10:G1000000", {"type": "no_blanks",
                                                          "format": decimal_hundredth})

            worksheet.conditional_format("K9:K1000000", {"type": "no_blanks",
                                                         "format": total_cost_to_service})

        '''
               Write formulas in cells for:
                  - OH Cost Per Asset
                  - Direct Cost Per Asset
                  - Cost to Service Per Asset
                  - Total Cost to Service

               for loop explanation:
                   - Start at row 15 because it is the first row after the headers
                   - asset_row is the last row that was written to, but we need to add 2 to it because it is based on 
                     zero-based indexing (+1) and second arg in Python range() function is not inclusive (+1) 
               '''

        for row in range(17, asset_row + 2):
            # Cell containing WO hours for current row
            wo_hours_cell = "G" + str(row)
            # Formula for OH Cost Per Asset = POHR (B10) * WO hours
            worksheet.write_formula(row - 1, 7, "=B10*{wo_hours}".format(wo_hours=wo_hours_cell), cell_borders)
            # Formula for Direct Cost Per Asset = Tech $/hr (B11) * WO hours
            worksheet.write_formula(row - 1, 8, "=B11*{wo_hours}".format(wo_hours=wo_hours_cell), cell_borders)

            # Formula for Cost to Service Per Asset = OH Costs + Direct Costs
            oh_cost_cell = "H" + str(row)
            direct_cost_cell = "I" + str(row)
            worksheet.write_formula(row - 1,
                                    9,
                                    "=SUM({oh}, {direct})".format(oh=oh_cost_cell, direct=direct_cost_cell),
                                    cell_borders)

            # Formula for Total Cost to Service = Qty * Cost to Service Per Asset
            qty_cell = "F" + str(row)
            per_asset_cost = "J" + str(row)
            worksheet.write_formula(row - 1, 10, "{unit_cost}*{qty}".format(unit_cost=per_asset_cost, qty=qty_cell),
                                    cell_borders)

        # Sum up total costs and write to cell B14
        worksheet.write("A13", "Total", title)
        worksheet.write(13, 0, "Net Cost to Service", total_cost_to_service)
        last_row_cell = "K{row}".format(row=asset_row+1)
        worksheet.write_formula(13,
                                1,
                                "=SUM({start}:{end})".format(start="K17", end=last_row_cell),
                                cell_borders_and_currency)

        # Write total cost for the cost centre to the "Summary" worksheet
        summary_sheet.write(self.summary_row, 0, cost_centre.name, heading)
        total_cost_reference = "{cc_name}!B14".format(cc_name=cost_centre.name)
        summary_sheet.write_formula(self.summary_row,
                                    1,
                                    "={formula}".format(formula=total_cost_reference),
                                    cell_borders_and_currency)
        self.summary_row += 1
