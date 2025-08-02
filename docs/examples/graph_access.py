"""Example of accessing graph elements from Louie responses."""

from louieai import louie

# Create a cursor instance
lui = louie()

# Make a query that returns graphs
lui("Show me a graph of the network connections")

# Access the latest graph
if lui.g:
    print(f"Graph dataset ID: {lui.g.get('dataset_id')}")
    print(f"Graph type: {lui.g.get('type')}")

# Access all graphs from the latest response
print(f"Number of graphs: {len(lui.gs)}")
for i, graph in enumerate(lui.gs):
    print(f"Graph {i}: {graph.get('dataset_id')}")

# Access graphs from previous queries
lui("Create another visualization")

# Access graphs from 2 queries ago
previous_graphs = lui[-2].gs
if previous_graphs:
    print(f"Previous query had {len(previous_graphs)} graphs")
    print(f"First graph from previous: {lui[-2].g.get('dataset_id')}")

# Check if a response has graphs
if lui[-1].gs:
    print("Latest response contains graph visualizations")
else:
    print("Latest response has no graphs")

# Mixed response with text, dataframes and graphs
lui("Analyze the data and show me graphs and tables")

# Access different element types
print(f"Text: {lui.text}")
print(f"Dataframes: {len(lui.dfs)}")
print(f"Graphs: {len(lui.gs)}")

# Iterate through all elements
for elem in lui.elements:
    print(f"Element type: {elem['type']}, value: {elem.get('value', 'N/A')[:50]}...")