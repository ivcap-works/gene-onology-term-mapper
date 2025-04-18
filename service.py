import os
from fastapi import FastAPI
from typing import List, Dict, Optional
import asyncio
from pydantic import BaseModel, ConfigDict, Field
from ivcap_fastapi import getLogger, logging_init
from ivcap_ai_tool import start_tool_server, add_tool_api_route, ToolOptions

from go_term_fetcher import Annotation, fetch_go_terms, filter_by_category

logging_init()
logger = getLogger("app")

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
                "$schema": "urn:sd:schema.is-prime.1",
                "number": 997,
                "is_prime": True
            },
        },
    )

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

add_tool_api_route(app, "/", map_go_terms, opts=ToolOptions(tags=["GO Term Mapper"]))

if __name__ == "__main__":
    start_tool_server(app, map_go_terms)
