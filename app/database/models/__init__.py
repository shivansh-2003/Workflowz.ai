from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    team_members: Mapped[list["TeamMember"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class TeamMember(Base):
    __tablename__ = "teams"
    __table_args__ = (
        UniqueConstraint("organization_name", "email", name="teams_org_email_unique"),
        CheckConstraint(
            "position IN ('head', 'member')",
            name="teams_position_check",
        ),
    )

    organization_name: Mapped[str] = mapped_column(String(100), primary_key=True)
    member_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    designation: Mapped[Optional[str]] = mapped_column(String(100))
    position: Mapped[str] = mapped_column(String(50), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="team_members")


class Project(Base):
    __tablename__ = "projects"
    __table_args__ = (
        UniqueConstraint(
            "organization_name", "project_name", name="projects_org_name_unique"
        ),
        CheckConstraint(
            "project_progress BETWEEN 0 AND 100",
            name="projects_progress_range",
        ),
    )

    organization_name: Mapped[str] = mapped_column(String(100), primary_key=True)
    project_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    project_name: Mapped[str] = mapped_column(String(100), nullable=False)
    project_description: Mapped[Optional[str]] = mapped_column(Text)
    project_progress: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_by: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Task(Base):
    __tablename__ = "tasks"
    __table_args__ = (
        ForeignKeyConstraint(
            ["organization_name", "project_id"],
            ["projects.organization_name", "projects.project_id"],
            name="tasks_project_fk",
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["organization_name", "task_assigned_to"],
            ["teams.organization_name", "teams.member_id"],
            name="tasks_assignee_fk",
            ondelete="RESTRICT",
        ),
        CheckConstraint(
            "task_importance IN ('high', 'medium', 'low') OR task_importance IS NULL",
            name="tasks_importance_check",
        ),
    )

    organization_name: Mapped[str] = mapped_column(String(100), primary_key=True)
    project_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    task_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_description: Mapped[str] = mapped_column(Text, nullable=False)
    task_deadline: Mapped[Optional[date]] = mapped_column(Date)
    task_assigned_to: Mapped[int] = mapped_column(Integer, nullable=False)
    task_importance: Mapped[Optional[str]] = mapped_column(String(50))
    task_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
