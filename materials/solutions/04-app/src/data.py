from pathlib import Path
import pandas as pd
from pins import board_connect

def load_map_data() -> pd.DataFrame:
    """
    Function to load the business license data.
    """
    # For development only. Temporarily store the data in the ~/Downloads directory
    # to make reloading the app faster.
    cache_path = Path("~/Downloads/business-data.arrow").expanduser()
    if cache_path.is_file():
        print("Reading data from cache...")
        df = pd.read_feather(cache_path)
    else:
        print("Reading data from Connect...")
        board = board_connect(server_url='https://colorado.posit.co/rsc/')
        df = board.pin_read("sam.edwardes/chicago-business-map-data")
        df = df.drop_duplicates().reset_index(drop=True)
        # Cache to disk...
        df.to_feather(cache_path)
    return df
