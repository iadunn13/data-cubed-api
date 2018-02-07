from itertools import permutations
from collections import defaultdict
from gmaps_integration import get_directions


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
			directions = get_directions(start, end)
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
	"""
	Since the determination of the best path through all locations relies on
	checking every possible path that does so (for n locations, there are n!
	possible paths that goes through each location)
	"""
	possible_paths = permutations(graph['nodes'])

	# grab the first path
	best_path = get_path_details(next(possible_paths), graph['edges'])
	for path in possible_paths:
		path_details = get_path_details(path, graph['edges'])
		if path_details['duration'] < best_path['duration']:
			best_path = path_details

	return best_path