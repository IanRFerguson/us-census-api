#!/bin/python3
import os
import glob
import pandas as pd

from census_app import here

#########


def parse_filename(x: str) -> list:
    """
    Isolate the components of the filename by convention

    Keyword arguments:
    x -- (str) Pathlike string, e.g., test/example/state-ny.html
    """

    # If full filepath is handed off we'll isolate the filename
    if "/" in x:
        x = x.split("/")[-1].strip()

    x = x.replace(".html", "")

    ###

    # Split into segments (_) and unique IDs (-)
    state_name = x.split("_")[0].split("-")[1]

    temp_var = x.split("_")[1].split("-")[1]

    if temp_var == "totalPopulation":
        var = "Total Population"

    elif temp_var == "popPctChange":
        var = "Population Percentage Change"

    timestamp = x.split("_")[2].split("timestamp-")[1].replace("-", "/")

    return [state_name, var, timestamp]


def get_all_results(output_files: list = None) -> pd.DataFrame:
    """
    Translate all files into a tidy DataFrame
    """

    if output_files is None:
        output_files = get_all_output_paths()

    ###

    container = []

    for file in output_files:
        components = parse_filename(x=file)

        components.extend([file])

        container.append(components)

    return pd.DataFrame(
        container,
        columns=["State Name", "API Request Type", "Requested At", "Link to Map"],
    )


def get_all_output_paths() -> list:
    """
    Get list out output files
    """

    output_files = os.path.join(here, "static", "output", "**/*.html")

    return [
        x.split("/")[-1].replace(".html", "")
        for x in glob.glob(output_files, recursive=True)
    ]
