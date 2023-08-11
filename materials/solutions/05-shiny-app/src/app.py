import datetime

import numpy as np
import pandas as pd
import shinyswatch
from ipyleaflet import (Map, Marker, MarkerCluster, ScaleControl)
from ipywidgets import HTML
from shiny import App, reactive, render, ui
import ibis
from shinywidgets import (output_widget, render_widget)

from .console import console
from .data import create_db_connection, get_zip_code_options, get_license_code_options



# Part 1: ui ----
app_ui = ui.page_navbar(
    shinyswatch.theme.zephyr(),
    ui.nav(
        "Map",
        ui.layout_sidebar(
            ui.panel_sidebar(
                ui.tags.h5("Filters"),
                ui.tags.hr(),
                ui.input_select(id="filter_zip_code", label="Zip Code", choices={'': 'All'}),
                ui.input_select(id="filter_license_code", label="License Type", choices={'': 'All'}),
                ui.input_select(id="filter_license_active", label="License Active", choices=["Yes", "No", "Show everything"]),
                ui.input_text(id="filter_name", label="Business Name", placeholder="Search for a business by name", value=None),
                ui.tags.br(),
                ui.tags.h5("Pagination"),
                ui.tags.hr(),
                ui.input_numeric(id="filter_number_of_rows", label="Number of Rows", value=100, step=50),
                ui.row(
                    ui.column(6, ui.output_ui("last_page_button_placeholder")),
                    ui.column(6, ui.output_ui("next_page_button_placeholder")),
                ),
            ),
            ui.panel_main(
                ui.navset_tab(
                    ui.nav("Table", ui.output_data_frame("business_table_output")),
                    ui.nav("Map", output_widget("leaflet_map")),
                )
            )
        )
    ),
    ui.nav(
        "About",
        ui.markdown("""
##### About this app

This app is used to help City of Chicago Food Inspectors identify which
establishments they should visit. The source code can be found here:
[github.com/posit-conf-2023/ds-workflows-python](https://github.com/posit-conf-2023/ds-workflows-python).
If you identify any issues please submit a bug report [here](https://github.com/posit-conf-2023/ds-workflows-python/issues/new/choose).
    """)
    ),
    title="City of Chicago Food Inspection",
    selected="Map",
    footer=ui.div(
        {"style": "background-color: rgb(248 249 250); margin-top: 20px;"},
        ui.div(
            {"style": "margin: 15px;"},
            "posit::conf(2023) // Data science Workflows with Python 🐍"
        )
    )
        
)

