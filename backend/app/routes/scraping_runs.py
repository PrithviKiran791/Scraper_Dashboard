from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import ScrapingRun


router = APIRouter(
    prefix="/api/scraping-runs",
    tags=["Scraping Runs"],
)


@router.post("")
def start_scraping_run(
    source: str,
    db: Session = Depends(get_db),
):
    run = ScrapingRun(
        source=source,
        status="RUNNING",
        products_found=0,
        started_at=datetime.utcnow(),
    )

    db.add(run)
    db.commit()
    db.refresh(run)

    return {
        "id": run.id,
        "source": run.source,
        "status": run.status,
        "products_found": run.products_found,
        "started_at": run.started_at,
        "completed_at": run.completed_at,
    }


@router.patch("/{run_id}")
def complete_scraping_run(
    run_id: int,
    products_found: int,
    status: str,
    db: Session = Depends(get_db),
):
    run = db.get(ScrapingRun, run_id)

    if run is None:
        raise HTTPException(
            status_code=404,
            detail="Scraping run not found",
        )

    run.status = status
    run.products_found = products_found

    if status == "COMPLETED":
        run.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(run)

    return {
        "id": run.id,
        "source": run.source,
        "status": run.status,
        "products_found": run.products_found,
        "started_at": run.started_at,
        "completed_at": run.completed_at,
    } 