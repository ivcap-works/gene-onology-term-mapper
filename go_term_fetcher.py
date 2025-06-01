#
# Copyright (c) 2025 Commonwealth Scientific and Industrial Research Organisation (CSIRO). All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file. See the AUTHORS file for names of contributors.
#
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

async def fetch_go_terms(uniprot_id: str) -> List[Annotation]:
    """Fetch the annotations for 'uniprot_id' from the QuickGO service."""
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

def filter_by_category(go_terms: List[Annotation], category: str) -> List[Annotation]:
    """If 'category' is in GO_CATEGORIES, filter the go_terms by that category."""
    if category not in GO_CATEGORIES:
        return go_terms
    return [t for t in go_terms if t.goAspect == GO_CATEGORIES[category]]


if __name__ == "__main__":
    import asyncio
    import json
    from fastapi.encoders import jsonable_encoder

    async def main():
        terms = await fetch_go_terms("P12345")
        print(json.dumps([jsonable_encoder(term) for term in terms[:3]], indent=2))
    asyncio.run(main())
