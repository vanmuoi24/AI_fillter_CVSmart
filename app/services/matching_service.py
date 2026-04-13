import re
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.utils.text_processor import normalize_text, is_english


class MatchingService:
    @staticmethod
    def build_job_description(job: Dict[str, Any]) -> str:
        job_parts = []

        if job.get("title"):
            title = job["title"]
            job_parts.append(f"Job title: {title}")
            job_parts.append(f"Job title: {title}")

        if job.get("skills"):
            skills = job["skills"]
            job_parts.append(f"Skills: {skills}")
            job_parts.append(f"Skills: {skills}")
            job_parts.append(f"Skills: {skills}")

        if job.get("description"):
            job_parts.append(f"Job description: {job['description']}")

        if job.get("requirements"):
            job_parts.append(f"Requirements: {job['requirements']}")
            job_parts.append(f"Requirements: {job['requirements']}")

        return "\n".join(job_parts)

    @staticmethod
    def extract_keywords(text: str) -> List[str]:
        if not text:
            return []

        separators = [",", "\n", ";", "|", "/", "-"]
        cleaned = text.lower()

        for sep in separators:
            cleaned = cleaned.replace(sep, ",")

        keywords = [item.strip() for item in cleaned.split(",") if item.strip()]
        return list(dict.fromkeys(keywords))

    @staticmethod
    def extract_email(text: str) -> str:
        match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        return match.group(0) if match else ""

    @staticmethod
    def extract_phone(text: str) -> str:
        match = re.search(r'(\+?\d[\d\-\s]{8,}\d)', text)
        return match.group(0).strip() if match else ""

    @staticmethod
    def extract_candidate_name(filename: str, content: str) -> str:
        lines = [line.strip() for line in content.splitlines() if line.strip()]
        if lines:
            first_line = lines[0]
            if len(first_line.split()) <= 6:
                return first_line
        return filename.rsplit(".", 1)[0]

    @staticmethod
    def guess_job_title(content: str) -> str:
        lines = [line.strip() for line in content.splitlines() if line.strip()]
        if len(lines) >= 2:
            return lines[1][:100]
        return ""

    @staticmethod
    def compute_similarity(
        job_description: str,
        cvs: List[Dict[str, Any]],
        job: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        if not job_description.strip():
            raise ValueError("Job description không được để trống")

        if not cvs:
            raise ValueError("Danh sách CV rỗng")

        jd_clean = normalize_text(job_description)
        cv_texts = [normalize_text(cv.get("content", "")) for cv in cvs]

        corpus = [jd_clean] + cv_texts
        is_en = is_english(job_description)

        vectorizer = TfidfVectorizer(
            stop_words="english" if is_en else None,
            ngram_range=(1, 2),
            max_features=5000
        )

        tfidf_matrix = vectorizer.fit_transform(corpus)
        jd_vector = tfidf_matrix[0:1]
        cv_vectors = tfidf_matrix[1:]
        scores = cosine_similarity(jd_vector, cv_vectors).flatten()

        job_skills = []
        job_title = ""

        if job:
            job_title = job.get("title", "")
            if job.get("skills"):
                if isinstance(job["skills"], list):
                    job_skills = [str(skill).strip().lower() for skill in job["skills"] if str(skill).strip()]
                else:
                    job_skills = MatchingService.extract_keywords(str(job["skills"]))

        results = []
        for cv, score in zip(cvs, scores):
            raw_score = float(score)
            content = cv.get("content", "")
            content_lower = content.lower()

            matched_skills = [skill for skill in job_skills if skill in content_lower]
            missing_skills = [skill for skill in job_skills if skill not in content_lower]

            candidate_name = MatchingService.extract_candidate_name(
                cv.get("filename", ""),
                content
            )

            results.append({
                "filename": cv.get("filename", ""),
                "score": round(min(raw_score * 30, 10), 2),
                "preview": content[:300],
                "source_type": cv.get("source_type", "unknown"),
                "is_scan_pdf": cv.get("is_scan_pdf", False),
                "ocr_confidence": cv.get("ocr_confidence"),
                "ocr_text_length": cv.get("ocr_text_length", len(content)),
                "candidate_data": {
                    "name": candidate_name,
                    "email": MatchingService.extract_email(content),
                    "phone": MatchingService.extract_phone(content),
                    "job_title": MatchingService.guess_job_title(content),
                    "skills": matched_skills,
                    "raw_text_length": len(content)
                },
                "comparison_data": {
                    "job_title": job_title,
                    "job_skills": job_skills,
                    "matched_skills": matched_skills,
                    "missing_skills": missing_skills,
                    "match_percent": round(raw_score * 100, 2)
                }
            })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results