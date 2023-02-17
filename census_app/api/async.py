#!/bin/python3
from rq import Queue
from redis import Redis
from urllib.parse import urlparse
import os
from dotenv import load_dotenv

from census_app import here
from census_app.api.call import get_api_data
from census_app.api.mapping import get_shape_data, build_map

load_dotenv(os.path.join(here, ".env"))

redis_url = os.environ.get("REDIS_URL")
url = urlparse(redis_url)

r = Redis(host=url.hostname, port=url.port, decode_responses=True)
queue = Queue(name="census", connection=r, default_timeout=3600)

##########


def build_api_call(state: str, variable: str):
    """
    Enqueues an asynchronous API call to read data and generate a choropleth
    map in the background

    Keyword arguments:
    * state -- (str) US state name (this is converted to a FIPS in the back-end)
    * variable -- (str) API request to format and query
    """

    census_data = get_api_data()
    shape_data = get_shape_data()
    build_map()


def run_api_call(state: str, variable: str):
    job = queue.enqueue(build_api_call, state, variable)
