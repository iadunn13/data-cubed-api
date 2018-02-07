from flask import Flask, request
from graph_utils import build_graph, get_best_path
from gmaps_integration import retrieve_direction_data
import json


app = Flask(__name__)


@app.route("/")
def efficient_path():
	"""
	Takes a list of locations and returns the most efficient path that goes through each location

	Restrictions:
		I've restricted it to a maximum of 9 locations because processing all permutation paths
		in graph_util.get_best_path() tends to cause my VM to crash around N=10
	"""
	request_addresses = request.values.getlist('addresses')
	if len(request_addresses) > 9:
		return json.dumps({"error": "too many locations provided"})

	direction_data = retrieve_direction_data(request_addresses)
	graph = build_graph(direction_data)
	best_path = get_best_path(graph)
	return json.dumps(best_path)

if __name__ == '__main__':
	app.run(debug=True)
