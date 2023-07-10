from pathlib import Path
from textwrap import dedent
import pandas as pd
import numpy as np
import shinyswatch
from ipywidgets import HTML
from ipyleaflet import Map, Marker, MarkerCluster, ScaleControl, Popup, CircleMarker
from pins import board_connect
from shiny import App, ui, render, reactive
from shinywidgets import output_widget, reactive_read, register_widget, render_widget
from rich.console import Console

from .data import load_map_data

console = Console()

# Global data
RAW_MAP_DATA = load_map_data()
ZIP_CODE_OPTIONS = {'': "All"} | {zip_code: zip_code for zip_code in RAW_MAP_DATA["zip_code"].to_list()}
LICENSE_CODE_OPTIONS = {'': "All"} | {row["license_code"]: row["license_code"] + " - " + row["license_description"] for idx, row in RAW_MAP_DATA.iterrows()}

# Part 1: ui ----
app_ui = ui.page_navbar(
    shinyswatch.theme.zephyr(),
    ui.nav(
        "Map",
        ui.layout_sidebar(
            ui.panel_sidebar(
                ui.tags.h5("Filters"),
                ui.input_select(id="filter_zip_code", label="Zip Code", choices=ZIP_CODE_OPTIONS),
                ui.input_select(id="filter_license_code", label="License Type", choices=LICENSE_CODE_OPTIONS),
                ui.input_text(id="filter_name", label="Business Name", placeholder="Search for a business by name", value=None),
            ),
            ui.panel_main(
                ui.tags.h5("Map"),
                output_widget("leaflet_map"),
                ui.tags.h5("Businesses"),
                ui.output_data_frame("business_table_output"),
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
        # ui.p("posit::conf(2023) // Data science Workflows with Python 🐍")
    )
        
)

# Part 2: server ----
def server(input, output, session): 

    @reactive.Calc
    def filter_data():
        console.log("Filtering data...")
        # Get filter values
        selected_name = input.filter_name()
        selected_zip_code = input.filter_zip_code()
        selected_license_code = input.filter_license_code()
        console.log(locals())
        
        # Get raw data
        df = RAW_MAP_DATA.copy()
        
        # Apply filters
        if selected_name:
            console.log(f"Filtering on Doing Business as Name: {selected_name}")
            df = df.loc[df["doing_business_as_name"].str.contains(selected_name, case=False) | df["legal_name"].str.contains(selected_name, case=False)]
        
        if selected_zip_code:
            console.log(f"Filtering on Zip Code: {selected_zip_code}")
            df = df.loc[df["zip_code"] == selected_zip_code]

        if selected_license_code:
            console.log(f"Filtering on License Code: {selected_license_code}")
            df = df.loc[df["license_code"] == selected_license_code]

        return df


    @output
    @render_widget
    def leaflet_map():
        """
        Create and register map.
        """
        map = create_map(df=filter_data())
        return map


    @output
    @render.data_frame
    def business_table_output():
        """
        Update the table under the map every time a change is made to one of the
        filters.
        """
        return filter_data()
    
    # @output
    # @render.w
    

def create_map(df: pd.DataFrame) -> Map:
    """
    Function to create the initial ipyleaflet Map object.
    """
    # Initialize and display when the session starts
    map = Map(
        center=(41.881832,  -87.623177), 
        zoom=11, 
        scroll_wheel_zoom=True
    )

    # Add a distance scale
    map.add_control(ScaleControl(position="bottomleft"))

    # Add markers
    markers = []
    for index, row in df.iterrows():
        lat = row["latitude"]
        lon =  row["longitude"]
        name =  row["doing_business_as_name"]
        license_id = row["license_id"]
        license_code = row["license_code"]
        license_description = row["license_description"]
        marker = Marker(
            location=(lat, lon),
            title=name,
            draggable=False,
        )
        marker.popup = HTML(value="".join([
            f"<p><b>Name:</b> {name}</p>",
            f"<p><b>License ID</b>: {license_id}</p>",
            f"<p><b>License Code/Description</b>: {license_code} - {license_description}</p>",
        ]))
        markers.append(marker)
    marker_cluster = MarkerCluster(markers=markers)
    map.add_layer(marker_cluster)

    return map




def predict_likelihood_of_violation(df: pd.DataFrame) -> pd.Series:
    # TODO: call the vetiver API once Gagan has finished creating it.
    # Right now this is just a placeholder function...
    preds = np.random.rand(df.shape[0])
    return pd.Series(preds)


# Combine into a shiny app.
# Note that the variable must be "app".
app = App(app_ui, server)