# Part 2: server ----
def server(input, output, session):
    
    # Create a database connection
    con = create_db_connection()
    
    # Track pagination
    page_number = reactive.Value(1)
    
    
    @reactive.Effect
    @reactive.event(input.next_page_button)
    def increment_pagination():
        page_number.set(page_number() + 1)
        console.log(f"Incrementing pagination (page={page_number()})...")


    @reactive.Effect
    @reactive.event(input.last_page_button)
    def decrement_pagination():
        page_number.set(page_number() - 1)
        console.log(f"Decrementing pagination (page={page_number()})....")


    @reactive.Effect
    @reactive.event(input.filter_zip_code, input.filter_license_code, input.filter_name)
    def reset_pagination():
        """
        Whenever a new filter is applied reset the pagination
        """
        page_number.set(1)
        console.log(f"Resetting pagination (page={page_number()})....")
    
    
    @output
    @render.ui
    def last_page_button_placeholder():
        if page_number() == 1:
            css_class = "disabled"
        else:
            css_class = ""
            
        return ui.input_action_button(
            "last_page_button", 
            f"Last Page ({page_number() - 1})", 
            width="100%",
            class_=css_class
        )


    @output
    @render.ui
    def next_page_button_placeholder():
        return ui.input_action_button(
            "next_page_button", 
            f"Next Page ({page_number() + 1})", 
            width="100%"
        )
    
    @reactive.Effect()
    def update_zip_code_options():
        ui.update_select(
            "filter_zip_code",
            choices=get_zip_code_options(con=con),
            selected=""
        )

    @reactive.Effect()
    def update_license_type_options():
        ui.update_select(
            "filter_license_code",
            choices=get_license_code_options(con=con),
            selected=""
        )

    
    @reactive.Calc
    def filter_data():        
        console.log("Filtering data...")
        
        # Get filter values
        selected_name = input.filter_name()
        selected_zip_code = input.filter_zip_code()
        selected_license_code = input.filter_license_code()
        selected_license_active = input.filter_license_active()
        
        # Create base query
        license_table = con.table("business_license_validated")
        
        # Only show business that are subject to food inspection
        inspections_table = con.table("food_inspection_validated")[["license_"]]
        license_table = license_table.inner_join(
            inspections_table, 
            license_table.license_id == inspections_table.license_
        )
        
        # Apply filters
        if selected_zip_code:
            console.log(f"Filtering on Zip Code: {selected_zip_code}")
            license_table = license_table[license_table.zip_code == selected_zip_code]
            
        if selected_license_code:
            console.log(f"Filtering on License Code: {selected_license_code}")
            license_table = license_table[license_table.license_code == selected_license_code]
            
        if selected_license_active == "Yes":
            console.log("Filtering on active licenses")
            license_table = license_table[license_table.expiration_date >= datetime.datetime.now()]
        elif selected_license_active == "No":
            console.log("Filtering on inactive licenses")
            license_table = license_table[license_table.expiration_date < datetime.datetime.now()]
 
        if selected_name:
            console.log(f"Filtering on Doing Business as Name: {selected_name}")
            license_table = license_table[license_table.doing_business_as_name.contains(selected_name.upper())]
            
        # Handle pagination
        page = page_number()
        limit = input.filter_number_of_rows()
        offset = (page - 1) * limit
        console.log(f"Pagination: page={page}, offset={offset}, limit={limit}")
        license_table = license_table.limit(limit, offset=offset)
        # console.log(ibis.show_sql(license_table))
        
        df = license_table.to_pandas()
        
        # Get predictions.
        df = predict_likelihood_of_violation(df)
        
        # Reorder columns
        first_cols = [
            "risk",
            "doing_business_as_name",
            "address",
            "license_id",
            "license_code",
            "license_description"
        ]
        
        col_order = first_cols + [i for i in df.columns if i not in first_cols]
        
        console.log("Filtering complete.")
        
        return df.loc[:, col_order]


    @output
    @render_widget
    def leaflet_map():
        """
        Create and register map.
        """   
        console.log("Rendering map...")
        map = Map(
            center=(41.881832,  -87.623177), 
            zoom=11, 
            scroll_wheel_zoom=True,
        )

        # Add a distance scale
        map.add_control(ScaleControl(position="bottomleft"))
        
        # Clean up the data so that there is only one location per row. One location
        # could have multiple licenses
        df = filter_data()
        
        # Only keep a subset of the columns that are relevant for mapping.
        map_cols = [
            "legal_name", 
            "doing_business_as_name",
            "address", 
            "zip_code",
            "latitude",
            "longitude",
            "license_id",
            "license_code",
            "license_description",
            "license_start_date",
            "expiration_date",
        ]
        
        # Apply the data cleaning steps.
        map_data = (
            df
            # .head(100_000)
            .loc[:, map_cols]
            .drop_duplicates()
            .reset_index(drop=True)
            .groupby([
                "legal_name", 
                "doing_business_as_name",
                "address", 
                "zip_code",
                "latitude",
                "longitude"
            ])
            .apply(lambda x: [{
                "license_id": row["license_id"], 
                "license_code": row["license_code"], 
                "license_description": row["license_description"],
                "license_start_date": row["license_start_date"],
                "expiration_date": row["expiration_date"],
            } for _, row in x.iterrows()])
            .reset_index()
            .rename({0: "license_data"}, axis=1)
        )

        # Add markers
        markers = []
        for _, row in map_data.iterrows():
            lat = row["latitude"]
            lon =  row["longitude"]
            name =  row["doing_business_as_name"]
            license_data = row["license_data"]
            
            marker = Marker(
                location=(lat, lon),
                title=name,
                draggable=False,
            )
            
            msg = HTML(f"""
                <p><b>Name:</b> {name}</p>
                <b>Licenses:</b>
                <ul>
                    {"".join([f"<li> {i['license_id']} - {i['license_code']} - {i['license_description']} </li>" for i in license_data])}
                </ul>
                """
            )
            marker.popup = msg
            markers.append(marker)
        
        marker_cluster = MarkerCluster(markers=markers)
        map.add_layer(marker_cluster)
        console.log("Rendering map complete")
        return map


    @output
    @render.data_frame
    def business_table_output():
        """
        Update the table under the map every time a change is made to one of the
        filters.
        """
        return filter_data()


def predict_likelihood_of_violation(df: pd.DataFrame) -> pd.DataFrame:
    # TODO: call the vetiver API once Gagan has finished creating it.
    # Right now this is just a placeholder function...
    out = df.copy()
    out["risk"] = np.random.rand(out.shape[0])
    return out


# Combine into a shiny app.
# Note that the variable must be "app".
app = App(app_ui, server)