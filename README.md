# US Census API Application

This is a lightweight `Flask` applicaiton that queries the US Census API, cleans the data, and renders an interactive `Folium` map with the output.

### User Notes

* This app is Dockerized and can be run simply with `docker compose up --build`
* The `Flask` app, `Redis` server, and `RQ` worker run in the same container
* Mapping requests are handled asynchronously so that users don't experience long wait times in the browser