import googlemaps
from collections import defaultdict


"""
This api key is connected to a project on a free google developers account
It has the following restrictions:
 - Only has access to Google Directions API
 - limited to 2500 requests per day
 - limited to 50 requests per second
Ref: https://developers.google.com/maps/documentation/directions/usage-limits?hl=en_US
"""
api_key = 'AIzaSyBGsse-VeQiKgcjHqQsBpQDnCLJpjZjPQ0'

gmaps = googlemaps.Client(key=api_key)


def get_location_order(locations):
	pair_dict = defaultdict(list)
	for x in locations:
		for y in locations:
			if x != y:
				pair_dict[x].append(y)

	location_order = []
	first = list(pair_dict.keys())[0]
	second = pair_dict[first][0]
	location_order.append(first)
	location_order.append(second)
	del pair_dict[first][0]
	if len(pair_dict[first]) == 0:
		del pair_dict[first]
	while pair_dict:
		last = location_order[-1]
		# always try to use the previous location as 'first'
		# to keep the chain
		if last in pair_dict:
			first = last

		else:
			first = list(pair_dict.keys())[0]
			# since we aren't continuing from the previous
			# chain we need to add the new 'first' to the order
			location_order.append(first)

		# add the pair to the location order
		second = pair_dict[first][0]
		location_order.append(second)

		# remove the pair from the pair dict
		del pair_dict[first][0]

		# if the 'first' address has no pairs left
		# remove it from the dict
		if len(pair_dict[first]) == 0:
			del pair_dict[first]

	return location_order


def process_request(request_locations):
	start_address = request_locations[0]
	end_address = request_locations[-1]
	waypoints = request_locations[1:-1]
	return gmaps.directions(
		start_address,
		end_address,
		waypoints=waypoints
	)


def retrieve_direction_data(locations):
	"""
	Retrieves data for each edge in the graph in batches of
	24 edges per request to the Google API

	The condensing of requests isn't incredibly necessary since
	the calculation of the best path forces a limit on the number
	of locations that this server can process at once
	"""
	# get a list of locations in the order that
	# we want to submit them to the Google API
	location_order = get_location_order(locations)

	request_locations = []
	responses = []
	last = location_order[0]
	for location in location_order[1:]:
		# if we have a value cached in 'last' we'll want to add it
		# to the request
		if last:
			request_locations.append(last)
			last = None

		request_locations.append(location)
		if len(request_locations) == 25:
			responses.append(process_request(request_locations))
			# keep the last location in the order so we don't lose out on that link
			last = request_locations[-1]
			request_locations = []

	# process a request for any remaining locations in the order
	if len(request_locations) > 0:
		responses.append(process_request(request_locations))

	return responses
