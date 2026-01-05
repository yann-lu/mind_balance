from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Date, Float, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from database import Base

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Project(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String)  # 不使用外键
    name = Column(String, index=True)
    color_hex = Column(String, default="#000000")
    icon = Column(String, default="fas fa-book")
    description = Column(String, nullable=True)
    status = Column(String, default="active") # active, archived
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ProjectBudget(Base):
    __tablename__ = "project_budgets"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String)  # 不使用外键
    target_percentage = Column(Integer) # 0-100
    valid_from = Column(DateTime(timezone=True), server_default=func.now())
    valid_to = Column(DateTime(timezone=True), nullable=True) # Null means current

    # 关系：一个预算属于一个项目 (多对一)
    project = relationship(
        Project,
        primaryjoin="ProjectBudget.project_id == Project.id",
        foreign_keys=[project_id]
    )

# 在两个类都定义完后，再添加 Project.budgets 关系
Project.budgets = relationship(
    ProjectBudget,
    primaryjoin="Project.id == ProjectBudget.project_id",
    back_populates="project",
    foreign_keys="[ProjectBudget.project_id]"
)

class Task(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, default=generate_uuid)
    project_id = Column(String)  # 不使用外键
    title = Column(String, index=True)
    description = Column(String, nullable=True)
    status = Column(String, default="todo") # todo, in_progress, done
    priority = Column(String, default="medium")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class TimeLog(Base):
    __tablename__ = "time_logs"

    id = Column(String, primary_key=True, default=generate_uuid)
    task_id = Column(String, nullable=True)  # 不使用外键
    project_id = Column(String)  # 不使用外键
    user_id = Column(String)  # 不使用外键

    log_type = Column(String) # TIMER, MANUAL
    start_at = Column(DateTime(timezone=True), nullable=True)
    end_at = Column(DateTime(timezone=True), nullable=True)
    duration_seconds = Column(Integer, default=0)
    log_date = Column(Date, server_default=func.current_date())

    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AIConfig(Base):
    """AI配置表"""
    __tablename__ = "ai_configs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String)  # 不使用外键
    provider = Column(String, nullable=False)  # 'deepseek', 'qwen', 'openai', etc.
    api_key = Column(String, nullable=False)
    api_base = Column(String, nullable=True)  # 自定义API端点
    model = Column(String, nullable=True)  # 使用的模型名称
    is_active = Column(Boolean, default=True)  # 是否为当前激活的配置
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class AIConversation(Base):
    """AI对话历史表"""
    __tablename__ = "ai_conversations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String)  # 不使用外键
    role = Column(String, nullable=False)  # 'system', 'user', 'assistant'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AISuggestion(Base):
    """AI学习建议缓存表"""
    __tablename__ = "ai_suggestions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String)  # 不使用外键
    suggestion_type = Column(String, nullable=False)  # 'daily_plan', 'energy_warning', 'task_recommendation'
    content = Column(Text, nullable=False)  # JSON格式的建议内容
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)  # 缓存过期时间
