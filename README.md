# 📘 Tutorial: Building a Gene Ontology (GO) Term Mapper Tool for the IVCAP Platform

See the [TUTORIAL](tutorial.md) file for more

----


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

## Development Steps

### Setup Poetry

We first create a basic `poetry` setup to define all the dependencies as well their respective versions.

```
% poetry init

This command will guide you through creating your pyproject.toml config.

Package name [gene-onology-term-mapper]:
Version [0.1.0]:
Description []:  A tool to map genes or proteins to GO terms using a local or remote database
Author [Max Ott <max.ott@data61.csiro.au>, n to skip]:
License []:
Compatible Python versions [>=3.10]:

Would you like to define your main dependencies interactively? (yes/no) [yes] no
Would you like to define your development dependencies interactively? (yes/no) [yes] no
Generated file

[project]
name = "gene-onology-term-mapper"
version = "0.1.0"
description = "A tool to map genes or proteins to GO terms using a local or remote database"
authors = [
    {name = "Max Ott",email = "max.ott@data61.csiro.au"}
]
readme = "README.md"
requires-python = ">=3.10"
dependencies = [
]


[build-system]
requires = ["poetry-core>=2.0.0,<3.0.0"]
build-backend = "poetry.core.masonry.api"


Do you confirm generation? (yes/no) [yes]
```

### Implementing the Core Functionality

