#!/bin/python3
import json
import logging
import os
import folium
import pandas as pd

from census_app import here

output_directory = os.path.join(here, "templates", "output")
logging.basicConfig(level=logging.INFO)

##########


def get_shape_data(state: str):
    """
    Requests JSON data from public GitHub repo

    Keyword arguments:
    * state -- (str) US state abbreviation
    """

    pass


def build_map(api_data: pd.DataFrame, output_directory: str = output_directory) -> None:
    """
    Creates a Folium map with the results of our API call
    and saves in the output directory
    """

    pass
