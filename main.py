import pandas as pd
from budgetreport import BudgetReport

# Show all df columns in run tool window
pd.set_option("display.expand_frame_repr", False)


def main():

    print("Importing data...")

    # Create BudgetReport object holding data needed to produce final output
    budget_report = BudgetReport()

    # Create list of Asset objects for which the user wants to budget
    assets = budget_report.create_asset_objects()

    print("Computing cost to service...")

    # Create CostCentre objects based on the Asset objects above
    budget_report.create_cost_centre_objects(assets, budget_report)

    # Compute asset support hours
    budget_report.compute_asset_support_hours()

    print("Writing output to Excel...")

    # Write output to Excel
    budget_report.write_output_to_excel()

    input("Budget report output successfully generated. Press 'Enter' to close this window.")


if __name__ == "__main__":

    main()

