from sqlalchemy.orm import Session
from sqlalchemy import func
from . import models, schemas
from datetime import datetime, date

# --- User ---
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, email: str):
    user = models.User(email=email, full_name="Demo User")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# --- Projects ---
def get_projects(db: Session, user_id: str):
    projects = db.query(models.Project).filter(models.Project.user_id == user_id).all()
    results = []
    for p in projects:
        # Get active budget
        budget = db.query(models.ProjectBudget).filter(
            models.ProjectBudget.project_id == p.id,
            models.ProjectBudget.valid_to == None
        ).first()
        energy_percent = budget.target_percentage if budget else 0
        
        # Get task stats
        task_count = db.query(func.count(models.Task.id)).filter(models.Task.project_id == p.id).scalar()
        completed_count = db.query(func.count(models.Task.id)).filter(
            models.Task.project_id == p.id, 
            models.Task.status == 'done'
        ).scalar()
        
        # Get duration stats
        duration = db.query(func.sum(models.TimeLog.duration_seconds)).filter(
            models.TimeLog.project_id == p.id
        ).scalar()
        
        # Create a transient object or dictionary to match Schema
        # We can attach attributes to the ORM object if we are careful, 
        # or convert to dict. Pydantic from_attributes handles objects with attributes.
        p.energy_percent = energy_percent
        p.total_tasks = task_count or 0
        p.completed_tasks = completed_count or 0
        p.total_duration = duration or 0
        p.is_completed = (p.status == 'completed')
        
        results.append(p)
    return results

def create_project(db: Session, project: schemas.ProjectCreate, user_id: str):
    # Extract energy_percent to handle separately
    project_data = project.model_dump(exclude={'energy_percent'})
    
    db_project = models.Project(**project_data, user_id=user_id)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    
    # Create initial budget
    if project.energy_percent is not None:
        budget = models.ProjectBudget(
            project_id=db_project.id,
            target_percentage=project.energy_percent
        )
        db.add(budget)
        db.commit()
        
    # Set default attributes for response
    db_project.energy_percent = project.energy_percent or 0
    db_project.total_tasks = 0
    db_project.completed_tasks = 0
    db_project.total_duration = 0
    db_project.is_completed = False
    
    return db_project

# --- Tasks ---
def get_tasks(db: Session, project_id: str = None):
    query = db.query(models.Task)
    if project_id:
        query = query.filter(models.Task.project_id == project_id)
    
    tasks = query.all()
    results = []
    for t in tasks:
        # Get project name
        project = db.query(models.Project).filter(models.Project.id == t.project_id).first()
        t.project_name = project.name if project else "Unknown"
        
        # Calculate duration
        total = db.query(func.sum(models.TimeLog.duration_seconds)).filter(models.TimeLog.task_id == t.id).scalar()
        t.total_duration = total or 0
        results.append(t)
    return results

def create_task(db: Session, task: schemas.TaskCreate):
    db_task = models.Task(**task.model_dump())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    # Populate for response
    project = db.query(models.Project).filter(models.Project.id == db_task.project_id).first()
    db_task.project_name = project.name if project else ""
    db_task.total_duration = 0
    
    return db_task

def update_task(db: Session, task_id: str, updates: schemas.TaskUpdate):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        return None
        
    update_data = updates.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)
        
    db.commit()
    db.refresh(task)
    
    # Re-populate computed fields for response
    project = db.query(models.Project).filter(models.Project.id == task.project_id).first()
    task.project_name = project.name if project else ""
    total = db.query(func.sum(models.TimeLog.duration_seconds)).filter(models.TimeLog.task_id == task.id).scalar()
    task.total_duration = total or 0
    
    return task

def delete_task(db: Session, task_id: str):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if task:
        db.delete(task)
        db.commit()
        return True
    return False

# --- Timer Logic ---
def start_timer(db: Session, task_id: str, user_id: str):
    # Stop any running timer for this user first (optional, but good practice)
    # For now, let's just create a new open log
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        return None
        
    log = models.TimeLog(
        task_id=task_id,
        project_id=task.project_id,
        user_id=user_id,
        log_type="TIMER",
        start_at=datetime.now(),
        log_date=date.today()
    )
    db.add(log)
    db.commit()
    return log

def stop_timer(db: Session, task_id: str, user_id: str):
    # Find latest open log for this task
    log = db.query(models.TimeLog).filter(
        models.TimeLog.task_id == task_id,
        models.TimeLog.user_id == user_id,
        models.TimeLog.end_at == None
    ).order_by(models.TimeLog.start_at.desc()).first()
    
    if log:
        log.end_at = datetime.now()
        # Calculate duration
        delta = log.end_at - log.start_at
        log.duration_seconds = int(delta.total_seconds())
        db.commit()
        return log
    return None

def pause_timer(db: Session, task_id: str, user_id: str):
    # Same as stop for now
    return stop_timer(db, task_id, user_id)

def log_manual_time(db: Session, task_id: str, manual_data: schemas.ManualTimeLog, user_id: str):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        return None
        
    log = models.TimeLog(
        task_id=task_id,
        project_id=task.project_id,
        user_id=user_id,
        log_type="MANUAL",
        duration_seconds=manual_data.duration,
        log_date=date.today(),
        start_at=datetime.now(), # Just for record
        end_at=datetime.now()
    )
    db.add(log)
    db.commit()
    return log

def update_task_status(db: Session, task_id: str, status: str):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if task:
        task.status = status
        db.commit()
        db.refresh(task)
    return task

# --- TimeLogs ---
def create_time_log(db: Session, log: schemas.TimeLogCreate, user_id: str):
    db_log = models.TimeLog(**log.model_dump(), user_id=user_id)
    if not db_log.log_date:
        db_log.log_date = date.today()
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

# --- Budgets ---
def set_project_budget(db: Session, budget: schemas.BudgetCreate):
    # 1. Close current budget
    current = db.query(models.ProjectBudget).filter(models.ProjectBudget.project_id == budget.project_id).filter(models.ProjectBudget.valid_to == None).first()
    
    if current:
        current.valid_to = datetime.now()
        db.add(current)
    
    # 2. Create new
    new_budget = models.ProjectBudget(
        project_id=budget.project_id,
        target_percentage=budget.target_percentage
    )
    db.add(new_budget)
    db.commit()
    return new_budget
