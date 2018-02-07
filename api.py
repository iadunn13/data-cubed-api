from flask import Flask, request
from graph_utils import build_graph, get_best_path
import googlemaps
import json


app = Flask(__name__)


@app.route("/")
def efficient_path():
	"""
	Takes a list of locations and returns the most efficient path that goes through each location

	Restrictions:
		No more than 7 locations at once.  Since the determination of the best path relies on
		checking every possible path, that means for N locations there are N! possible paths
		to check.  At somewhere around N=11 or N=12 this becomes too large to process in a quick
		amount of time

		Combining this with the fact that my Google API key will hit the requests per second limit
		with N > 7 (see gmaps_integration.py for more info), I'm opting to just cap it at 7
	"""
	request_addresses = request.values.getlist('addresses')
	if len(request_addresses) > 7:
		return json.dumps({"error": "too many locations provided"})

	graph = build_graph(request_addresses)
	best_path = get_best_path(graph)
	return json.dumps(best_path)

if __name__ == '__main__':
	app.run(debug=True)