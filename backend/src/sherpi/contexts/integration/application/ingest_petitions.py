from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sherpi.application.analyze_petition import AnalyzePetition
from sherpi.application.persistence import AnalysisRecord, AnalysisRepository
from sherpi.contexts.integration.domain.ingestion import IngestJob, IngestStatus
from sherpi.contexts.integration.domain.ports import IngestJobRepository
from sherpi.contexts.integration.domain.source import PetitionSource
from sherpi.infrastructure.logging import get_logger

_log = get_logger("sherpi.integration")


class IngestPetitions:
    def __init__(
        self,
        source: PetitionSource,
        orchestrator: AnalyzePetition,
        analysis_repo: AnalysisRepository,
        job_repo: IngestJobRepository,
        max_pages: int = 300,
    ) -> None:
        self._source = source
        self._orchestrator = orchestrator
        self._analysis_repo = analysis_repo
        self._job_repo = job_repo
        self._max_pages = max_pages

    async def run(self, job: IngestJob) -> IngestJob:
        job.status = IngestStatus.RUNNING
        self._job_repo.save(job)
        _log.info("ingest.start", job_id=job.id, tribunal=job.tribunal)
        try:
            docs = await self._source.fetch(job.tribunal, job.date_from, job.date_to, limit=50)
            job.total = len(docs)
            self._job_repo.save(job)
            for doc in docs:
                try:
                    result = await self._orchestrator.run(
                        doc.content, max_pages=self._max_pages, rito=doc.rito
                    )
                    record = AnalysisRecord(
                        id=uuid.uuid4().hex,
                        created_at=datetime.now(UTC),
                        filename=f"{doc.process_number}.pdf",
                        result=result,
                    )
                    self._analysis_repo.save(record)
                    job.processed += 1
                except Exception as exc:
                    job.failed += 1
                    _log.warning(
                        "ingest.doc_failed",
                        job_id=job.id,
                        process=doc.process_number,
                        error=str(exc),
                    )
                finally:
                    self._job_repo.save(job)
            job.status = IngestStatus.DONE
        except Exception as exc:
            job.status = IngestStatus.FAILED
            job.error = str(exc)
            _log.error("ingest.job_failed", job_id=job.id, error=str(exc))
        finally:
            job.finished_at = datetime.now(UTC)
            self._job_repo.save(job)
        _log.info("ingest.done", job_id=job.id, processed=job.processed, failed=job.failed)
        return job
