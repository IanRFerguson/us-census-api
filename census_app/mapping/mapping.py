#!/bin/python3
import json
import logging
import os
import folium
import pandas as pd
import geopandas as gpd

from census_app import here, data_path

with open(os.path.join(data_path, "state_mapping.json")) as incoming:
    state_mapping = json.load(incoming)

output_directory = os.path.join(here, "static", "output")
logging.basicConfig(level=logging.INFO)

##########


def get_shape_data(fips_list: list, return_full_state: bool = False):
    """
    Isolate shapes from the master shapefile based on
    an incoming list of FIPS codes. Alternatively, we can read in all
    shapes for the current state and treat null values as 0's

    Keyword arguments:
    * fips_list -- (list) List of FIPS codes to match
    * return_full_state -- (bool) if True, returns all shapes for a state
    """

    shapefile_path = os.path.join(
        here, "data", "tl_2020_us_county", "tl_2020_us_county.shp"
    )

    if not os.path.exists(shapefile_path):
        raise OSError(f"Invalid shapefile path [given={shapefile_path}]")

    shapes = gpd.read_file(shapefile_path)

    ###

    if return_full_state:
        state_fips = fips_list[0][:2]
        shapes = shapes[shapes["STATEFP"] == state_fips].reset_index(drop=True)

    else:

        def state_county_fips(df, state="STATEFP", county="COUNTYFP"):
            return f"{df[state]}{df[county]}"

        shapes["fips"] = shapes.apply(state_county_fips, axis=1)
        shapes = shapes[shapes["fips"].isin(fips_list)].reset_index(drop=True)

    return shapes


def get_aggregate_data(api_data: pd.DataFrame):
    """
    Creates relevant shapefiles and aggregates with API data

    Keyword arguments:
    * api_data -- (DataFrame) Results from our API call
    """

    fips_list = api_data["fips"].to_list()
    shapes = get_shape_data(fips_list=fips_list)

    api_data = api_data.loc[:, ["fips", "county", "values"]]

    api_data = shapes.merge(api_data, on="fips", how="inner")

    ###

    # NOTE - Here we cast essential values to integers, as it plays nicely with Folium
    for var in ["fips", "values"]:
        api_data[var] = api_data[var].astype(int)

    shapes["fips"] = shapes["fips"].astype(int)

    return api_data, shapes


def mapping_coords(state_name: str) -> tuple:
    """
    Returns state coordinates and starting zoom position
    """

    temp = state_mapping[state_name]

    return temp["coord_list"], temp["zoom"]


def build_map(
    api_data: gpd.GeoDataFrame,
    output_name: str,
    state_name: str,
    output_directory: str = output_directory,
) -> None:
    """
    Creates a Folium map with the results of our API call
    and saves in the output directory
    """

    # Generate aggregated dataset with values and FIPS codes
    data, shapes = get_aggregate_data(api_data=api_data)

    # Identify coords and starting zoom for each state
    location, zoom_start = mapping_coords(state_name=state_name)

    # Build map
    m = folium.Map(location=location, zoom_start=zoom_start)

    folium.Choropleth(
        geo_data=shapes,
        data=data,
        columns=["fips", "values"],
        key_on="feature.properties.fips",
        fill_color="YlOrRd",
        fill_opacity=0.75,
        line_color="grey",
        line_opacity=0.5,
    ).add_to(m)

    # Hover functions

    def style_function(x):
        return {
            "fillColor": "#ffffff",
            "color": "#000000",
            "fillOpacity": 0.1,
            "weight": 0.1,
        }

    def highlight_function(x):
        return {
            "fillColor": "#000000",
            "color": "#000000",
            "fillOpacity": 0.50,
            "weight": 0.1,
        }

    NIL = folium.features.GeoJson(
        data,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=["county", "values"],
            aliases=["County Name: ", "Total Population: "],
            style=(
                "background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;"
            ),
        ),
    )

    # Add hover functions to leaflet.js map
    m.add_child(NIL)
    m.keep_in_front(NIL)
    folium.LayerControl().add_to(m)

    # Save to output directory
    m.save(os.path.join(output_directory, output_name))
