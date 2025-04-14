import uuid

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
    create_engine,
    func,
)
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()


class Task(Base):
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    action = Column(String, nullable=False)
    total_files = Column(Integer, default=1)
    status = Column(String, default="PENDING")
    created_at = Column(DateTime, default=func.now())
    extras = Column(JSON, default={})
    files = relationship("File", back_populates="task")
    results = relationship("TaskResult", back_populates="task")


class File(Base):
    __tablename__ = "uploaded_files"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    extension = Column(String, default="image/png")
    data = Column(LargeBinary, nullable=False)
    order = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    task = relationship("Task", back_populates="files")
    task_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
    )


class TaskResult(Base):
    __tablename__ = "task_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    data = Column(LargeBinary, nullable=False)
    order = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    extension = Column(String, default="image/png")
    task = relationship("Task", back_populates="results")
    task_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
    )


DATABASE_URL = "postgresql://myuser:mypass@localhost:5432/mydb"
engine = create_engine(DATABASE_URL)

# Base.metadata.drop_all(engine)
# This will create the table if it doesn't exist
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine, autocommit=False)
