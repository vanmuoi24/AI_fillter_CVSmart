from typing import List
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import os
import time
from app.schemas.cv_schema import (
    MatchTextRequest,
    MatchTextResponse,
    MatchFilesResponse,
    MatchUrlsRequest,
    MatchDatasetRequest,
MatchDatasetResponse
)
from app.services.matching_service import MatchingService
from app.utils.file_parser import (
    extract_text_from_upload,
    extract_text_from_url,
    extract_text_from_local_file   # 🔥 THÊM DÒNG NÀY
)

router = APIRouter(prefix="/cv", tags=["CV Matching"])


@router.get("/health")
def health_check():
    return {"status": "ok", "message": "CV Screening API is running"}


@router.post("/match-text", response_model=MatchTextResponse)
async def match_cv_text(payload: MatchTextRequest):
    valid_candidates = []

    for candidate in payload.candidates:
        if candidate.content.strip():
            valid_candidates.append({
                "filename": candidate.filename,
                "content": candidate.content
            })

    if not valid_candidates:
        raise HTTPException(status_code=400, detail="Không có candidate hợp lệ")

    ranked_results = MatchingService.compute_similarity(
        payload.job_description,
        valid_candidates
    )

    return MatchTextResponse(
        total_valid_cvs=len(valid_candidates),
        ranked_candidates=ranked_results
    )


@router.post("/match-files", response_model=MatchFilesResponse)
async def match_cv_files(
    job_description: str = Form(...),
    files: List[UploadFile] = File(...)
):
    if not files:
        raise HTTPException(status_code=400, detail="Vui lòng upload ít nhất 1 CV")

    cvs = []
    errors = []

    for file in files:
        try:
            text = await extract_text_from_upload(file)

            if not text.strip():
                errors.append({
                    "filename": file.filename,
                    "error": "Không trích xuất được nội dung"
                })
                continue

            cvs.append({
                "filename": file.filename,
                "content": text
            })
        except Exception as e:
            errors.append({
                "filename": file.filename,
                "error": str(e)
            })

    if not cvs:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Không có CV hợp lệ để xử lý",
                "errors": errors
            }
        )

    ranked_results = MatchingService.compute_similarity(job_description, cvs)

    return MatchFilesResponse(
        job_description_preview=job_description[:300],
        total_valid_cvs=len(cvs),
        total_invalid_files=len(errors),
        ranked_candidates=ranked_results,
        errors=errors
    )

@router.post("/match-urls", response_model=MatchFilesResponse)
async def match_cv_urls(payload: MatchUrlsRequest):
    job_description = MatchingService.build_job_description(payload.job.dict())

    cvs = []
    errors = []

    for candidate in payload.candidates:
        try:
            extracted = extract_text_from_url(candidate.url, candidate.filename)

            text = extracted.get("content", "")
            if not text.strip():
                errors.append({
                    "filename": candidate.filename,
                    "error": "Không trích xuất được nội dung"
                })
                continue

            cvs.append({
                "filename": candidate.filename,
                "content": text,
                "source_type": extracted.get("source_type", "unknown"),
                "is_scan_pdf": extracted.get("is_scan_pdf", False),
                "ocr_confidence": extracted.get("ocr_confidence"),
                "ocr_text_length": extracted.get("ocr_text_length", len(text))
            })

        except Exception as e:
            errors.append({
                "filename": candidate.filename,
                "error": str(e)
            })

    if not cvs:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Không có CV hợp lệ để xử lý",
                "errors": errors
            }
        )

    ranked_results = MatchingService.compute_similarity(
        job_description=job_description,
        cvs=cvs,
        job=payload.job.dict()
    )

    return MatchFilesResponse(
        job_description_preview=job_description[:300],
        total_valid_cvs=len(cvs),
        total_invalid_files=len(errors),
        ranked_candidates=ranked_results,
        errors=errors
    )
    
@router.post("/match-dataset", response_model=MatchDatasetResponse)
async def match_dataset(payload: MatchDatasetRequest):
    start_time = time.time()

    job_description = MatchingService.build_job_description(payload.job.model_dump())

    folder_path = payload.folder_path or "dataset"

    if not os.path.exists(folder_path):
        raise HTTPException(status_code=400, detail=f"Không tìm thấy thư mục: {folder_path}")

    if not os.path.isdir(folder_path):
        raise HTTPException(status_code=400, detail=f"Đây không phải thư mục: {folder_path}")

    cvs = []
    errors = []

    supported_extensions = (".pdf", ".docx", ".txt")

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        if not os.path.isfile(file_path):
            continue

        if not filename.lower().endswith(supported_extensions):
            continue

        try:
            text = extract_text_from_local_file(file_path)

            if not text.strip():
                errors.append({
                    "filename": filename,
                    "error": "Không trích xuất được nội dung"
                })
                continue

            cvs.append({
                "filename": filename,
                "content": text
            })
        except Exception as e:
            errors.append({
                "filename": filename,
                "error": str(e)
            })

    if not cvs:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Không có CV hợp lệ trong dataset",
                "errors": errors
            }
        )

    ranked_results = MatchingService.compute_similarity(job_description, cvs)

    end_time = time.time()
    processing_time = round(end_time - start_time, 3)
    cv_per_second = round(len(cvs) / processing_time, 2) if processing_time > 0 else 0.0

    return MatchDatasetResponse(
        job_description_preview=job_description[:300],
        total_valid_cvs=len(cvs),
        total_invalid_files=len(errors),
        processing_time_seconds=processing_time,
        cv_per_second=cv_per_second,
        ranked_candidates=ranked_results,
        errors=errors
    )