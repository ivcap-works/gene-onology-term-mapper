#
# Copyright (c) 2025 Commonwealth Scientific and Industrial Research Organisation (CSIRO). All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file. See the AUTHORS file for names of contributors.
#
import os
from typing import List, Dict, Optional
import asyncio
from pydantic import BaseModel, ConfigDict, Field
from ivcap_service import getLogger, Service
from ivcap_ai_tool import start_tool_server, logging_init, ToolOptions, ivcap_ai_tool

from my_app.go_term_fetcher import Annotation, fetch_go_terms, filter_by_category

logging_init()
logger = getLogger("app")

service = Service(
    name="Gene Ontology (GO) Term Mapper",
    contact={
        "name": "Mary Doe",
        "email": "mary.doe@acme.au",
    },
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

@ivcap_ai_tool("/", opts=ToolOptions(tags=["GO Term Mapper"]))
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

if __name__ == "__main__":
    start_tool_server(service)
