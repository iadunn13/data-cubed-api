# data-cubed-api

A simple API assignment from Data Cubed.

##### Premise:
Please write a Python server that takes the addresses of 3 locations (valid addresses recognizable by the Google API ) and outputs the distance and time taken of the most efficient route going through all 3 locations. No front end is necessary, the server may be queried via CURL with results being in a form of a JSON file. External APIs may be used for this assignment.

For a bonus, allow as input an arbitrary number of locations as opposed to just 3.


## My Solution:
### Setup Steps:
This solution was written in Python 3.5.3 and uses Flask and the Google Maps API
If you are running a different version of Python, it may be easiest to just set up a virtual env using [pyenv](https://github.com/pyenv/pyenv-virtualenv)

I've included a requirements file for easy use with pip:

`pip install -r requirements.txt`


To run this API server, clone/download this repo and from the project directory run:

`python api.py`

This should have the server running and have the API accessible at http://127.0.0.1:5000/
Logging output will be seen in api.log

The API should work using both the requests library or cURL

With requests:

```
import requests
data = {"addresses": [...]}
url = "http://127.0.0.1:5000/"
requests.get(url, data=data)
```

With cURL:

```
curl -X GET -H Accept:application/json -H Content-Type:application/json --data '{"addresses": [...]}' http://127.0.0.1:5000/
```

#### Notes:
I've included a Google API key in this project that I've set up specifically for this project and it only has access to the Google Maps Directions API.  Since the key I set up was free, there is a requests per second limit of 50 (See [here](https://developers.google.com/maps/documentation/directions/usage-limits?hl=en_US)).
My API should be making only one call to Google, so this limit will only be reached if a lot of requests are sent to my API at once.

The process of determining the most efficient path becomes too computationally expensive at around 11 locations.  This is because for N locations in the graph, there are N! possible paths that pass through all nodes.  For the time being I have put in a check to require 10 locations or less.

