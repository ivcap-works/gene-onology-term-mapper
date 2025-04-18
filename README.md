# Gene Ontology (GO) Term Mapper

## What it does

Maps genes or proteins to GO terms using a local or remote database (e.g., UniProt or QuickGO), optionally builds a graph.

* Input: List of gene symbols
* Output: GO terms and categories
* Bonus: Build a GO hierarchy using networkx

## Core Workflow

* Input: List of gene/protein IDs (e.g. UniProt IDs or gene symbols)
* Query: Use QuickGO or UniProt API to fetch GO annotations
* Filter: Select GO terms by category (BP, MF, CC)
* Output: JSON of GO annotations per gene
* Optional: Visualize GO hierarchy using networkx

## Sample Questions for an Agent using this service as tool

These are typical user-facing queries an AI assistant might receive:

* "What are the biological functions of genes TP53, AKT1, and MCM10?"
<br>→ Agent maps the gene symbols to UniProt IDs (if needed) and calls map_go_terms.

* "List GO terms for protein Q9H0H5 involved in cellular components."
<br>→ Uses map_go_terms(ids=["Q9H0H5"], category="CC").

* "Give me all molecular functions associated with proteins P12345 and Q96GD4."

* "Which GO terms are shared between these proteins?"
<br>→ Agent may call map_go_terms and perform post-processing to find overlaps.
