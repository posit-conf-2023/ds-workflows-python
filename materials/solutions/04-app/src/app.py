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
from .console import console

# Global data
RAW_MAP_DATA = load_map_data()
# ZIP_CODE_OPTIONS = {'': "All"} | {zip_code: zip_code for zip_code in RAW_MAP_DATA["zip_code"].to_list()}
ZIP_CODE_OPTIONS = {zip_code: zip_code for zip_code in RAW_MAP_DATA["zip_code"].to_list()}
# LICENSE_CODE_OPTIONS = {'': "All"} 
LICENSE_CODE_OPTIONS = {} 
for location_license_data in RAW_MAP_DATA["license_data"].tolist():
    for i in location_license_data:
        LICENSE_CODE_OPTIONS[i["license_code"]] = i["license_code"] + " - " + i["license_description"]


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
        
        # Get raw data
        df = RAW_MAP_DATA.copy()
        console.log(f"Original data has {df.shape[0]:,} rows.")
        
        # Apply filters
        if selected_zip_code:
            console.log(f"Filtering on Zip Code: {selected_zip_code}")
            df = df.loc[df["zip_code"] == selected_zip_code]
        
        if selected_license_code:
            console.log(f"Filtering on License Code: {selected_license_code}")
            df = df.loc[df["license_data"].apply(lambda x: any([i["license_code"] == selected_license_code for i in x])), :]
        
        if selected_name:
            console.log(f"Filtering on Doing Business as Name: {selected_name}")
            df = df.loc[df["doing_business_as_name"].str.contains(selected_name, case=False) | df["legal_name"].str.contains(selected_name, case=False)]

        console.log(f"Filtered data has {df.shape[0]:,} rows.")

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
    console.log("Rendering map...")
    console.log("Rendering map...")
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
        license_data = row["license_data"]
        marker = Marker(
            location=(lat, lon),
            title=name,
            draggable=False,
        )
        marker.popup = HTML(value="".join([
            f"<p><b>Name:</b> {name}</p>",
            f"<p><b>Licenses:</b></p>",
            f"""<ul>{" ".join([f'<li>{i["license_code"]} - {i["license_description"]}</li>' for i in license_data])}</ul>"""
        ]))
        markers.append(marker)
    marker_cluster = MarkerCluster(markers=markers)
    map.add_layer(marker_cluster)
    console.log("Rendering map complete")

    return map




def predict_likelihood_of_violation(df: pd.DataFrame) -> pd.Series:
    # TODO: call the vetiver API once Gagan has finished creating it.
    # Right now this is just a placeholder function...
    preds = np.random.rand(df.shape[0])
    return pd.Series(preds)


# Combine into a shiny app.
# Note that the variable must be "app".
app = App(app_ui, server)