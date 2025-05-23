from pydantic import BaseModel
from typing import List


class AggregateRequest(BaseModel):
    """Request body for aggregation endpoint."""

    json_paths: List[str]
