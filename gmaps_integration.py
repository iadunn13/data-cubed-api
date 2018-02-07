import googlemaps

"""
This api key is connected to a project on a free google developers account
It has the following restrictions:
 - Only has access to Google Directions API
 - limited to 2500 requests per day
 - limited to 50 requests per second**
Ref: https://developers.google.com/maps/documentation/directions/usage-limits?hl=en_US

**  under the basic implementation, for N addresses provided to this api, n(n-1) requests
	are made to the Google API.  This means that the limit is when N > 7
	possible solutions to this:

		1) manually throttle requests on this end

		2) the requests to the Google API can be condensed down
		   to retrieve the data for 25 graph edges per request
		   using the waypoints argument of the directions API.
		   This would rely on google returning only the most
		   efficient route between any two locations.  (Ommiting
		   the waypoints argument and only providing start and end
		   will return multiple possible routes that we can then
		   scan for the most efficient one)
"""
api_key = 'AIzaSyBGsse-VeQiKgcjHqQsBpQDnCLJpjZjPQ0'

gmaps = googlemaps.Client(key=api_key)

def get_directions(start, end):
	return gmaps.directions(start, end, alternatives=True)
