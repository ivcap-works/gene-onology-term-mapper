from pathlib import Path
from typing import Dict, List
import networkx as nx
import matplotlib.pyplot as plt

from go_term_fetcher import Annotation

def build_go_graph(go_data: Dict[str, List[Annotation]]) -> nx.DiGraph:
    G = nx.DiGraph()
    for gene, terms in go_data.items():
        G.add_node(gene, type="gene")
        for term in terms:
            go_id = term.goId
            name = term.goName
            G.add_node(go_id, label=name, type="go_term")
            G.add_edge(gene, go_id)
    return G

def draw_graph(G: nx.DiGraph):
    pos = nx.spring_layout(G, k=0.5)
    node_colors = ['skyblue' if G.nodes[n]['type'] == 'gene' else 'lightgreen' for n in G.nodes]
    nx.draw(G, pos, with_labels=True, node_color=node_colors, font_size=8)
    plt.show()

def export_graph_image(G: nx.DiGraph, output_path: str = "go_graph.png"):
    pos = nx.spring_layout(G, k=0.7)
    node_colors = ['skyblue' if G.nodes[n]['type'] == 'gene' else 'lightgreen' for n in G.nodes]

    plt.figure(figsize=(10, 8))
    nx.draw(G, pos, with_labels=True, node_color=node_colors, font_size=8, edge_color='gray')
    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300)
    plt.close()

if __name__ == "__main__":
    import asyncio
    import json
    from fastapi.encoders import jsonable_encoder
    from go_term_fetcher import fetch_go_terms

    async def main():
        terms = {
            "P12345": await fetch_go_terms("P12345"),
            "Q9H0H5": await fetch_go_terms("Q9H0H5")
        }
        graph = build_go_graph(terms)
        draw_graph(graph)

    asyncio.run(main())
