from datetime import UTC, datetime
from uuid import uuid4

from fastapi import FastAPI

from .models import EventType, ExportModel

app = FastAPI()


@app.get("/api/1/exports", response_model=list[ExportModel])
def get_exports():
    return [
        ExportModel(
            type=EventType.STITCH,
            experiment_id="test",
            ref_id=uuid4(),
            uploaded_at=datetime.now(UTC),
        ),
    ]
