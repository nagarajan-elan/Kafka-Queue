import json
import logging
import time

from kafka import KafkaConsumer, KafkaProducer

from constants import Status
from database.utils import get_task_details
from utils import merge_images_to_pdf

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s"
)

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)


def merge_images_to_pdf_runner():
    consumer = KafkaConsumer(
        "test-topic",
        bootstrap_servers="localhost:9092",
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    )

    for msg in consumer:
        msg_data = msg.value
        logging.info(f">> msg: {msg_data} ")

        task_id = msg_data["task_id"]
        total_files, task_files, task_status, task_results = get_task_details(task_id)

        if total_files == len(task_files) and task_status == Status.PENDING.value:
            logging.info(f">> Starting Task: {task_id} at {time.time()}")
            merge_images_to_pdf(task_id, task_files)
            logging.info(f">> Completed Task: {task_id} at {time.time()}")
        else:
            logging.info("Skipped...")
            continue
