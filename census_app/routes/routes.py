#!/bin/python3
import us
import os

from flask import render_template, redirect, url_for, flash, request
from census_app.routes import bp

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

    states = [k.name for k in us.states.STATES]
    variable_options = ["Total Population"]

    if request.method == "POST":
        state_value = request.form["state"]
        variable_value = request.form["variable"]

        if any([state_value == "#", variable_value == "#"]):
            flash("Please select values for both fields!")
            return redirect(url_for("routes.index"))

        return redirect(
            url_for("routes.api_call", state=state_value, variable=variable_value)
        )

    return render_template(
        "index.html", states=states, variable_options=variable_options
    )


@bp.route("/api/<state>/<variable>", methods=["GET"])
def api_call(state: str, variable: str):
    """
    REST API ROUTE

    Developer notes
    * This REST route takes a state and variable
    * The custom API function is handed off to an RQ worker
    """

    flash(f"Request received for {variable} in {state}")

    return redirect(url_for("routes.index"))


@bp.route("/results", methods=["GET", "POST"])
def results():
    """
    RESULTS PAGE

    Developer notes
    * Here we'll list all jobs that have processed previously
    """

    return render_template("results.html", column_headers=["Test", "1", "2", "3", "4"])
