#!/bin/python3
import us
import os
import logging
import glob
from time import sleep

from flask import render_template, redirect, url_for, flash, request
from census_app.routes import bp
from census_app import here

logging.basicConfig(level=logging.INFO)

##########


@bp.route("/", methods=["GET", "POST"])
def index():
    """
    LANDING PAGE

    Developer notes
    * User will select a state and a variable
    * We'll make an API call and render a Choropleth map asynchronously
    * Output HTML will render in templates directory
    """

    # List of US state names
    states = [k.name for k in us.states.STATES]

    # Dictionary of display name: API value key values
    variable_map = {
        "Total Population [2020]": "totalPopulation",
        "Population % Change [2000 - 2020]": "popPctChange",
    }

    if request.method == "POST":

        # Read in values from HTML form and validate
        state_value = request.form["state"]
        variable_value = request.form["variable"]

        if any([state_value == "#", variable_value == "#"]):
            flash("Please select values for both fields!")
            return redirect(url_for("routes.index"))

        logging.info(
            f"Received request [state={state_value}, request={variable_value}]"
        )

        return redirect(
            url_for("routes.api_call", state=state_value, variable=variable_value)
        )

    return render_template("index.html", states=states, variable_options=variable_map)


@bp.route("/api/<state>/<variable>", methods=["GET"])
def api_call(state: str, variable: str):
    """
    REST API ROUTE

    Developer notes
    * This REST route takes a state and variable
    * The custom API function is handed off to an RQ worker
    """

    from census_app.api.async_request import run_api_call

    run_api_call(state=state, variable=variable)

    flash(f"API request recieved + running in the background")

    return redirect(url_for("routes.index"))


@bp.route("/results", methods=["GET", "POST"])
def results():
    """
    RESULTS PAGE

    Developer notes
    * Here we'll list all jobs that have processed previously
    """

    from census_app.results.results import get_all_results

    data = get_all_results()
    columns = data.columns.to_list()

    return render_template(
        "results.html", data=data.to_dict("records"), column_headers=columns
    )


@bp.route("/render_map/<filename>", methods=["GET", "POST"])
def render_map(filename: str):
    """
    KISS, we'll just hand this route an HTML path
    and it'll render a presentation for the end user

    Keyword arguments:
    * html_path -- (str) Pathlike string to HTML output
    """

    from census_app.results.results import parse_filename

    components = parse_filename(filename)

    filename = os.path.join("output", f"{filename}.html")

    return render_template(
        "map.html", filename=filename, state=components[0], api_type=components[1]
    )


@bp.route("/dev_map_route", methods=["GET"])
def dev_render_map():
    """
    DEV FUNCTION
    """

    from census_app.results.results import get_all_output_paths

    test = get_all_output_paths()[0]

    return redirect(url_for("routes.render_map", filename=test))


@bp.route("/peace-out", methods=["GET"])
def peace_out():
    """
    DEV FUNCTION
    """

    static_paths = os.path.join(here, "static", "output", "**/*.html")
    all_files = [x for x in glob.glob(static_paths, recursive=True)]

    logging.info(all_files)

    for file in all_files:
        try:
            os.remove(file)
            logging.info(f"Removed {file.split('/')[-1].replace('.html', '')}")

        except Exception as e:
            logging.error(f"Failed to remove file [exception={e}]")

    flash("All output files removed")

    return redirect(url_for("routes.index"))
