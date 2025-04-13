import logging

from database.models import Session, Task, TaskResult

logger = logging.getLogger()


def get_task_details(id):
    session = Session()
    try:
        task = session.query(Task).get(id)
        # TODO: return instance alone
        return task.total_files, task.files, task.status, task.results
    except Exception as e:
        logger.exception(f"Error while fetching image record from db: {str(e)}")
    finally:
        session.close()


def fetch_task_results(task_id):
    session = Session()
    try:
        results = session.query(TaskResult).filter(TaskResult.task_id == task_id).all()
        logger.info("Fetched results")
        return results
    except Exception as e:
        logger.exception(f"Error while updating result status: {str(e)}")
    finally:
        session.close()


def update_task_status(id, status):
    session = Session()
    try:
        record = session.query(Task).get(id)
        record.status = status
        session.commit()
        logger.info("Commited result")
    except Exception as e:
        logger.exception(f"Error while updating result status: {str(e)}")
    finally:
        session.close()


def create_record(record, table):
    session = Session()
    try:
        session.add(record)
        session.commit()
        session.refresh(record)
        logger.info(f"{table.__tablename__} record has been created")
        return record
    except Exception as e:
        logger.exception(
            f"Error while adding {table.__tablename__} record to db: {str(e)}"
        )
    finally:
        session.close()


def get_record_by_id(id, table):
    session = Session()
    try:
        task = session.query(table).get(id)
        # TODO: Check if refresh is needed
        session.refresh(task)
        return task
    except Exception as e:
        logger.exception(
            f"Error while fetching {table.__tablename__} record from db: {str(e)}"
        )
    finally:
        session.close()
