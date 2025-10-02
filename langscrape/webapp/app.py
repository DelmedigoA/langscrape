"""Flask application that powers the lightweight Langscrape UI."""

from __future__ import annotations

import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from threading import Lock
from typing import Dict, List, Optional

from flask import Flask, jsonify, render_template, request

from .pipeline import DEFAULT_FIELDS, run_extraction


@dataclass
class Record:
    """Represents the extraction state for a single URL."""

    url: str
    fields: Dict[str, str] = field(default_factory=dict)
    status: str = "pending"
    error: Optional[str] = None


@dataclass
class Job:
    """Tracks the lifecycle of a batch of URL extractions."""

    id: str
    urls: List[str]
    records: List[Record]
    status: str = "pending"
    error: Optional[str] = None

    def asdict(self) -> Dict[str, object]:
        return {
            "id": self.id,
            "status": self.status,
            "error": self.error,
            "records": [
                {
                    "url": record.url,
                    "status": record.status,
                    "error": record.error,
                    "fields": record.fields,
                }
                for record in self.records
            ],
        }


_executor: Optional[ThreadPoolExecutor] = None
_jobs: Dict[str, Job] = {}
_jobs_lock = Lock()


def _get_executor() -> ThreadPoolExecutor:
    global _executor
    if _executor is None:
        _executor = ThreadPoolExecutor(max_workers=2)
    return _executor


def _create_job(urls: List[str]) -> Job:
    job_id = uuid.uuid4().hex
    records = [
        Record(
            url=url,
            fields={field: "" for field in DEFAULT_FIELDS},
        )
        for url in urls
    ]
    job = Job(id=job_id, urls=urls, records=records)
    with _jobs_lock:
        _jobs[job_id] = job
    return job


def _process_job(job_id: str) -> None:
    from langscrape.utils import load_config, get_llm

    with _jobs_lock:
        job = _jobs.get(job_id)
    if job is None:
        return

    with _jobs_lock:
        job.status = "running"
    config = None
    try:
        config = load_config()
        llm = get_llm(config)
    except Exception as exc:  # pragma: no cover - defensive guard for runtime issues
        error_message = f"Failed to initialise LLM: {exc}".strip()
        with _jobs_lock:
            job.status = "failed"
            job.error = error_message
            for record in job.records:
                record.status = "error"
                record.error = error_message
        return

    has_error = False
    for record in job.records:
        with _jobs_lock:
            record.status = "running"

        try:
            result = run_extraction(url=record.url, config=config, llm=llm)
        except Exception as exc:  # pragma: no cover - runtime guard
            has_error = True
            message = str(exc)
            with _jobs_lock:
                record.status = "error"
                record.error = message
        else:
            with _jobs_lock:
                record.fields.update(result)
                record.status = "completed"

    with _jobs_lock:
        job.status = "completed_with_errors" if has_error else "completed"
        job.error = "Some URLs failed to process." if has_error else None


def create_app() -> Flask:
    """Create and configure the Flask application."""

    app = Flask(
        __name__,
        static_folder="static",
        template_folder="templates",
    )

    @app.route("/")
    def index():
        return render_template("index.html", columns=DEFAULT_FIELDS)

    @app.post("/api/jobs")
    def create_job():
        payload = request.get_json(force=True, silent=True) or {}
        urls = payload.get("urls", [])
        if not isinstance(urls, list):
            return jsonify({"error": "`urls` must be an array of strings."}), 400

        cleaned_urls = [url.strip() for url in urls if isinstance(url, str) and url.strip()]
        if not cleaned_urls:
            return jsonify({"error": "Please provide at least one URL."}), 400

        job = _create_job(cleaned_urls)
        executor = _get_executor()
        executor.submit(_process_job, job.id)
        return jsonify({"columns": DEFAULT_FIELDS, **job.asdict()}), 201

    @app.get("/api/jobs/<job_id>")
    def get_job(job_id: str):
        with _jobs_lock:
            job = _jobs.get(job_id)
        if job is None:
            return jsonify({"error": "Job not found."}), 404
        return jsonify({"columns": DEFAULT_FIELDS, **job.asdict()})

    return app


__all__ = ["create_app"]
