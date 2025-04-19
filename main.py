import threading
from io import BytesIO
from typing import Annotated

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from constants import Status
from database.models import File as UploadedFile
from database.models import Task, TaskResult
from database.utils import create_record, fetch_task_results, get_record_by_id
from kafka_utils import merge_images_to_pdf_runner, producer
from schemas import TaskPayload
from utils import logging

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # List of allowed origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)


@app.get("/")
def root():
    return {"Hello": "World"}


@app.post("/task")
def create_task(
    paylod: TaskPayload,
):
    task = Task(
        action=paylod.action,
        total_files=paylod.total_files,
    )
    task = create_record(task, Task)
    if not task:
        return {"error": "Failed to create task"}
    return {"task_id": task.id}


@app.post("/upload-file")
def upload_file(
    file: Annotated[UploadFile, File()],
    task_id: Annotated[str, Form()],
    order: Annotated[int, Form()],
    action: Annotated[str, Form()],
):
    file_data = file.file.read()
    task = get_record_by_id(task_id, Task)
    if not task:
        return {"message": "Invalid task id"}

    file_record = UploadedFile(
        name=file.filename,
        extension=file.content_type,
        data=file_data,
        task=task,
        order=order,
    )
    create_record(file_record, UploadedFile)
    data = {"task_id": task_id}
    producer.send(action, data)
    return {"message": "Uploaded successfully"}


@app.get("/task/{task_id}")
def task_result(task_id: str):
    task = get_record_by_id(task_id, Task)
    if not task:
        return {"message": "Invalid task id"}

    if task.status == Status.COMPLETED.value:
        results = fetch_task_results(task_id)
        result_ids = [result.id for result in results]
        return {"status": Status.COMPLETED.value, "results": result_ids}

    else:
        return {"status": task.status}


@app.get("/task-result/{task_result_id}")
def download_result(task_result_id: str):
    result = get_record_by_id(task_result_id, TaskResult)

    pdf_bytes = result.data
    pdf_stream = BytesIO(pdf_bytes)

    return StreamingResponse(
        pdf_stream,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=file-{task_result_id}.pdf"
        },
    )


@app.on_event("startup")
def start_consumer_thread():
    thread = threading.Thread(target=merge_images_to_pdf_runner, daemon=True)
    thread.start()


# TODO:
# Write cleanup cron based on timestamp
# Fix event startup
# Add minimal FE
# Make consumers pluggable
