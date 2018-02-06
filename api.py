from flask import Flask, request
from itertools import permutations
import json
import googlemaps


app = Flask(__name__)
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

		2) there may be a way to use the waypoints argument to
		  collapse multiple requests down into 1, however this
		  would put more reliance on the Google API to provide
		  the most efficient route between 2 points (see get_shortest_route())
"""
api_key = 'AIzaSyBGsse-VeQiKgcjHqQsBpQDnCLJpjZjPQ0'

gmaps = googlemaps.Client(key=api_key)


def get_shortest_route(routes):
	"""
	takes a list of routes from the Google Directions API and returns
	the shortest route

	I would rather call the API with alternatives=True and determine
	the best route from the response locally instead of assuming the
	API will return the best option.  This also leaves room to add
	more complex analysis for determining route efficiency
	"""

	# Note:
	# as per the API docs, routes with no intermediate waypoints
	# will only have 1 element in 'legs'

	# for the sake of simplicity, I am considering the shortest duration to be
	# the most efficient
	return min(routes, key=lambda x: x['legs'][0]['duration']['value'])


def get_edge_from_route(route):
	"""
	Converts a route from the Google Directions API to an edge
	for use in our graph (essentially just cuts out extraneous data)
	"""
	path = route['legs'][0]
	return {
		"start": path['start_address'],
		"end": path['end_address'],
		"duration": path['duration']['value'],
		"distance": path['distance']['value'],
	}


def get_path_details(path, edges):
	start = path[0]
	details = {
		"path": path,
		"duration": 0,
		"distance": 0
	}
	for end in path[1:]:
		edge_data = edges[start][end]
		details["duration"] += edge_data["duration"]
		details["distance"] += edge_data["distance"]
		start = end
	return details


def get_best_path(graph):
	possible_paths = permutations(graph['nodes'])

	# grab the first path
	best_path = get_path_details(next(possible_paths), graph['edges'])
	for path in possible_paths:
		path_details = get_path_details(path, graph['edges'])
		if path_details['duration'] < best_path['duration']:
			best_path = path_details

	return best_path


def build_graph(addresses):
	""" 
	simple graph where each node has an edge to each other node
	the distances of the edges will be represented by the distances
	given by the Google Directions API


	graph.nodes will be a list of the names (addresses) of each node

	graph.edges will be a dict in the form of:
	{
		start_address: {
			end_address: {
				direction data between start_address and end_address
			}
			.
			.
			.
		} for start_address in graph.nodes
	}

	"""
	graph = {
		"nodes": [],
		"edges": {}
	}
	for i, start in enumerate(addresses):
		address = start
		for end in addresses[:i] + addresses[i+1:]:
			# create an edge for each pair of locations
			# going in both directions
			directions = gmaps.directions(start, end, alternatives=True)
			shortest_route = get_shortest_route(directions)
			edge = get_edge_from_route(shortest_route)

			start_address = edge['start']
			if start_address not in graph['edges']:
				# key everything using the exact string returned from the API
				# it doesn't always match exactly with the initial input string
				# (i.e. one may have the zipcode, country, etc. and the other doesn't)
				graph['edges'][start_address] = {}
				address = start_address

			graph['edges'][start_address][edge['end']] = edge
		graph['nodes'].append(address)

	return graph

@app.route("/")
def efficient_path():

	request_addresses = request.values.getlist('addresses')
	graph = build_graph(request_addresses)
	best_path = get_best_path(graph)
	return json.dumps(best_path)

if __name__ == '__main__':
	app.run(debug=True)