import io
import logging
import time

from PIL import Image

from constants import Status
from database.models import Task, TaskResult
from database.utils import create_record, get_record_by_id, update_task_status

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s"
)


# def compress_image(
#     task: UploadedImageTask,
# ) -> bytes:
#     images = task.files
#     for _image in images:
#         file = _image.image_data

#         # Fetch these from task extras
#         width = 1000
#         quality = 90
#         target_format = "JPEG"

#         # Load the image from bytes
#         image = Image.open(BytesIO(file))

#         # Optionally resize if image is too large
#         if image.width > width:
#             ratio = width / float(image.width)
#             new_height = int(float(image.height) * ratio)
#             image = image.resize((width, new_height), Image.Resampling.LANCZOS)
#         # Convert to RGB for JPEG
#         if image.mode in ("RGBA", "P"):
#             image = image.convert("RGB")
#         time.sleep(20)

#         # Compress and save to bytes buffer
#         output_io = BytesIO()
#         image.save(output_io, format=target_format, quality=quality)
#         compressed_bytes = output_io.getvalue()

#         return compressed_bytes


def merge_images_to_pdf(task_id, task_files):
    # order files by order stored
    files = sorted(task_files, key=lambda x: x.order)
    images = []

    for image in files:
        img = Image.open(io.BytesIO(image.data)).convert("RGB")
        images.append(img)

    if not images:
        return None
    
    time.sleep(5)

    output_buffer = io.BytesIO()
    images[0].save(output_buffer, format="PDF", save_all=True, append_images=images[1:])
    pdf_bytes = output_buffer.getvalue()
    output_buffer.close()

    # Store task results
    task = get_record_by_id(task_id, Task)
    task_result = TaskResult(
        data=pdf_bytes,
        extension="application/pdf",
        task=task,
    )
    result = create_record(task_result, TaskResult)
    update_task_status(task_id, Status.COMPLETED.value)

    if not result:
        logging.info("Failed to store task result")
