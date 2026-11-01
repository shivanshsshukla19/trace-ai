from typing import List, Optional
from pydantic import BaseModel, Field

class EdgeCase(BaseModel):
    scenario: str = Field(description="Description of the edge case input condition")
    impact: str = Field(description="Runtime consequence (e.g., TLE, SegFault, Wrong Answer)")
    fix_suggestion: str = Field(description="Concrete recommendation to handle this condition safely")

class CodeAnalysisRequest(BaseModel):
    code: str = Field(..., description="The user source code snippet")
    language: str = Field(default="cpp", description="Target programming language (e.g., cpp, python)")
    max_n: Optional[str] = Field(default="", description="Target problem constraints (e.g., N <= 10^5)")

class CodeAnalysisResponse(BaseModel):
    time_complexity: str = Field(description="Big-O time complexity (e.g., O(N^2), O(N log N))")
    time_complexity_reasoning: str = Field(description="Concise breakdown of loops or recurrence relation")
    space_complexity: str = Field(description="Big-O auxiliary space complexity (e.g., O(1), O(N))")
    space_complexity_reasoning: str = Field(description="Explanation of auxiliary heap/stack allocations")
    tle_risk: bool = Field(description="True if the code risks Time Limit Exceeded based on max_n constraints or common 10^8 operation limits")
    tle_verdict: str = Field(description="Detailed TLE prediction (e.g., 'PASSES: ~10^5 ops <= 10^8 limit' or 'TLE: ~10^10 ops > 10^8 cutoff')")
    edge_cases: List[EdgeCase] = Field(description="List of unhandled boundary conditions")
    optimized_code: str = Field(description="Refactored modern, idiomatic implementation")
    key_takeaway: str = Field(description="One-sentence core algorithmic insight")