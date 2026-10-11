from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    DateTime
)

from sqlalchemy.orm import declarative_base, sessionmaker

from datetime import datetime

from tool import analyze_complaint


# ============================================================
# FASTAPI
# ============================================================

app = FastAPI(
    title="AI Complaint Prioritization API",
    version="1.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# DATABASE
# ============================================================

DATABASE_URL = "sqlite:///./complaints.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


# ============================================================
# DATABASE MODEL
# ============================================================

class ComplaintModel(Base):

    __tablename__ = "complaints"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(100),
        nullable=False
    )

    email = Column(
        String(150),
        nullable=False
    )

    raw_text = Column(
        Text,
        nullable=False
    )

    category = Column(
        String(50),
        default="General"
    )

    priority = Column(
        String(30),
        default="Medium"
    )

    sentiment = Column(
        String(30),
        default="Neutral"
    )

    summary = Column(
        Text,
        default=""
    )

    status = Column(
        String(30),
        default="Unsolved"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


Base.metadata.create_all(bind=engine)


# ============================================================
# REQUEST MODELS
# ============================================================

class ComplaintCreate(BaseModel):

    name: str

    email: str

    category: str = "General"

    text: str


class StatusUpdate(BaseModel):

    status: str


# ============================================================
# HELPER
# ============================================================

def normalize_priority(priority):

    if not priority:
        return "Medium"

    priority = priority.strip().lower()

    if priority in ["light", "low"]:
        return "Light"

    if priority in [
        "critical",
        "urgent",
        "high"
    ]:
        return "Critical"

    return "Medium"


def serialize_complaint(complaint):

    return {
        "id": complaint.id,

        "ticket_id":
            f"CMP-{complaint.id:06d}",

        "name":
            complaint.name,

        "email":
            complaint.email,

        "text":
            complaint.raw_text,

        "category":
            complaint.category,

        "priority":
            complaint.priority,

        "sentiment":
            complaint.sentiment,

        "summary":
            complaint.summary,

        "status":
            complaint.status,

        "created_at":
            complaint.created_at.isoformat()
            if complaint.created_at
            else None
    }


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {
        "message":
            "AI Complaint Prioritization API is running"
    }


# ============================================================
# CREATE COMPLAINT
# ============================================================

@app.post("/complaints/")
def create_complaint(payload: ComplaintCreate):

    if not payload.name.strip():

        raise HTTPException(
            status_code=400,
            detail="Name is required"
        )

    if not payload.email.strip():

        raise HTTPException(
            status_code=400,
            detail="Email is required"
        )

    if not payload.text.strip():

        raise HTTPException(
            status_code=400,
            detail="Complaint text is required"
        )

    # AI analysis
    analysis = analyze_complaint(
        payload.text,
        payload.category
    )

    priority = normalize_priority(
        analysis.get("priority")
    )

    db = SessionLocal()

    try:

        complaint = ComplaintModel(

            name=payload.name.strip(),

            email=payload.email.strip(),

            raw_text=payload.text.strip(),

            category=analysis.get(
                "category",
                "General"
            ),

            priority=priority,

            sentiment=analysis.get(
                "sentiment",
                "Neutral"
            ),

            summary=analysis.get(
                "summary",
                ""
            ),

            status="Unsolved",

            created_at=datetime.utcnow()
        )

        db.add(complaint)

        db.commit()

        db.refresh(complaint)

        return serialize_complaint(
            complaint
        )

    finally:

        db.close()


# ============================================================
# GET ALL COMPLAINTS
# ============================================================

@app.get("/complaints/")
def get_complaints():

    db = SessionLocal()

    try:

        complaints = (
            db.query(ComplaintModel)
            .order_by(
                ComplaintModel.id.desc()
            )
            .all()
        )

        return [
            serialize_complaint(c)
            for c in complaints
        ]

    finally:

        db.close()


# ============================================================
# GET SINGLE COMPLAINT
# ============================================================

@app.get("/complaints/{complaint_id}")
def get_complaint(
    complaint_id: int
):

    db = SessionLocal()

    try:

        complaint = (
            db.query(ComplaintModel)
            .filter(
                ComplaintModel.id ==
                complaint_id
            )
            .first()
        )

        if not complaint:

            raise HTTPException(
                status_code=404,
                detail="Complaint not found"
            )

        return serialize_complaint(
            complaint
        )

    finally:

        db.close()


# ============================================================
# UPDATE STATUS
# ============================================================

@app.patch(
    "/complaints/{complaint_id}/status"
)
def update_status(
    complaint_id: int,
    payload: StatusUpdate
):

    allowed_statuses = [
        "Unsolved",
        "Ongoing",
        "Resolved"
    ]

    if payload.status not in allowed_statuses:

        raise HTTPException(
            status_code=400,
            detail="Invalid status"
        )

    db = SessionLocal()

    try:

        complaint = (
            db.query(ComplaintModel)
            .filter(
                ComplaintModel.id ==
                complaint_id
            )
            .first()
        )

        if not complaint:

            raise HTTPException(
                status_code=404,
                detail="Complaint not found"
            )

        complaint.status = payload.status

        db.commit()

        db.refresh(complaint)

        return serialize_complaint(
            complaint
        )

    finally:

        db.close()


# ============================================================
# RESOLVE COMPLAINT
# ============================================================

@app.patch(
    "/complaints/{complaint_id}/resolve"
)
def resolve_complaint(
    complaint_id: int
):

    db = SessionLocal()

    try:

        complaint = (
            db.query(ComplaintModel)
            .filter(
                ComplaintModel.id ==
                complaint_id
            )
            .first()
        )

        if not complaint:

            raise HTTPException(
                status_code=404,
                detail="Complaint not found"
            )

        complaint.status = "Resolved"

        db.commit()

        db.refresh(complaint)

        return serialize_complaint(
            complaint
        )

    finally:

        db.close()