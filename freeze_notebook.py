#!/usr/bin/env python3
"""
A script to add a "no-execute" tag to all cells in a Jupyter Notebook.

This script:
- Reads the notebook (JSON format).
- Iterates over all cells.
- For each cell, it checks if the metadata dictionary has a "tags" list.
- If the tag "no-execute" is not already present, it appends it.
- Writes the updated notebook back to disk.

Usage:
    python edit_notebook.py <input_notebook.ipynb> [output_notebook.ipynb]

If no output file is specified, the input file will be overwritten.
"""

import json
import sys
import os

def add_no_execute_tag(notebook_path, output_path=None):
    """
    Reads a notebook, adds the "no-execute" tag to every cell, and saves the modified notebook.
    
    Args:
        notebook_path (str): Path to the notebook file to be modified.
        output_path (str): Optional output path for the modified notebook.
                           If None, the notebook is overwritten in place.
    """
    # Read the original notebook file.
    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)
    
    # Iterate over each cell in the notebook.
    for cell in nb.get("cells", []):
        # Ensure 'metadata' is present.
        if "metadata" not in cell:
            cell["metadata"] = {}
        metadata = cell["metadata"]
        
        # Get the existing tags or initialize an empty list.
        tags = metadata.get("tags", [])
        
        # If "no-execute" tag is not in the tags, add it.
        if "no-execute" not in tags:
            tags.append("no-execute")
        
        # Update the metadata for the cell.
        metadata["tags"] = tags
        cell["metadata"] = metadata

    # Determine the output path.
    if output_path is None:
        # Overwrite the original file.
        output_path = notebook_path

    # Write the updated notebook back to disk.
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=2)
    
    print(f"Modified notebook saved to '{output_path}'.")

if __name__ == "__main__":
    # Check if the notebook path was provided as an argument.
    if len(sys.argv) < 2:
        print("Usage: python edit_notebook.py <input_notebook.ipynb> [output_notebook.ipynb]")
        sys.exit(1)
    
    notebook_path = sys.argv[1]
    
    # Optionally, get the output file from the command line, if provided.
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Validate that the provided notebook path exists.
    if not os.path.isfile(notebook_path):
        print(f"Error: The file '{notebook_path}' does not exist.")
        sys.exit(1)
    
    # Run the function to add the tag.
    add_no_execute_tag(notebook_path, output_path)