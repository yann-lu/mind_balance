import uuid
from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Union
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

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    color_hex: Optional[str] = None
    icon: Optional[str] = None
    description: Optional[str] = None
    energy_percent: Optional[int] = None
    status: Optional[str] = None

class Project(ProjectBase):
    id: Union[str, uuid.UUID]
    user_id: Union[str, uuid.UUID]
    
    # Enriched fields
    energy_percent: int = 0
    total_tasks: int = 0
    completed_tasks: int = 0
    total_duration: int = 0
    is_completed: bool = False

    model_config = ConfigDict(from_attributes=True)

# --- Budget Schemas ---
class BudgetCreate(BaseModel):
    project_id: Union[str, uuid.UUID]
    target_percentage: int

# --- Task Schemas ---
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str = "medium"

class TaskCreate(TaskBase):
    project_id: Union[str, uuid.UUID]

class TaskUpdate(BaseModel):
    status: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None

class Task(TaskBase):
    id: Union[str, uuid.UUID]
    project_id: Union[str, uuid.UUID]
    project_name: str = "" # Enriched
    status: str
    created_at: datetime
    total_duration: int = 0
    
    model_config = ConfigDict(from_attributes=True)

# --- TimeLog Schemas ---
class ManualTimeLog(BaseModel):
    duration: int
    note: Optional[str] = None

class TimeLogCreate(BaseModel):
    task_id: Optional[Union[str, uuid.UUID]] = None
    project_id: Union[str, uuid.UUID]
    log_type: str # TIMER, MANUAL
    duration_seconds: int
    log_date: Optional[date] = None
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None

class TimeLog(BaseModel):
    id: Union[str, uuid.UUID]
    duration_seconds: int
    log_type: str
    model_config = ConfigDict(from_attributes=True)

# --- Analysis Schemas ---
class VarianceResult(BaseModel):
    project_id: str
    project_name: str
    target_percentage: int
    actual_percentage: float
    variance: float
    status: str # "Balanced", "Over-invested", "Under-invested"

# --- Statistics Schemas ---
class OverviewStats(BaseModel):
    total_duration: int = 0  # 总学习时长（秒）
    completed_tasks: int = 0  # 完成的任务数
    study_days: int = 0  # 学习天数
    avg_daily_duration: int = 0  # 日均学习时长（秒）
    today_duration: int = 0  # 今日学习时长（秒）
    active_projects: int = 0  # 活跃项目数
    pending_tasks: int = 0  # 待完成任务数
    energy_rate: int = 0  # 精力达标率（百分比）

    # 使用别名转换为camelCase供前端使用
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=lambda field_name: ''.join(
            word.capitalize() if i > 0 else word
            for i, word in enumerate(field_name.split('_'))
        )
    )

class ProjectTimeDistribution(BaseModel):
    id: str
    name: str
    color_hex: str
    icon: str
    duration: int  # 时长（秒）

    # 使用别名转换为camelCase供前端使用
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=lambda field_name: ''.join(
            word.capitalize() if i > 0 else word
            for i, word in enumerate(field_name.split('_'))
        )
    )

class DailyTrend(BaseModel):
    date: str  # 日期字符串，如 "2024-01-01"
    duration: int  # 时长（秒）

class EnergyDistribution(BaseModel):
    id: str
    name: str
    color_hex: str
    icon: str
    targetEnergy: int  # 目标精力百分比
    actualEnergy: int  # 实际精力百分比
    totalDuration: int  # 总时长（秒）
    completedTasks: int  # 完成任务数
    totalTasks: int  # 总任务数

    # 使用别名转换为camelCase供前端使用
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=lambda field_name: ''.join(
            word.capitalize() if i > 0 else word
            for i, word in enumerate(field_name.split('_'))
        )
    )

# --- AI Config Schemas ---
class AIConfigBase(BaseModel):
    provider: str  # 'deepseek', 'qwen', 'openai'
    api_key: str
    api_base: Optional[str] = None
    model: Optional[str] = None

class AIConfigCreate(AIConfigBase):
    pass

class AIConfigUpdate(BaseModel):
    provider: Optional[str] = None
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    model: Optional[str] = None
    is_active: Optional[bool] = None

class AIConfig(AIConfigBase):
    id: int
    user_id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# --- AI Planning Schemas ---
class GeneratePlanRequest(BaseModel):
    period: Optional[str] = "today"  # "today", "week", "month"
    use_ai: Optional[bool] = False  # 是否使用AI完整分析(True=AI模式, False=规则引擎模式)

class EnergyWarning(BaseModel):
    id: str
    title: str
    message: str
    level: str  # 'high', 'medium', 'low'
    suggestions: List[dict]

class TaskRecommendation(BaseModel):
    id: str
    name: str
    projectName: str
    icon: str
    color: str
    priority: str
    estimatedTime: str
    reason: str

class EnergySuggestion(BaseModel):
    projectName: str
    icon: str
    color: str
    target: int
    actual: int
    status: str  # 'balanced', 'unbalanced'
    suggestion: str
