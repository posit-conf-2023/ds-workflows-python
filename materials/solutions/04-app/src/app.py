from pathlib import Path
import pandas as pd
import shinyswatch
from ipywidgets import HTML
from ipyleaflet import Map, Marker, MarkerCluster, ScaleControl, Popup, CircleMarker
from pins import board_connect
from shiny import App, ui
from shinywidgets import output_widget, reactive_read, register_widget

# Part 1: ui ----
app_ui = ui.page_navbar(
    shinyswatch.theme.zephyr(),
    ui.nav(
        "Main",
        ui.layout_sidebar(
            ui.panel_sidebar(
                ui.tags.h5("Sidebar")
            ),
            ui.panel_main(
                ui.tags.h5("Map"),
                output_widget("map")
            )
        )
    ),
    title="City of Chicago Food Inspection",
)

# Part 2: server ----
def server(input, output, session):



    # Register widgets:
    map = create_map()
    register_widget("map", map)
    


def create_map():
    # Initialize and display when the session starts (1)
    map = Map(
        center=(41.881832,  -87.623177), 
        zoom=11, 
        scroll_wheel_zoom=True
    )

    # Add a distance scale
    map.add_control(ScaleControl(position="bottomleft"))

    # Add markers
    df = load_business_license_data().head(500)
    markers = []
    for index, row in df.iterrows():
        lat = row["latitude"]
        lon =  row["longitude"]
        name =  row["doing_business_as_name"]
        marker = CircleMarker(
            location=(lat, lon),
            title=name,
            draggable=False,
        )
        # marker.popup = HTML(value=name)
        from rich import inspect
        markers.append(marker)
    marker_cluster = MarkerCluster(markers=markers)
    inspect(markers[0])
    # map.add_layer(marker_cluster)
    # for marker in markers:
        # marker.popup = HTML(value="xxx")

    # Test marker
    marker = Marker(location=(41.881832,  -87.623177))
    # marker.popup = HTML(value="Hello world")
    map.add_layer(marker)


    return map

def load_business_license_data():
    cache_path = Path("~/Downloads/business-data.arrow").expanduser()
    if cache_path.is_file():
        print("Reading data from cache...")
        df = pd.read_feather(cache_path)
    else:
        print("Reading data from Connect...")
        board = board_connect(server_url='https://colorado.posit.co/rsc/')
        df = board.pin_read("sam.edwardes/chicago-business-license-data-validated")
        df = (
            df
            .loc[df["license_description"] == "Retail Food Establishment"]
            .loc[:, ["legal_name", "doing_business_as_name", "latitude", "longitude"]]
            .drop_duplicates()
            .reset_index(drop=True)
        )
        # Cache to disk...
        df.to_feather(cache_path)
    return df

# Combine into a shiny app.
# Note that the variable must be "app".
app = App(app_ui, server)