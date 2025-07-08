# # Packages
import sys
import os
from jsonschema import validate
import json
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

SVIF_SCHEMA = {
        "type": "object", "properties": {
        # Elements
        "elements": {"type": "object", "properties": {
            # Nodes
            "nodes": {"type": "array", "properties": {
                "data": {"type": "object", "properties": {
                    "id": {"type": "string"},
                    "labels": {"type": "array"},
                    "properties": {"type": "object", "properties": {
                        "simpleName": {"type": "string"},
                        "metaSrc": {"type": "string"}
                    }}
                    # Required object of node data
                }, "required": ["id"]}
                # Required in node
            }, "required": ["data"]},
            # Edges
            "edges": {"type": "array", "properties": {
                "data": {"type": "object", "properties": {
                    "id": {"type": "string"},
                    "source": {"type": "string"},
                    "target": {"type": "string"},
                    "label": {"type": "string"},
                    "properties": {"type": "object"}
                    # Required objects of edge data
                }, "required": ["id", "source", "target"]}
                # Required in edge
            }, "required": ["data"]}
            # Required in elements. ClassViz still accepts file without edges
        }, "required": ["nodes"]}
    # Require elements to be a valid SVIF file
    }, "required": ["elements"]
}

def is_valid_svif_file(path):
    data = json.load(open(path))
    validate(instance=data, schema=SVIF_SCHEMA)

# Launch a simple HTTP server to serve static files
def serve(tool_dir, port):
    os.chdir(tool_dir)                 # Change to the tool directory
    handler = SimpleHTTPRequestHandler
    httpd = ThreadingHTTPServer(("0.0.0.0", port), handler)
    print(f"ClassViz ready on http://0.0.0.0:{port}/")
    httpd.serve_forever()              # Block until the container stops


def main():
    if len(sys.argv) != 3:
        sys.exit("Error: Wrong number of arguments\nUsage: classviz.py <input> <output>")

    input_path, output_path = sys.argv[1:]
    port = int(os.getenv("GALAXY_IT_PORT", "7800"))

    try:
        is_valid_svif_file(input_path)
    except ValidationError as e:
        print("Invalid SVIF format:", e)
        sys.exit(7)
    except json.JSONDecodeError:
        print("Not a JSON file.")
        sys.exit(6)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    open(output_path, "wb").write(open(input_path, "rb").read())

    # Launch the server with the web files in the tool directory
    tool_dir = os.path.dirname(__file__)
    serve(tool_dir, port)

if __name__ == "__main__":
    print("Running Visualization tool.")
    main()

