"""
Database models for Document AI system

Creates tables:
- documents: Văn bản nguồn (source documents)
- projects: Dự án báo cáo (report projects)
- ai_tasks: Lịch sử tác vụ AI (AI task history)
- report_sections: Các phần của báo cáo (report sections)
- statistical_data: Dữ liệu thống kê (statistical data)
- report_templates: Mẫu báo cáo (report templates)
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DECIMAL, TIMESTAMP, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Project(Base):
    """Dự án báo cáo"""
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(500), nullable=False)
    description = Column(Text)
    report_type = Column(String(100))  # periodic, special, summary, proposal
    department = Column(String(200))
    period = Column(String(100))  # "Tháng 12/2025", "Quý IV/2025", "Năm 2025"
    status = Column(String(50), default="draft")  # draft, in_progress, review, completed
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    documents = relationship("Document", back_populates="project", cascade="all, delete-orphan")
    ai_tasks = relationship("AITask", back_populates="project", cascade="all, delete-orphan")
    report_sections = relationship("ReportSection", back_populates="project", cascade="all, delete-orphan")
    statistical_data = relationship("StatisticalData", back_populates="project", cascade="all, delete-orphan")
    user = relationship("User", back_populates="projects")


class Document(Base):
    """Văn bản nguồn"""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    title = Column(String(500), nullable=False)
    file_type = Column(String(50))  # pdf, docx, txt, image
    file_path = Column(String(500))
    file_size = Column(Integer)
    extracted_text = Column(Text)
    doc_metadata = Column(JSON)  # {pages: 10, word_count: 5000, ...}
    status = Column(String(50), default="uploaded")  # uploaded, processing, extracted, error
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    project = relationship("Project", back_populates="documents")
    user = relationship("User")


class AITask(Base):
    """Lịch sử tác vụ AI"""
    __tablename__ = "ai_tasks"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    task_type = Column(String(100), nullable=False)  # extract, analyze, compare, generate, refine
    task_group = Column(String(50))  # group_1, group_2, group_3
    input_data = Column(JSON)  # {documents: [...], parameters: {...}}
    prompt = Column(Text)
    ai_response = Column(Text)
    tokens_used = Column(Integer)
    cost_vnd = Column(DECIMAL(10, 2))
    status = Column(String(50), default="pending")  # pending, processing, completed, error
    error_message = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())
    completed_at = Column(TIMESTAMP)

    # Relationships
    project = relationship("Project", back_populates="ai_tasks")
    user = relationship("User")


class ReportSection(Base):
    """Các phần của báo cáo"""
    __tablename__ = "report_sections"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    section_type = Column(String(100))  # introduction, overview, statistics, evaluation, challenges, recommendations, conclusion
    section_order = Column(Integer)
    title = Column(String(500))
    content = Column(Text)
    ai_generated = Column(Boolean, default=False)
    reviewed = Column(Boolean, default=False)
    version = Column(Integer, default=1)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    project = relationship("Project", back_populates="report_sections")


class StatisticalData(Base):
    """Dữ liệu thống kê"""
    __tablename__ = "statistical_data"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    data_type = Column(String(100))  # table, chart, number, percentage
    label = Column(String(500))
    data_json = Column(JSON)  # {headers: [...], rows: [...]} or {labels: [...], values: [...]}
    source = Column(String(500))  # "Phòng KH-TC", "Sở XYZ"
    notes = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    project = relationship("Project", back_populates="statistical_data")


class ReportTemplate(Base):
    """Mẫu báo cáo"""
    __tablename__ = "report_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(500), nullable=False)
    report_type = Column(String(100))
    department_type = Column(String(200))
    structure = Column(JSON)  # [{section: "Phần 1", subsections: [...]}, ...]
    sample_content = Column(Text)
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    creator = relationship("User")
