from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date

# --- Project Schemas ---
class ProjectBase(BaseModel):
    name: str
    color_hex: str
    icon: str = "fas fa-book"
    description: Optional[str] = None
    status: str = "active"

class ProjectCreate(ProjectBase):
    energy_percent: Optional[int] = 0

class Project(ProjectBase):
    id: str
    user_id: str
    
    # Enriched fields
    energy_percent: int = 0
    total_tasks: int = 0
    completed_tasks: int = 0
    total_duration: int = 0
    is_completed: bool = False

    class Config:
        from_attributes = True

# --- Budget Schemas ---
class BudgetCreate(BaseModel):
    project_id: str
    target_percentage: int

# --- Task Schemas ---
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str = "medium"

class TaskCreate(TaskBase):
    project_id: str

class TaskUpdate(BaseModel):
    status: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None

class Task(TaskBase):
    id: str
    project_id: str
    project_name: str = "" # Enriched
    status: str
    created_at: datetime
    total_duration: int = 0
    
    class Config:
        from_attributes = True

# --- TimeLog Schemas ---
class ManualTimeLog(BaseModel):
    duration: int
    note: Optional[str] = None

class TimeLogCreate(BaseModel):
    task_id: Optional[str] = None
    project_id: str
    log_type: str # TIMER, MANUAL
    duration_seconds: int
    log_date: Optional[date] = None
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None

class TimeLog(BaseModel):
    id: str
    duration_seconds: int
    log_type: str
    class Config:
        from_attributes = True

# --- Analysis Schemas ---
class VarianceResult(BaseModel):
    project_id: str
    project_name: str
    target_percentage: int
    actual_percentage: float
    variance: float
    status: str # "Balanced", "Over-invested", "Under-invested"
