"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-09-17

"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True, index=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("first_name", sa.String(100), nullable=False, server_default=""),
        sa.Column("last_name", sa.String(100), nullable=False, server_default=""),
        sa.Column("role", sa.String(30), nullable=False, server_default="user"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    op.create_table(
        "job_descriptions",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("owner_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("company", sa.String(150), nullable=True),
        sa.Column("raw_text", sa.Text, nullable=False),
        sa.Column("parsed", sa.JSON, nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    op.create_table(
        "resumes",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("owner_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("parent_id", sa.Integer, sa.ForeignKey("resumes.id"), nullable=True, index=True),
        sa.Column("job_description_id", sa.Integer, sa.ForeignKey("job_descriptions.id"), nullable=True),
        sa.Column("kind", sa.String(20), nullable=False, server_default="MASTER"),
        sa.Column("name", sa.String(255), nullable=False, server_default="Master Resume"),
        sa.Column("personal_info", sa.JSON, nullable=False),
        sa.Column("template_id", sa.String(50), nullable=False, server_default="classic"),
        sa.Column("font_family", sa.String(50), nullable=False, server_default="Calibri"),
        sa.Column("font_size_pt", sa.Float, nullable=False, server_default="11.0"),
        sa.Column("heading_size_pt", sa.Float, nullable=False, server_default="12.5"),
        sa.Column("line_spacing", sa.Float, nullable=False, server_default="1.15"),
        sa.Column("section_spacing_pt", sa.Float, nullable=False, server_default="10.0"),
        sa.Column("bullet_spacing_pt", sa.Float, nullable=False, server_default="3.0"),
        sa.Column("margin_in", sa.Float, nullable=False, server_default="0.65"),
        sa.Column("company", sa.String(150), nullable=True),
        sa.Column("role_title", sa.String(150), nullable=True),
        sa.Column("page_count", sa.Integer, nullable=True),
        sa.Column("last_ats_score", sa.Float, nullable=True),
        sa.Column("source_filename", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    op.create_table(
        "resume_sections",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("resume_id", sa.Integer, sa.ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("section_key", sa.String(80), nullable=False),
        sa.Column("type", sa.String(40), nullable=False),
        sa.Column("title", sa.String(150), nullable=False),
        sa.Column("order", sa.Integer, nullable=False, server_default="0"),
        sa.Column("visible", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("content", sa.JSON, nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    op.create_table(
        "resume_facts",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("resume_id", sa.Integer, sa.ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("fact_key", sa.String(150), nullable=False),
        sa.Column("value", sa.Text, nullable=False),
        sa.Column("locked", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    op.create_table(
        "ats_analysis",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("resume_id", sa.Integer, sa.ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("job_description_id", sa.Integer, sa.ForeignKey("job_descriptions.id"), nullable=True),
        sa.Column("overall_score", sa.Float, nullable=False),
        sa.Column("keyword_match_pct", sa.Float, nullable=False, server_default="0"),
        sa.Column("skills_match_pct", sa.Float, nullable=False, server_default="0"),
        sa.Column("title_match_pct", sa.Float, nullable=False, server_default="0"),
        sa.Column("experience_relevance_pct", sa.Float, nullable=False, server_default="0"),
        sa.Column("section_completeness_pct", sa.Float, nullable=False, server_default="0"),
        sa.Column("parsing_accuracy_pct", sa.Float, nullable=False, server_default="0"),
        sa.Column("formatting_compatibility_pct", sa.Float, nullable=False, server_default="0"),
        sa.Column("readability_pct", sa.Float, nullable=False, server_default="0"),
        sa.Column("matched_keywords", sa.JSON, nullable=False),
        sa.Column("missing_keywords", sa.JSON, nullable=False),
        sa.Column("related_keywords", sa.JSON, nullable=False),
        sa.Column("formatting_warnings", sa.JSON, nullable=False),
        sa.Column("section_warnings", sa.JSON, nullable=False),
        sa.Column("suggestions", sa.JSON, nullable=False),
        sa.Column("parsing_checklist", sa.JSON, nullable=False),
        sa.Column("page_count", sa.Integer, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    op.create_table(
        "resume_exports",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("resume_id", sa.Integer, sa.ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("format", sa.String(10), nullable=False),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("storage_path", sa.String(500), nullable=False),
        sa.Column("page_count", sa.Integer, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    op.create_table(
        "ai_changes",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("resume_id", sa.Integer, sa.ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("target_path", sa.String(200), nullable=False),
        sa.Column("change_type", sa.String(40), nullable=False),
        sa.Column("original_value", sa.Text, nullable=False),
        sa.Column("suggested_value", sa.Text, nullable=False),
        sa.Column("rationale", sa.Text, nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="PENDING"),
        sa.Column("fabrication_risk", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("blocked_locked_field", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("ai_changes")
    op.drop_table("resume_exports")
    op.drop_table("ats_analysis")
    op.drop_table("resume_facts")
    op.drop_table("resume_sections")
    op.drop_table("resumes")
    op.drop_table("job_descriptions")
    op.drop_table("users")
