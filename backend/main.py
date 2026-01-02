from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from . import models, schemas, crud, database
from .services import analysis, statistics

# Create Tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="MindBalance API")

# --- CORS Configuration ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173", "http://127.0.0.1:5173"], # Allow Frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Helpers ---
# In a real app, we'd get user_id from JWT token. 
# Here we mock it or create a default user on startup.
DEMO_USER_EMAIL = "demo@mindbalance.ai"

@app.on_event("startup")
def startup_event():
    db = database.SessionLocal()
    user = crud.get_user_by_email(db, DEMO_USER_EMAIL)
    if not user:
        user = crud.create_user(db, DEMO_USER_EMAIL)
        # Create some demo projects
        # Project 1
        p1_in = schemas.ProjectCreate(
            name="Learn Python", 
            color_hex="#3776AB", 
            icon="fab fa-python",
            description="Mastering Python for backend dev",
            energy_percent=50
        )
        crud.create_project(db, p1_in, user.id)
        
        # Project 2
        p2_in = schemas.ProjectCreate(
            name="Database Design", 
            color_hex="#336791",
            icon="fas fa-database",
            description="SQL, NoSQL and schema optimization",
            energy_percent=30
        )
        crud.create_project(db, p2_in, user.id)
        
        # Project 3
        p3_in = schemas.ProjectCreate(
            name="English", 
            color_hex="#FF0000",
            icon="fas fa-language",
            description="Daily reading and vocabulary",
            energy_percent=20
        )
        crud.create_project(db, p3_in, user.id)

    db.close()

def get_current_user_id(db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, DEMO_USER_EMAIL)
    if not user:
        # Fallback if startup didn't run or user missing
        user = crud.create_user(db, DEMO_USER_EMAIL)
    return user.id

# --- Routes ---

@app.get("/api/projects", response_model=List[schemas.Project])
def read_projects(db: Session = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    return crud.get_projects(db, user_id)

@app.post("/api/projects", response_model=schemas.Project)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    try:
        print(f"Creating project: {project}")
        return crud.create_project(db, project, user_id)
    except Exception as e:
        print(f"Error creating project: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/projects/{project_id}", response_model=schemas.Project)
def update_project(project_id: str, project: schemas.ProjectUpdate, db: Session = Depends(get_db)):
    updated_project = crud.update_project(db, project_id, project)
    if not updated_project:
        raise HTTPException(status_code=404, detail="Project not found")
    return updated_project

@app.delete("/api/projects/{project_id}")
def delete_project(project_id: str, db: Session = Depends(get_db)):
    if not crud.delete_project(db, project_id):
        raise HTTPException(status_code=404, detail="Project not found")
    return {"message": "Project deleted"}

@app.post("/api/projects/{project_id}/complete")
def complete_project(project_id: str, db: Session = Depends(get_db)):
    if not crud.complete_project(db, project_id):
        raise HTTPException(status_code=404, detail="Project not found")
    return {"message": "Project marked as completed"}

@app.get("/api/projects/{project_id}/tasks", response_model=List[schemas.Task])
def read_project_tasks(project_id: str, db: Session = Depends(get_db)):
    return crud.get_tasks(db, project_id)

@app.get("/api/tasks", response_model=List[schemas.Task])
def read_all_tasks(project_id: Optional[str] = None, db: Session = Depends(get_db)):
    return crud.get_tasks(db, project_id)

@app.post("/api/tasks", response_model=schemas.Task)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    return crud.create_task(db, task)

@app.put("/api/tasks/{task_id}", response_model=schemas.Task)
def update_task(task_id: str, task: schemas.TaskUpdate, db: Session = Depends(get_db)):
    updated = crud.update_task(db, task_id, task)
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated

@app.delete("/api/tasks/{task_id}")
def delete_task(task_id: str, db: Session = Depends(get_db)):
    if not crud.delete_task(db, task_id):
         raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted"}

@app.post("/api/tasks/{task_id}/timer/start")
def start_timer(task_id: str, db: Session = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    crud.start_timer(db, task_id, user_id)
    return {"message": "Timer started"}

@app.post("/api/tasks/{task_id}/timer/stop")
def stop_timer(task_id: str, db: Session = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    result = crud.stop_timer(db, task_id, user_id)
    if not result:
        raise HTTPException(status_code=400, detail="No active timer found for this task")
    return {"message": "Timer stopped"}

@app.post("/api/tasks/{task_id}/timer/pause")
def pause_timer(task_id: str, db: Session = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    result = crud.pause_timer(db, task_id, user_id)
    if not result:
        raise HTTPException(status_code=400, detail="No active timer found for this task")
    return {"message": "Timer paused"}

@app.post("/api/tasks/{task_id}/time-manual")
def add_manual_time(task_id: str, data: schemas.ManualTimeLog, db: Session = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    crud.log_manual_time(db, task_id, data, user_id)
    return {"message": "Time added"}

@app.post("/api/timelogs", response_model=schemas.TimeLog)
def create_timelog(log: schemas.TimeLogCreate, db: Session = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    return crud.create_time_log(db, log, user_id)

@app.post("/api/budgets", response_model=schemas.BudgetCreate) # returning simplified for now
def set_budget(budget: schemas.BudgetCreate, db: Session = Depends(get_db)):
    crud.set_project_budget(db, budget)
    return budget

@app.get("/api/analysis/variance", response_model=List[schemas.VarianceResult])
def get_variance(days: int = 7, db: Session = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    return analysis.calculate_variance(db, user_id, days)

# --- Statistics Routes ---

@app.get("/api/statistics/overview")
def get_overview(period: str = "week", db: Session = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    """获取概览统计数据"""
    stats = statistics.get_overview_stats(db, user_id, period)
    return stats.model_dump(by_alias=True)

@app.get("/api/statistics/project-time")
def get_project_time(period: str = "week", db: Session = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    """获取项目时间分布"""
    projects = statistics.get_project_time_distribution(db, user_id, period)
    return [p.model_dump(by_alias=True) for p in projects]

@app.get("/api/statistics/daily-trend")
def get_daily_trend(period: str = "week", db: Session = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    """获取每日学习时长趋势"""
    trends = statistics.get_daily_trend(db, user_id, period)
    return [t.model_dump(by_alias=True) for t in trends]

@app.get("/api/statistics/energy")
def get_energy_distribution(period: str = "week", db: Session = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    """获取精力分配对比"""
    energy = statistics.get_energy_distribution(db, user_id, period)
    return [e.model_dump(by_alias=True) for e in energy]

@app.get("/")
def read_root():
    return {"message": "MindBalance API is running. Go to /docs for Swagger UI."}
