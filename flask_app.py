from flask import Flask, jsonify    # pip install Flask

app = Flask(__name__)

# Define the endpoints and responses
room = {
    "A": [-10.5, -12.5],
    "B": [-10.5, 12.5],
    "C": [10.5, 12.5],
    "D": [10.5, -12.5]
}
anchors = {
    "anchor1": [0, 1.3],
    "anchor2": [2.45, 2.0],
    "anchor3": [4, 0.2]
}
tags = {
    "tag1": [0, 0],
}

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "get_room": "/coordinate/room",
        "get_anchors": "/coordinate/anchors",
        "get_tags": "/coordinate/tags"
    })

@app.route('/coordinate/room', methods=['GET'])
def get_room():
    return jsonify(room)

@app.route('/coordinate/anchors', methods=['GET'])
def get_anchors():
    return jsonify(anchors)

@app.route('/coordinate/tags', methods=['GET'])
def get_tags():
    return jsonify(tags)


if __name__ == '__main__':
    app.run(debug=True)
