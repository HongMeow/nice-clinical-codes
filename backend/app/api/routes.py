import asyncio
import logging
import time

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.graph.graph import run_pipeline

logger = logging.getLogger(__name__)

router = APIRouter()


# Request / Response schemas

class SearchRequest(BaseModel):
    query: str = Field(
        ...,
        description="Clinical condition query, e.g. 'type 2 diabetes with hypertension'",
        min_length=2,
        max_length=500,
    )


class CodeResult(BaseModel):
    code: str
    term: str
    vocabulary: str
    decision: str  # include, exclude, uncertain
    confidence: float
    rationale: str
    sources: list[str]
    usage_frequency: int | None = None
    classifier_score: float | None = None


class SearchResponse(BaseModel):
    query: str
    conditions_parsed: list[dict]
    results: list[CodeResult]
    summary: dict
    provenance_trail: list[dict]
    elapsed_seconds: float


# Endpoints

@router.post("/search", response_model=SearchResponse)
async def search_codes(request: SearchRequest):
    """Search for clinical codes matching a condition query."""
    t0 = time.time()

    try:
        result = await asyncio.to_thread(run_pipeline, request.query)
    except Exception as exc:
        logger.error("Pipeline failed: %s", exc)
        raise HTTPException(status_code=500, detail="Pipeline processing failed")

    elapsed = round(time.time() - t0, 2)
    final_codes = result.get("final_code_list", [])

    return SearchResponse(
        query=request.query,
        conditions_parsed=result.get("parsed_conditions", []),
        results=[
            CodeResult(
                code=c["code"],
                term=c["term"],
                vocabulary=c["vocabulary"],
                decision=c["decision"],
                confidence=c["confidence"],
                rationale=c["rationale"],
                sources=c.get("sources", []),
                usage_frequency=c.get("usage_frequency"),
                classifier_score=c.get("classifier_score"),
            )
            for c in final_codes
        ],
        summary=result.get("summary", {}),
        provenance_trail=result.get("provenance_trail", []),
        elapsed_seconds=elapsed,
    )


class ReviewRequest(BaseModel):
    search_id: str
    decisions: dict[str, str] = Field(
        ...,
        description="Map of code -> decision (include/exclude) for uncertain codes",
    )


@router.post("/review")
async def review_codes(request: ReviewRequest):
    """Submit human review decisions for uncertain codes."""
    # TODO: human-in-the-loop resume (NICE-033)
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.get("/export/{search_id}")
async def export_codes(search_id: str, output_format: str = "csv"):
    """Export a code list as CSV or Excel."""
    # TODO: implement export (NICE-023)
    raise HTTPException(status_code=501, detail="Not implemented yet")
