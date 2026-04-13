from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class CandidateInput(BaseModel):
    filename: str
    content: str


class CandidateUrlInput(BaseModel):
    filename: str
    url: str


class JobInput(BaseModel):
    title: str = ""
    company: str = ""
    category: str = ""
    employment_type: str = ""
    skills: str = ""
    description: str = ""
    requirements: str = ""
    location: str = ""
    min_salary: str = ""
    max_salary: str = ""


class MatchTextRequest(BaseModel):
    job_description: str = Field(..., min_length=1)
    candidates: List[CandidateInput]


class MatchUrlsRequest(BaseModel):
    job: JobInput
    candidates: List[CandidateUrlInput]


class MatchDatasetFolderRequest(BaseModel):
    job: JobInput
    folder_path: Optional[str] = "dataset"



class RankedCandidateResponse(BaseModel):
    filename: str
    score: float
    preview: str
    source_type: Optional[str] = None
    is_scan_pdf: bool = False
    ocr_confidence: Optional[float] = None
    ocr_text_length: Optional[int] = None
    candidate_data: Optional[Dict[str, Any]] = None
    comparison_data: Optional[Dict[str, Any]] = None


class MatchTextResponse(BaseModel):
    total_valid_cvs: int
    ranked_candidates: List[RankedCandidateResponse]


class ErrorFileResponse(BaseModel):
    filename: str
    error: str


class MatchFilesResponse(BaseModel):
    job_description_preview: str
    total_valid_cvs: int
    total_invalid_files: int
    ranked_candidates: List[RankedCandidateResponse]
    errors: List[ErrorFileResponse]


class MatchDatasetRequest(BaseModel):
    job: JobInput
    folder_path: str = "dataset"


class MatchDatasetResponse(BaseModel):
    job_description_preview: str
    total_valid_cvs: int
    total_invalid_files: int
    processing_time_seconds: float
    cv_per_second: float
    ranked_candidates: List[RankedCandidateResponse]
    errors: List[ErrorFileResponse]