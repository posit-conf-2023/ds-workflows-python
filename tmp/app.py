from shiny import ui, render, App
import pandas as pd

app_ui = ui.page_fluid(
    ui.layout_sidebar(
        ui.panel_sidebar(
            ui.tags.h5("Filters"),
            ui.input_select(
                "selected_color", 
                label="Color",
                choices=["red", "blue", "green", "yellow"]
            )
        ),
        ui.panel_main(
            ui.tags.h5("Raw Data"),
            ui.output_data_frame("raw_data"),
            ui.tags.h5("Filtered Data"),
            ui.output_data_frame("filtered_data")

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

    @output
    @render.data_frame
    def filtered_data():
        return data.loc[data["color"] == input.selected_color(), :]
    

app = App(app_ui, server)