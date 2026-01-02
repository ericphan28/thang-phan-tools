"""
Pydantic schemas for Document AI API
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# Enums
class ProjectStatus(str, Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"


class ReportType(str, Enum):
    PERIODIC = "periodic"  # Báo cáo định kỳ
    SPECIAL = "special"  # Báo cáo chuyên đề
    SUMMARY = "summary"  # Báo cáo tổng kết
    PROPOSAL = "proposal"  # Tờ trình


class DocumentStatus(str, Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    EXTRACTED = "extracted"
    ERROR = "error"


class TaskGroup(str, Enum):
    GROUP_1 = "group_1"  # Input Processing
    GROUP_2 = "group_2"  # Content Generation
    GROUP_3 = "group_3"  # Document Refinement


class TaskType(str, Enum):
    # Group 1
    EXTRACT_DOCUMENT = "extract_document"
    ANALYZE_STATISTICS = "analyze_statistics"
    COMPARE_DATA = "compare_data"
    SUMMARIZE_CLASSIFY = "summarize_classify"
    
    # Group 2
    SUGGEST_OUTLINE = "suggest_outline"
    WRITE_EVALUATION = "write_evaluation"
    WRITE_CHALLENGES = "write_challenges"
    WRITE_RECOMMENDATIONS = "write_recommendations"
    
    # Group 3
    REFINE_STYLE = "refine_style"
    CREATE_ABSTRACT = "create_abstract"
    CHECK_ACCURACY = "check_accuracy"


# Project schemas
class ProjectBase(BaseModel):
    name: str = Field(..., max_length=500, description="Tên dự án")
    description: Optional[str] = Field(None, description="Mô tả dự án")
    report_type: Optional[ReportType] = Field(None, description="Loại báo cáo")
    department: Optional[str] = Field(None, max_length=200, description="Phòng/Ban")
    period: Optional[str] = Field(None, max_length=100, description="Kỳ báo cáo")


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    report_type: Optional[ReportType] = None
    department: Optional[str] = Field(None, max_length=200)
    period: Optional[str] = Field(None, max_length=100)
    status: Optional[ProjectStatus] = None


class ProjectResponse(ProjectBase):
    id: int
    user_id: int
    status: ProjectStatus
    created_at: datetime
    updated_at: datetime
    
    # Counts
    documents_count: int = 0
    ai_tasks_count: int = 0
    sections_count: int = 0

    class Config:
        from_attributes = True


# Document schemas
class DocumentBase(BaseModel):
    title: str = Field(..., max_length=500, description="Tên văn bản")
    file_type: Optional[str] = Field(None, max_length=50)


class DocumentCreate(DocumentBase):
    pass


class DocumentResponse(DocumentBase):
    id: int
    project_id: int
    user_id: int
    file_path: Optional[str]
    file_size: Optional[int]
    extracted_text: Optional[str]
    doc_metadata: Optional[Dict[str, Any]]
    status: DocumentStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# AI Task schemas
class AITaskCreate(BaseModel):
    project_id: int
    task_type: TaskType
    task_group: TaskGroup
    input_data: Dict[str, Any] = Field(..., description="Input data for AI task")
    use_history: bool = Field(False, description="Use context from previous tasks")


class AITaskResponse(BaseModel):
    id: int
    project_id: int
    user_id: int
    task_type: TaskType
    task_group: TaskGroup
    input_data: Dict[str, Any]
    prompt: Optional[str]
    ai_response: Optional[str]
    tokens_used: Optional[int]
    cost_vnd: Optional[float]
    status: str
    error_message: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


# Report Section schemas
class ReportSectionBase(BaseModel):
    section_type: str = Field(..., max_length=100)
    section_order: int
    title: str = Field(..., max_length=500)
    content: Optional[str] = None


class ReportSectionCreate(ReportSectionBase):
    project_id: int


class ReportSectionUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=500)
    content: Optional[str] = None
    reviewed: Optional[bool] = None


class ReportSectionResponse(ReportSectionBase):
    id: int
    project_id: int
    ai_generated: bool
    reviewed: bool
    version: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Statistical Data schemas
class StatisticalDataBase(BaseModel):
    data_type: str = Field(..., max_length=100, description="table, chart, number, percentage")
    label: str = Field(..., max_length=500)
    data_json: Dict[str, Any]
    source: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = None


class StatisticalDataCreate(StatisticalDataBase):
    project_id: int


class StatisticalDataResponse(StatisticalDataBase):
    id: int
    project_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Template schemas
class ReportTemplateBase(BaseModel):
    name: str = Field(..., max_length=500)
    report_type: Optional[str] = Field(None, max_length=100)
    department_type: Optional[str] = Field(None, max_length=200)
    structure: Dict[str, Any]
    sample_content: Optional[str] = None


class ReportTemplateCreate(ReportTemplateBase):
    pass


class ReportTemplateResponse(ReportTemplateBase):
    id: int
    is_active: bool
    created_by: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


# Export schemas
class ExportRequest(BaseModel):
    project_id: int
    format: str = Field(..., pattern="^(word|pdf)$", description="Export format: word or pdf")
    include_sections: Optional[List[str]] = Field(None, description="List of section IDs to include")


class ExportResponse(BaseModel):
    file_url: str
    file_name: str
    file_size: int
    format: str
