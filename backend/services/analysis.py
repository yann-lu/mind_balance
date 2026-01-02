from sqlalchemy.orm import Session
from sqlalchemy import func
import models
import schemas
from datetime import date, timedelta

def calculate_variance(db: Session, user_id: str, days: int = 7):
    # 1. Define time window
    end_date = date.today()
    start_date = end_date - timedelta(days=days)

    # 2. Get Total Time across all projects
    total_seconds = db.query(func.sum(models.TimeLog.duration_seconds))\
        .filter(models.TimeLog.user_id == user_id)\
        .filter(models.TimeLog.log_date >= start_date).scalar() or 0

    if total_seconds == 0:
        return []

    # 3. Get Time per Project
    project_times = db.query(
        models.TimeLog.project_id,
        func.sum(models.TimeLog.duration_seconds).label('seconds')
    ).filter(models.TimeLog.user_id == user_id)\
     .filter(models.TimeLog.log_date >= start_date)\
     .group_by(models.TimeLog.project_id).all()

    results = []
    
    for pt in project_times:
        proj_id = pt.project_id
        actual_seconds = pt.seconds
        actual_pct = (actual_seconds / total_seconds) * 100

        # 4. Get Current Target
        # Note: For MVP we take the *current* active budget. 
        # A full production version would time-slice this against historical budgets.
        budget = db.query(models.ProjectBudget)\
            .filter(models.ProjectBudget.project_id == proj_id)\
            .filter(models.ProjectBudget.valid_to == None).first()
        
        target_pct = budget.target_percentage if budget else 0
        project = db.query(models.Project).filter(models.Project.id == proj_id).first()
        
        variance = actual_pct - target_pct
        
        status = "Balanced"
        if variance > 10: status = "Over-invested"
        elif variance < -10: status = "Under-invested"

        results.append(schemas.VarianceResult(
            project_id=proj_id,
            project_name=project.name if project else "Unknown",
            target_percentage=target_pct,
            actual_percentage=round(actual_pct, 1),
            variance=round(variance, 1),
            status=status
        ))

    return results
