#!/bin/python3
from rq import Queue
from redis import Redis
from urllib.parse import urlparse
import os
import json
from dotenv import load_dotenv
from datetime import datetime
import pytz
import logging

from census_app import here
from census_app.api.call import get_api_data
from census_app.mapping.mapping import build_map

load_dotenv(os.path.join(here, ".env"))

redis_url = os.environ.get("REDIS_URL")
url = urlparse(redis_url)

r = Redis(host=url.hostname, port=url.port, decode_responses=True)
queue = Queue(name="census", connection=r, default_timeout=3600)

logging.basicConfig(level=logging.INFO)

##########


def build_api_call(state: str, variable: str):
    """
    Enqueues an asynchronous API call to read data and generate a choropleth
    map in the background

    Keyword arguments:
    * state -- (str) US state name (this is converted to a FIPS in the back-end)
    * variable -- (str) API request to format and query
    """

    logging.info(f"Request received ... [state={state}, variable={variable}]")
    timestamp = datetime.now(pytz.timezone("US/Eastern")).strftime("%m-%d-%Y")
    naming_convention = f"state-{state}_var-{variable}_timestamp-{timestamp}.html"

    # Call data from Census API and build DataFrame
    logging.info("Sending Census request...")
    census_data = get_api_data(state_name=state, variable=variable)

    # Render map and save output
    logging.info("Building map...")
    build_map(api_data=census_data, output_name=naming_convention, state_name=state)

    logging.info("Map built successfully!")


def run_api_call(state: str, variable: str):
    job = queue.enqueue(build_api_call, state, variable)
    task = job.get_id()

    result = {
        "Id": task,
        "State": state,
        "VariableName": variable,
        "RequestedAt": datetime.now(pytz.timezone("US/Eastern")).strftime(
            "%b-%d-%Y::%H:%M:%S"
        ),
    }

    return json.dumps(result)
