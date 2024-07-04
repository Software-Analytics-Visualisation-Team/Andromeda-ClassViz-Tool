# # Packages
import sys
import os
from jsonschema import validate
import json

def is_valid_svif_file(input_file: str):
    """Check if the input file at file_path is a valid SVIF file.

    Args:
        file_path (str): Path to the input file.

    Returns:
        bool: True if the file is a valid SVIF file, False otherwise.
    """
    # Schema for SVIF files
    schema = {
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
    print(f"Inputting {input_file}.")

    # Validate input file type
    try:
        # Load input file
        with open(input_file) as f:
            is_SVIF = json.load(f)
    except:
        print("Not a JSON file.")
        sys.exit(6)

    # Validate input file SVIF format
    try:
        validate(instance=is_SVIF, schema=schema)
        print("Input file validated.")
    except:
        print("Invalid SVIF format.")
        sys.exit(7)


def rm_file(file_path: str):
    """Remove previous input file at file_path.

    Args:
        file_path (str): Path to the file.
    """
    # Remove file
    if os.path.exists(file_path):
        os.remove(file_path)
        print("Previous input file removed.")
    else:
        print("The file does not exist.") 

def copy_input_file_to_data_folder(input_file: str, output_file: str):
    """Copy content of user input file to 'data/'.

    Args:
        input_file (str): Path to the input file.
        output_file (str): Path to the output file.
    """

    # Get content of input file
    with open(input_file, 'r') as f:
        data = f.read()
        # Write content to output file
        with open(output_file, 'w') as f:
            f.write(data)
            print(f"Copied input file to {output_file}.")

def build_http_server(tool_dir: str):
    """Build a HTTP server to host the visualization.
    Args:
        tool_dir (str): Path to the directory containing the visualization tool.
    """
    # Build the HTTP server
    os.system(f"python3 -m http.server 7800 -d {tool_dir}")

def main(argv):
    """Take in command-line arguments and use them as parameters for other methods.

    Args:
        argv (list[type]]): Provided CLI arguments.
    """
    # Assign CLI arguments
    input_file, output_file, tool_dir = argv[1:4]

    # Validate input file
    is_valid_svif_file(input_file)
    
    # Remove previous input file if it exists - cause Galaxy is laggy
    rm_file(output_file)
    # Copy input file to 'data/'
    copy_input_file_to_data_folder(input_file, output_file)
    # Build HTTP server to deploy ClassViz
    build_http_server(tool_dir)

if __name__ == "__main__":
    print("Running Visualization tool.")
    main(sys.argv)
