from shiny import ui, render, App
import pandas as pd

app_ui = ui.page_fluid(
    ui.layout_sidebar(
        ui.panel_sidebar(
            ui.tags.h5("Filters"),
            # TODO: add dropdown filter to filter based on colour
            # SAM TODO: add docs to the dropdown
        ),
        ui.panel_main(
            ui.tags.h5("Raw Data!!!!!"),
            ui.output_data_frame("raw_data"),
            ui.tags.h5("Filtered Data")
            # TODO: Display the filtered data in a table,

        )
    )
)

def server(input, output, session):

    data = pd.DataFrame({
        "color": ["red", "blue", "red", "green", "yellow", "green"],
        "x": [1, 4, 10, 99, 3, 26]
    })

    @output
    @render.data_frame
    def raw_data():
        return data

    # TODO: write a function that filters and renders the filtered data.
    

app = App(app_ui, server)