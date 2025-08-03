from sqlmodel import SQLModel, Field, Relationship, JSON, Column
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


class ProjectStatus(str, Enum):
    """Project status enumeration."""

    DRAFT = "draft"
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PACKAGED = "packaged"
    FAILED = "failed"


class FileType(str, Enum):
    """File type enumeration for uploaded assets."""

    HTML = "html"
    CSS = "css"
    JAVASCRIPT = "javascript"
    IMAGE = "image"
    FONT = "font"
    OTHER = "other"


# Persistent models (stored in database)
class Project(SQLModel, table=True):
    """Main project entity that represents a web-to-mobile packaging project."""

    __tablename__ = "projects"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=200)
    description: str = Field(default="", max_length=1000)
    status: ProjectStatus = Field(default=ProjectStatus.DRAFT)
    package_name: str = Field(max_length=100)  # Android package name (e.g., com.example.myapp)
    app_name: str = Field(max_length=100)  # Display name for the mobile app
    version_code: int = Field(default=1)
    version_name: str = Field(default="1.0.0", max_length=20)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    packaged_at: Optional[datetime] = Field(default=None)

    # Configuration for mobile app
    config: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))

    # Relationships
    files: List["ProjectFile"] = Relationship(back_populates="project", cascade_delete=True)
    builds: List["BuildOutput"] = Relationship(back_populates="project", cascade_delete=True)


class ProjectFile(SQLModel, table=True):
    """Represents uploaded files associated with a project."""

    __tablename__ = "project_files"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="projects.id")
    filename: str = Field(max_length=255)
    original_filename: str = Field(max_length=255)
    file_path: str = Field(max_length=500)  # Path where file is stored
    file_type: FileType = Field(default=FileType.OTHER)
    file_size: int = Field(default=0)  # Size in bytes
    mime_type: str = Field(max_length=100)
    is_main_file: bool = Field(default=False)  # True for index.html
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)

    # File metadata
    file_metadata: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))

    # Relationships
    project: Project = Relationship(back_populates="files")


class BuildOutput(SQLModel, table=True):
    """Represents the output of a packaging/build operation."""

    __tablename__ = "build_outputs"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="projects.id")
    build_version: str = Field(max_length=50)
    output_path: str = Field(max_length=500)  # Path to generated APK/build artifacts
    build_log: str = Field(default="")  # Build process log
    success: bool = Field(default=False)
    error_message: str = Field(default="")
    build_duration: Optional[int] = Field(default=None)  # Duration in seconds
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Build metadata and configuration used
    build_config: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))

    # Relationships
    project: Project = Relationship(back_populates="builds")


# Non-persistent schemas (for validation, forms, API requests/responses)
class ProjectCreate(SQLModel, table=False):
    """Schema for creating a new project."""

    name: str = Field(max_length=200)
    description: str = Field(default="", max_length=1000)
    package_name: str = Field(max_length=100, regex=r"^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)*$")
    app_name: str = Field(max_length=100)
    version_name: str = Field(default="1.0.0", max_length=20)
    config: Dict[str, Any] = Field(default={})


class ProjectUpdate(SQLModel, table=False):
    """Schema for updating an existing project."""

    name: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    package_name: Optional[str] = Field(default=None, max_length=100, regex=r"^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)*$")
    app_name: Optional[str] = Field(default=None, max_length=100)
    version_name: Optional[str] = Field(default=None, max_length=20)
    status: Optional[ProjectStatus] = Field(default=None)
    config: Optional[Dict[str, Any]] = Field(default=None)


class FileUpload(SQLModel, table=False):
    """Schema for file upload metadata."""

    original_filename: str = Field(max_length=255)
    file_type: FileType = Field(default=FileType.OTHER)
    is_main_file: bool = Field(default=False)
    file_metadata: Dict[str, Any] = Field(default={})


class ProjectSummary(SQLModel, table=False):
    """Summary schema for project listing."""

    id: int
    name: str
    status: ProjectStatus
    app_name: str
    version_name: str
    file_count: int
    created_at: str  # ISO format string
    updated_at: str  # ISO format string


class BuildRequest(SQLModel, table=False):
    """Schema for requesting a build/package operation."""

    build_config: Dict[str, Any] = Field(default={})
    increment_version: bool = Field(default=True)


class BuildStatus(SQLModel, table=False):
    """Schema for build status response."""

    id: int
    project_id: int
    build_version: str
    success: bool
    error_message: str
    build_duration: Optional[int]
    created_at: str  # ISO format string
    output_path: Optional[str] = Field(default=None)
