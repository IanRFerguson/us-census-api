#!/bin/python3
import os
import requests
import us
import logging
import yaml
from dotenv import load_dotenv
import pandas as pd

from census_app import here, data_path

yaml_path = os.path.join(data_path, "query_dictionary.yaml")
logging.basicConfig(level=logging.INFO)
load_dotenv(os.path.join(here, ".env"))

census_key = os.environ.get("CENSUS_API_KEY")

##########


def generate_api_call(state: str, variable: str):
    """
    This helper reads in the appropriate YAML key (by variable name)
    and formats it with the appropriate state value

    Keyword arguments:
    * state -- (str) US state name
    * variable -- (str) Corresponds to the key of the yaml file
    """

    # Read YAML with base API calls
    with open(yaml_path) as incoming:
        call = yaml.safe_load(incoming)[variable]

    # Convert state name to FIPS
    fips = state_name_to_fips(state_name=state)

    # Impute FIPS code and census key into API call
    call = call.format(fips, census_key)

    return call


def state_name_to_fips(state_name: str) -> str:
    """
    Converts state name to FIPS code (e.g., California => "06")

    Keyword arguments:
    * state_name -- (str) Longform name of US state (e.g., "New York")

    Returns
    * US state FIPS code
    """

    # Use US module to lookup State object
    state_object = us.states.lookup(state_name)

    return state_object.fips


def get_api_data(state_name: str, variable: str) -> pd.DataFrame:
    """
    This helper performs the following operations:
    * Generate Census API call
    * Calls and validates response
    * Reads as Pandas DataFrame and formats appropriately

    Keyword arguments:
    * state_name -- (str) Longform state name (e.g., California)
    * variable -- (str) Variable to query
    """

    # Format API call
    api_call = generate_api_call(state=state_name, variable=variable)

    # Send request to Census API and validate
    response = requests.get(api_call)

    if response.status_code != 200:
        raise ValueError(f"Error @ API call [status={response.status_code}]")

    values = response.json()

    # Convert to dataframe (columns headers = first row)
    dataframe = pd.DataFrame(values[1:], columns=values[0])
    dataframe = formatter(dataframe=dataframe, variable=variable)

    return dataframe


def formatter(dataframe: pd.DataFrame, variable: str) -> pd.DataFrame:
    """
    Wraps a few data cleaning methods

    Keyword arguments:
    * dataframe -- (DataFrame) Yielded from API call
    * variable -- (str) API variable for conditional statements
    """

    def fips_from_two_columns(
        df: pd.DataFrame,
        state_fips_column: str = "state",
        county_fips_column: str = "county",
    ):
        return f"{df[state_fips_column]}{df[county_fips_column]}"

    # Total population cleanup
    if variable == "totalPopulation":
        logging.info("Cleaning total population responses...")

        # Convert column names
        dataframe.rename(columns={"P1_001N": "values"}, inplace=True)

        dataframe["fips"] = dataframe.apply(fips_from_two_columns, axis=1)

        dataframe["county"] = dataframe["NAME"].apply(lambda x: x.split(",")[0].title())

    return dataframe
