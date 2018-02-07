from collections import defaultdict
from itertools import permutations


def get_edge_from_leg(leg):
	"""
	Converts a route leg from the Google Directions API to an edge
	for use in our graph (essentially just cuts out extraneous data)
	"""
	return {
		"start": leg['start_address'],
		"end": leg['end_address'],
		"duration": leg['duration']['value'],
		"distance": leg['distance']['value'],
	}


def add_edge_to_graph(graph, edge):
	# due to the way the api calls are condensed,
	# there may be duplicate legs present
	# if for some reason one was better than the other
	# we should use it
	start_address = edge["start"]
	end_address = edge["end"]
	#import pdb; pdb.set_trace()
	if (not graph["edges"][start_address]
			or end_address not in graph["edges"][start_address]
			or graph["edges"][start_address][end_address]["duration"] > edge["duration"]):
		graph["edges"][start_address][end_address] = edge

	if start_address not in graph["nodes"]:
		graph["nodes"].append(start_address)


def build_graph(direction_data):
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
		"edges": defaultdict(dict)
	}
	for response in direction_data:
		for route in response:
			for leg in route['legs']:
				start_address = leg["start_address"]
				end_address = leg["end_address"]
				edge = get_edge_from_leg(leg)
				add_edge_to_graph(graph, edge)				

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
	possible_paths = permutations(graph['nodes'])

	# grab the first path
	best_path = get_path_details(next(possible_paths), graph['edges'])
	for path in possible_paths:
		path_details = get_path_details(path, graph['edges'])
		if path_details['duration'] < best_path['duration']:
			best_path = path_details

	return best_path