The base functionality will be provided by a function `fetch_go_terms(uniprot_id: str) -> List[Annotation]`
which takes a protein ID as argument and returns a list of annotations. It uses the
[Gene Ontology and GO Annotations (QuickGO)](https://www.ebi.ac.uk/QuickGO/) service to retrieve the
annotations.

Let's open a new file `go_term_fetcher.py` and add the following:

```python
async def fetch_go_terms(uniprot_id: str) -> List[Annotation]:
    url = f"https://www.ebi.ac.uk/QuickGO/services/annotation/search"
    params = {
        "geneProductId": f"UniProtKB:{uniprot_id}",
        "limit": 100
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
        results = [Annotation(**d) for d in data["results"]]
        return results
```

We also need to import some libraries as well as define the _shape_ of the
returned annotations.

```python
import httpx
from typing import List, Dict, Optional
from pydantic import BaseModel

GO_CATEGORIES = {
    "BP": "biological_process",
    "MF": "molecular_function",
    "CC": "cellular_component",
}

class Annotation(BaseModel):
    id: Optional[str] = None
    geneProductId: Optional[str] = None
    qualifier: Optional[str] = None
    goId: Optional[str] = None
    goAspect: Optional[str] = None
    goEvidence: Optional[str] = None
    goName: Optional[str] = None
    assignedBy: Optional[str] = None
    symbol: Optional[str] = None
    synonyms: Optional[str] = None
    name: Optional[str] = None
    reference: Optional[str] = None
```

and add the dependencies to poetry

```
% poetry add httpx pydantic fastapi
Using version ^0.28.1 for httpx
Using version ^2.11.4 for pydantic
Using version ^0.115.12 for fastapi

Updating dependencies
Resolving dependencies... (0.5s)

Package operations: 15 installs, 0 updates, 0 removals

  - Installing typing-extensions (4.13.2)
  - Installing exceptiongroup (1.3.0)
  - Installing idna (3.10)
  - Installing sniffio (1.3.1)
  - Installing annotated-types (0.7.0)
  - Installing anyio (4.9.0)
  - Installing certifi (2025.4.26)
  - Installing h11 (0.16.0)
  - Installing pydantic-core (2.33.2)
  - Installing typing-inspection (0.4.0)
  - Installing httpcore (1.0.9)
  - Installing pydantic (2.11.4)
  - Installing starlette (0.46.2)
  - Installing fastapi (0.115.12)
  - Installing httpx (0.28.1)

Writing lock file
```

To test our progress so far, we add some code to verify that this is working:

```python
if __name__ == "__main__":
    import asyncio
    import json
    from fastapi.encoders import jsonable_encoder

    async def main():
        terms = await fetch_go_terms("P12345")
        print(json.dumps([jsonable_encoder(term) for term in terms[:3]], indent=2))
    asyncio.run(main())
```

And now, let's test it

```
% poetry run python go_term_fetcher.py
[
  {
    "id": "UniProtKB:P12345!306410571",
    "geneProductId": "UniProtKB:P12345",
    "qualifier": "enables",
    "goId": "GO:0003824",
    "goAspect": "molecular_function",
    "goEvidence": "IEA",
    "goName": null,
    "assignedBy": "InterPro",
    "symbol": "GOT2",
    "synonyms": null,
    "name": null,
    "reference": "GO_REF:0000002"
  },
  {
    "id": "UniProtKB:P12345!306410572",
    "geneProductId": "UniProtKB:P12345",
    "qualifier": "enables",
    "goId": "GO:0004069",
    "goAspect": "molecular_function",
    "goEvidence": "ISS",
    "goName": null,
    "assignedBy": "UniProt",
    "symbol": "GOT2",
    "synonyms": null,
    "name": null,
    "reference": "GO_REF:0000024"
  },
  {
    "id": "UniProtKB:P12345!306410573",
    "geneProductId": "UniProtKB:P12345",
    "qualifier": "enables",
    "goId": "GO:0004069",
    "goAspect": "molecular_function",
    "goEvidence": "IEA",
    "goName": null,
    "assignedBy": "UniProt",
    "symbol": "GOT2",
    "synonyms": null,
    "name": null,
    "reference": "GO_REF:0000120"
  }
]
```

### Implementing the IVCAP Service Wrapper

Our tool is stateless as well as requires little computational resources. In fact, most of the run time
will be spent to wait for the reply from the remote _QuickGO_ service. In short it can easily process many requests in
parallel and is an excellent candidate for a FaaS type service. In practical terms, we will implement a web service
which will receive requests as `POST` events and return the result in JOSN format.

Therefore, our plan is as follows:

* Create a new file `service.py`
* Define a FastAPI instance
* Define the Request as well as Result models
* Implement the IVCAP service wrapper around the previously defined `fetch_go_terms` function
* "Publish" the service implementation
* Add imports and other housekeeping requirements
* Add code to start the server

#### Define a FastAPI instance

We will use the [FastAPI](https://fastapi.tiangolo.com/) to implement our web service. To start, we define the
`FastAPI` instance in a new file `service.py`.

```python
import os
from fastapi import FastAPI

title="Gene Ontology (GO) Term Mapper"
description = """This service maps a set of protein or gene identifiers (typically UniProt IDs)
to their corresponding Gene Ontology (GO) annotations using the QuickGO REST API.
It can filter results by specific GO categories and is optimized for
multi-ID batch processing."""

app = FastAPI(
    title=title,
    description=description,
    version=os.environ.get("VERSION", "???"),
    contact={
        "name": "Mary Doe",
        "email": "mary.doe@acme.au",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/license/MIT",
    },
    docs_url="/api",
)
```

#### Define the Request as well as Result models

We already have implemented our function, but need more formally define the _shape_ or _schema_ of the incoming request
as well as the reply. For that, we will add the two models `Request` and `Result`
using the additional functionality from the [Pydantic](https://docs.pydantic.dev/latest/) library to
make them more self-descriptive:

```python
from typing import List, Dict, Optional
from pydantic import BaseModel, ConfigDict, Field

class Request(BaseModel):
    jschema: str = Field("urn:sd:schema.gene-ontology-term-mapper.request.1", alias="$schema")
    ids: List[str] = Field(description="List of UniProt IDs")
    category: Optional[str] = Field(None, description="GO category: BP, MF, or CC")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "$schema": "urn:sd:schema.gene-ontology-term-mapper.request.1",
            "ids": [ "P12345", "Q9H0H5" ],
            "category": "BP"
        }
    })

class Result(BaseModel):
    jschema: str = Field("urn:sd:schema.gene-ontology-term-mapper.1", alias="$schema")
    results: Dict[str, List[Annotation]] = Field(description="contains a list of annotations for every UniProt ID")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "$schema": "urn:sd:schema.gene-ontology-term-mapper.1",
                "results": {
                    "P12345": [{
                        "id": "UniProtKB:P12345!296618610",
                        "geneProductId": "UniProtKB:P12345",
                        "qualifier": "involved_in",
                        "goId": "GO:0006103",
                        "goAspect": "biological_process",
                        "goEvidence": "ISS",
                        "assignedBy": "UniProt",
                        "symbol": "GOT2",
                        "reference": "GO_REF:0000024"
                    }]
                }
            }
        },
    )
```

#### Implement the IVCAP service wrapper around the previously defined `fetch_go_terms` function

We now implement the "wrapper" function which takes the above `Request` instance, calls the previously defined
`fetch_go_terms` function for each of the requested UniProt IDs and assembles the result. PLease note that we
are adding a quite extensive 'doc_string' to the function. The IVCAP SDK will use this as the tool description
accessible to the various agent frameworks.

```python
import asyncio
from go_term_fetcher import Annotation, fetch_go_terms, filter_by_category

async def map_go_terms(
    req: Request
) -> Result:
    """This function maps a set of protein or gene identifiers (typically UniProt IDs)
    to their corresponding Gene Ontology (GO) annotations using the QuickGO REST API.
    It can filter results by specific GO categories and is optimized for
    multi-ID batch processing.

    Supported high-level are:
    * GO categories are Biological Process (BP)
    * Molecular Function (MF)
    * Cellular Component (CC)

    Typical use-cases for this function are:
    * Enriching gene or protein datasets with structured functional annotations
    * Supporting biological data exploration or hypothesis generation
    * Downstream graph or network construction for biological analysis
"""
    results = {}

    async def fetch_and_filter(uid):
        terms = await fetch_go_terms(uid)
        filtered = filter_by_category(terms, req.category) if req.category else terms
        results[uid] = filtered

    await asyncio.gather(*(fetch_and_filter(i) for i in req.ids))
    return Result(results=results)
```

#### Publish the service implementation

The following function registers the service implementation `map_go_terms` with the IVCAP service library.

The first argument is the above defined `FastAPI` variable, `"/"` indicates that this service is published
at the root of the URL. Finally, `opts` allow for additional customisation. See the IVCAP service docs for more
details.

```python
from ivcap_ai_tool import add_tool_api_route, ToolOptions

add_tool_api_route(app, "/", map_go_terms, opts=ToolOptions(tags=["GO Term Mapper"]))
```

#### Add housekeeping requirements

WHat remains missing is initialising the logger and creating one for local consumption. Best to put this at the
beginning of the file.

```python
from ivcap_fastapi import getLogger, logging_init

logging_init()
logger = getLogger("app")
```

#### Add code to start the server

Now that we have everything in place, we need to start the http server.

```python
if __name__ == "__main__":
    from ivcap_ai_tool import start_tool_server

    start_tool_server(app, map_go_terms)
```
