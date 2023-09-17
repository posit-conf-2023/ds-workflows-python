import os

import ibis
import pandas as pd
import vetiver
from loguru import logger
from shiny import App, reactive, render, req, ui

app_ui = ui.page_fluid(
    ui.layout_sidebar(
        ui.panel_sidebar(
            ui.tags.h5("Filters"),
            ui.input_text(
                "business_name_filter", 
                label="Business Name", 
                placeholder="Search for a business by name", 
                value=None
            ),
        ),
        ui.panel_main(
            ui.tags.h5("Inspection Summary"),
            ui.output_data_frame("output_business_listing_table"),
            ui.tags.h5("Selected Establishment"),
            ui.output_data_frame("output_prediction_table")

        )
    )
)


def server(input, output, session):
    
    # Create a connection to the database
    con = ibis.postgres.connect(
        user="posit",
        password=os.environ["CONF23_DB_PASSWORD"],
        host=os.environ["CONF23_DB_HOST"],
        port=5432,
        database="conf23_python"
    )

    @reactive.Calc
    def query_db_for_businesses():
        logger.info("query_db_for_businesses() - Starting")
        # Query the database to get business license details
        data = con.table("model_features")

        # Filter the data
        if input.business_name_filter():
            selected_business_name = input.business_name_filter().upper()
            print(f"Querying the data for '{selected_business_name}'")
            data = data.filter([data.dba_name.upper().contains(selected_business_name)])

        # Summarise the data by business
        data = data \
            .group_by("dba_name") \
            .agg(
                number_of_inspections=data.inspection_id.count(),
                number_of_violations=data.CUM_VIOLATIONS.max(),
                last_inspection=data.inspection_date.max()
            ) \
            .order_by(ibis.desc('number_of_violations'))

        # Finish the query and convert to a pandas dataframe
        data = data.limit(15).to_pandas()

        # Convert the data column to a string
        data = data.assign(last_inspection=data["last_inspection"].dt.strftime('%Y-%m-%d'))

        # Rename to a more human friendly format
        data = data.rename(columns={
            "dba_name": "Business Name",
            "number_of_inspections": "Number of Inspections",
            "number_of_violations": "Number of Violations",
            "last_inspection": "Last Inspection",
        })
        logger.info("query_db_for_businesses() - Complete")
        return data


    @output
    @render.data_frame
    def output_business_listing_table():
        logger.info("Updating business listing table")
        return render.DataGrid(
            query_db_for_businesses(),
            row_selection_mode="multiple",
            width="100%",
        )


    @reactive.Calc
    def get_predictions():
        logger.info("get_predictions() - Starting")

        # Get the selected rows from the business listing table
        selected_idx = list(req(input.output_business_listing_table_selected_rows()))
        logger.info(f"{selected_idx=}")

        # Get the data for selected rows
        selected_data = query_db_for_businesses().loc[selected_idx, :]
        logger.debug(f"{selected_data=}")

        # For each selected row, query the SQL database to get the features associated
        # with the business.
        frames = []
        for record in selected_data.to_dict(orient="records"):
            data = con.table("model_features")
            data = data.filter([
                data.dba_name == record["Business Name"],
                data.inspection_date == record["Last Inspection"]
            ])
            data = data[[
                "dba_name",
                "inspection_date",
                "BAKERY",
                "GROCERY_STORE",
                "RESTAURANT",
                "HIGH_RISK",
                "MEDIUM_RISK",
                "LOW_RISK",
                "CUM_VIOLATIONS",
            ]]
            data = data.limit(1).to_pandas()
            frames.append(data)
        
        # Call the vetiver endpoint to get the predictions.
        all_selected_businesses = pd.concat(frames)

        # TODO: update `endpoint` to point to the URL for the Vetiver model on Connect.
        # TIP: to get the URL, open https://connect.conf23workflows.training.posit.co/connect/#/apps/5ebb5685-bdcc-4951-b91e-dbf8ba64d9aa/access
        endpoint = ...
        
        # TODO: use `vetiver.predict()` to predict the result for all of the rows in
        # `all_selected_businesses`.
        predction_results = ...

        # Assign the prediction results to the dataframe.
        all_selected_businesses["Prediction Result"] = predction_results.iloc[:, 0].values
        
        # Tidy the data and create more human readable names.
        all_selected_businesses = all_selected_businesses.assign(
            last_inspection=data["inspection_date"].dt.strftime('%Y-%m-%d')
        ).rename(columns={
            "dba_name": "Business Name",
            "last_inspection": "Last Inspection"
        })[[
            "Business Name",
            "Last Inspection",
            "Prediction Result",
            "BAKERY",
            "GROCERY_STORE",
            "RESTAURANT",
            "HIGH_RISK",
            "MEDIUM_RISK",
            "LOW_RISK",
            "CUM_VIOLATIONS",
        ]]
        logger.debug(f"{all_selected_businesses=}")
        logger.info("get_predictions() - Complete")
        return all_selected_businesses


    @output
    @render.data_frame
    def output_prediction_table():
        logger.info("Updating prediction results table")
        return render.DataGrid(
            get_predictions(),
            row_selection_mode="none",
            width="100%",
        )
    

app = App(app_ui, server)