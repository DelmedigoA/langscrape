from langscrape.agent.graph import get_graph

def test_save_graph_image(filename: str = "graph.png"):
    graph = get_graph(tools=[])
    png_bytes = graph.get_graph().draw_mermaid_png()

    # Save to file
    with open(filename, "wb") as f:
        f.write(png_bytes)

    print(f"✅ Graph image saved to {filename}")

# Run it
test_save_graph_image("assets/graph.png")
