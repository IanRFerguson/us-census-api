# US Census API Application

This is a lightweight `Flask` applicaiton that queries the US Census API, cleans the data, and renders an interactive `Folium` map with the output.

### Running the App

* This app is Dockerized and can be run simply with `docker compose up --build`
* The `Flask` app, `Redis` server, and `RQ` worker run in the same container
* Mapping requests are handled asynchronously so that users don't experience long wait times in the browser


### Usage Notes

* Select your state and API request type on the landing page

<img src="./images/landing.png" width="65%">

* A choropleth map is rendered and saved asynchronously; see all requests stored on the results page

<img src="./images/results.png" width="65%">

* You can click on the `View` anchor for each request to see a customized rendering of the map

<img src="./images/example.png" width="65%">
