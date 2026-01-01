from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from . import models, schemas, crud, database
from .services import analysis

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
    return user.id

# --- Routes ---

@app.get("/projects", response_model=List[schemas.Project])
def read_projects(db: Session = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    return crud.get_projects(db, user_id)

@app.post("/projects", response_model=schemas.Project)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    return crud.create_project(db, project, user_id)

@app.get("/projects/{project_id}/tasks", response_model=List[schemas.Task])
def read_project_tasks(project_id: str, db: Session = Depends(get_db)):
    return crud.get_tasks(db, project_id)

@app.get("/tasks", response_model=List[schemas.Task])
def read_all_tasks(project_id: Optional[str] = None, db: Session = Depends(get_db)):
    return crud.get_tasks(db, project_id)

@app.post("/tasks", response_model=schemas.Task)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    return crud.create_task(db, task)

@app.put("/tasks/{task_id}", response_model=schemas.Task)
def update_task(task_id: str, task: schemas.TaskUpdate, db: Session = Depends(get_db)):
    updated = crud.update_task(db, task_id, task)
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated

@app.delete("/tasks/{task_id}")
def delete_task(task_id: str, db: Session = Depends(get_db)):
    if not crud.delete_task(db, task_id):
         raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted"}

@app.post("/tasks/{task_id}/timer/start")
def start_timer(task_id: str, db: Session = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    crud.start_timer(db, task_id, user_id)
    return {"message": "Timer started"}

@app.post("/tasks/{task_id}/timer/stop")
def stop_timer(task_id: str, db: Session = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    crud.stop_timer(db, task_id, user_id)
    return {"message": "Timer stopped"}

@app.post("/tasks/{task_id}/timer/pause")
def pause_timer(task_id: str, db: Session = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    crud.pause_timer(db, task_id, user_id)
    return {"message": "Timer paused"}

@app.post("/tasks/{task_id}/time-manual")
def add_manual_time(task_id: str, data: schemas.ManualTimeLog, db: Session = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    crud.log_manual_time(db, task_id, data, user_id)
    return {"message": "Time added"}

@app.post("/timelogs", response_model=schemas.TimeLog)
def create_timelog(log: schemas.TimeLogCreate, db: Session = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    return crud.create_time_log(db, log, user_id)

@app.post("/budgets", response_model=schemas.BudgetCreate) # returning simplified for now
def set_budget(budget: schemas.BudgetCreate, db: Session = Depends(get_db)):
    crud.set_project_budget(db, budget)
    return budget

@app.get("/analysis/variance", response_model=List[schemas.VarianceResult])
def get_variance(days: int = 7, db: Session = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    return analysis.calculate_variance(db, user_id, days)

@app.get("/")
def read_root():
    return {"message": "MindBalance API is running. Go to /docs for Swagger UI."}
