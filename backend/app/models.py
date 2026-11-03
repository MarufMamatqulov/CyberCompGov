from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Agency(Base):
    __tablename__ = "agencies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(32), unique=True)
    name: Mapped[str] = mapped_column(String(255))
    category: Mapped[str] = mapped_column(String(16))  # "MII" | "Oddiy"
    region: Mapped[str] = mapped_column(String(128))
    norm_threshold: Mapped[float] = mapped_column(Float)

    officers: Mapped[list["IctOfficer"]] = relationship(back_populates="agency")


class IctOfficer(Base):
    __tablename__ = "ict_officers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    pinfl: Mapped[str] = mapped_column(String(14), unique=True)
    full_name: Mapped[str] = mapped_column(String(255))
    position: Mapped[str] = mapped_column(String(255))
    agency_id: Mapped[int] = mapped_column(ForeignKey("agencies.id"))
    experience_years: Mapped[int] = mapped_column(Integer, default=0)
    role: Mapped[str] = mapped_column(String(16), default="officer")  # "admin" | "officer"
    group: Mapped[str] = mapped_column(String(16), default="ministry")  # ministry | regional | district
    username: Mapped[str] = mapped_column(String(64), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))

    agency: Mapped[Agency] = relationship(back_populates="officers")
    sessions: Mapped[list["EvalSession"]] = relationship(back_populates="officer", order_by="EvalSession.created_at")


class CompetencyBlock(Base):
    __tablename__ = "competency_blocks"

    code: Mapped[str] = mapped_column(String(4), primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    ahp_weight: Mapped[float] = mapped_column(Float)
    alpha_k: Mapped[float] = mapped_column(Float)
    beta_s: Mapped[float] = mapped_column(Float)
    gamma_a: Mapped[float] = mapped_column(Float)
    min_threshold: Mapped[float | None] = mapped_column(Float, nullable=True)


class KsaIndicator(Base):
    __tablename__ = "ksa_indicators"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    block_code: Mapped[str] = mapped_column(ForeignKey("competency_blocks.code"))
    sub_code: Mapped[str] = mapped_column(String(8), unique=True)
    sub_name: Mapped[str] = mapped_column(String(255))
    k_code: Mapped[str] = mapped_column(String(8))
    k_desc: Mapped[str] = mapped_column(Text)
    s_code: Mapped[str] = mapped_column(String(8))
    s_desc: Mapped[str] = mapped_column(Text)
    a_code: Mapped[str] = mapped_column(String(8))
    a_desc: Mapped[str] = mapped_column(Text)
    nist_ref: Mapped[str] = mapped_column(String(255), default="")
    ecsf_ref: Mapped[str] = mapped_column(String(255), default="")
    law_ref: Mapped[str] = mapped_column(String(255), default="")


class QuestionItem(Base):
    """K (test), S (laboratoriya) va A (situatsion keys) topshiriqlari."""

    __tablename__ = "questions_bank"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(32), unique=True)
    kind: Mapped[str] = mapped_column(String(8))  # "test" | "lab" | "case"
    block_code: Mapped[str] = mapped_column(ForeignKey("competency_blocks.code"))
    sub_code: Mapped[str] = mapped_column(String(8))
    title: Mapped[str] = mapped_column(String(255))
    order: Mapped[int] = mapped_column(Integer, default=0)
    payload_json: Mapped[dict] = mapped_column(JSON)  # nomzodga ko‘rsatiladigan qism
    answer_json: Mapped[dict] = mapped_column(JSON)  # faqat serverda: to‘g‘ri javoblar va baholash qoidalari


class EvalSession(Base):
    __tablename__ = "eval_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    verify_code: Mapped[str] = mapped_column(String(32), unique=True)
    officer_id: Mapped[int] = mapped_column(ForeignKey("ict_officers.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    duration_minutes: Mapped[float] = mapped_column(Float, default=0)
    k_scores_json: Mapped[dict] = mapped_column(JSON)
    s_scores_json: Mapped[dict] = mapped_column(JSON)
    a_scores_json: Mapped[dict] = mapped_column(JSON)
    sub_scores_json: Mapped[dict] = mapped_column(JSON, default=dict)
    details_json: Mapped[dict] = mapped_column(JSON, default=dict)
    c1_score: Mapped[float] = mapped_column(Float)
    c2_score: Mapped[float] = mapped_column(Float)
    c3_score: Mapped[float] = mapped_column(Float)
    c4_score: Mapped[float] = mapped_column(Float)
    i_axk: Mapped[float] = mapped_column(Float)
    phi_flag: Mapped[int] = mapped_column(Integer)
    level_name: Mapped[str] = mapped_column(String(128))
    decision_text: Mapped[str] = mapped_column(Text)
    norm_threshold: Mapped[float] = mapped_column(Float, default=80.0)
    # "before" / "after" — eksperiment (3.3-jadval); "attestatsiya" — tizimda jonli topshirilgan
    stage: Mapped[str] = mapped_column(String(16), default="attestatsiya")

    officer: Mapped[IctOfficer] = relationship(back_populates="sessions")
    gaps: Mapped[list["SkillGapPlan"]] = relationship(back_populates="session", cascade="all, delete-orphan")


class SkillGapPlan(Base):
    __tablename__ = "skill_gaps_plan"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("eval_sessions.id"))
    block_code: Mapped[str] = mapped_column(String(4))
    sub_code: Mapped[str] = mapped_column(String(8), default="")
    delta_c: Mapped[float] = mapped_column(Float)
    assigned_course_title: Mapped[str] = mapped_column(String(255))
    course_hours: Mapped[int] = mapped_column(Integer)
    deadline_days: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(32), default="Tayinlangan")

    session: Mapped[EvalSession] = relationship(back_populates="gaps")
