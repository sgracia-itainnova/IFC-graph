import argparse
import ifcopenshell
import networkx as nx
from pyvis.network import Network

import p2n
import opd

def plot_large_graph(graph, output_file):
    # Initialize Pyvis network
    net = Network(notebook=False, height="1000px", width="100%", bgcolor="#222222", font_color="white")

    # Add nodes with labels
    print('Adding nodes to plot')
    for i, (node, data) in enumerate(graph.nodes(data=True)):
        net.add_node(node, label=data.get('name', ''), title=str(data))
        print(f'Added node {i}/{len(graph.nodes)}')

    # Add edges with labels
    print('Adding edges to plot')
    for i, (source, target, data) in enumerate(graph.edges(data=True)):
        net.add_edge(source, target, label=data.get('type', ''), title=str(data))
        print(f'Added edge {i}/{len(graph.edges)}')

    # Save the interactive plot to the specified file
    net.save_graph(output_file)

def save_graph(graph, filename):
    nx.write_edgelist(graph, filename)

def load_graph(filename):
    return nx.read_edgelist(filename)

ONLY_PLOT = True

# Press the green button in the gutter to run the script.
if __name__ == "__main__":
    USAGE = """
        Visualize IFC STEP file.
        Usage: python ifc-graph.py -f /path/filename -a all|zhu|wiss
        Example python ifc-graph.py -f ./test.ifc -a zhu
    """
    parser = argparse.ArgumentParser(description=USAGE)
    parser.add_argument('-f', '--file', type=str, help='Input IFC STEP file path and file name',
                        default='test.ifc')
    parser.add_argument('-a', '--algorithm', type=str,
                        help='Write "all" to test all algorithms. Write "zhu" or "wiss" to test other algorithms',
                        default='all')
    parser.add_argument('-o', '--output', type=str, help='Output HTML file for the graph visualization',
                        default='ifc_graph.html')
    parser.add_argument('-g', '--graph', type=str, help='Output file for saving the graph object',
                        default='ifc_graph.txt')
    args = parser.parse_args()

    if not ONLY_PLOT:
        # Parse IFC STEP file using IfcOpenShell
        print("Use IfcOpenShell to parse IFC STEP file.")
        my_ifc_file = ifcopenshell.open(args.file)

        # Create an in-memory graph using NetworkX
        G = nx.Graph()

        # Insert using Zhu algorithm
        if args.algorithm in ('all', 'zhu'):
            p2n.create_full_graph(G, my_ifc_file)

        # Insert using Wiss algorithm
        if args.algorithm in ('all', 'wiss'):
            opd.create_full_graph(G, my_ifc_file)

        # Cleanup IFC file
        del my_ifc_file

        # Print the created graph
        print("Graph created:")

        # Save the graph object
        save_graph(G, args.graph)
        print(f"Graph object saved to {args.graph}")

    # Plot the graph using Pyvis and save it to the specified file
    G = load_graph(args.graph)
    plot_large_graph(G, args.output)
