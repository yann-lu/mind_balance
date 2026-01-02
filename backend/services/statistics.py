from sqlalchemy.orm import Session
from sqlalchemy import func, and_
import models
import schemas
from datetime import date, timedelta, datetime


def get_date_range(period: str):
    """根据时间周期获取日期范围"""
    end_date = date.today()

    if period == 'week':
        start_date = end_date - timedelta(days=7)
    elif period == 'month':
        # 本月第一天
        start_date = end_date.replace(day=1)
    elif period == 'all':
        start_date = date.min  # 非常早的日期
    else:
        # 默认最近7天
        start_date = end_date - timedelta(days=7)

    return start_date, end_date


def get_overview_stats(db: Session, user_id: str, period: str = 'week') -> schemas.OverviewStats:
    """获取概览统计数据"""
    start_date, end_date = get_date_range(period)

    # 总学习时长
    total_duration = db.query(func.sum(models.TimeLog.duration_seconds))\
        .filter(models.TimeLog.user_id == user_id)\
        .filter(models.TimeLog.log_date >= start_date)\
        .filter(models.TimeLog.log_date <= end_date)\
        .scalar() or 0

    # 完成的任务数
    completed_tasks = db.query(func.count(models.Task.id))\
        .join(models.Project, models.Task.project_id == models.Project.id)\
        .filter(models.Project.user_id == user_id)\
        .filter(models.Task.status == 'done')\
        .scalar() or 0

    # 学习天数（有记录的日期数量）
    study_days = db.query(func.count(func.distinct(models.TimeLog.log_date)))\
        .filter(models.TimeLog.user_id == user_id)\
        .filter(models.TimeLog.log_date >= start_date)\
        .filter(models.TimeLog.log_date <= end_date)\
        .scalar() or 0

    # 日均学习时长
    avg_daily_duration = int(total_duration / study_days) if study_days > 0 else 0

    return schemas.OverviewStats(
        total_duration=total_duration,
        completed_tasks=completed_tasks,
        study_days=study_days,
        avg_daily_duration=avg_daily_duration
    )


def get_project_time_distribution(db: Session, user_id: str, period: str = 'week') -> list[schemas.ProjectTimeDistribution]:
    """获取项目时间分布"""
    start_date, end_date = get_date_range(period)

    # 查询每个项目的时间分布
    project_times = db.query(
        models.Project.id,
        models.Project.name,
        models.Project.color_hex,
        models.Project.icon,
        func.sum(models.TimeLog.duration_seconds).label('duration')
    ).join(models.TimeLog, models.Project.id == models.TimeLog.project_id)\
     .filter(models.Project.user_id == user_id)\
     .filter(models.TimeLog.log_date >= start_date)\
     .filter(models.TimeLog.log_date <= end_date)\
     .group_by(models.Project.id, models.Project.name, models.Project.color_hex, models.Project.icon)\
     .all()

    return [
        schemas.ProjectTimeDistribution(
            id=str(pt.id),
            name=pt.name,
            color_hex=pt.color_hex,
            icon=pt.icon,
            duration=pt.duration or 0
        )
        for pt in project_times
    ]


def get_daily_trend(db: Session, user_id: str, period: str = 'week') -> list[schemas.DailyTrend]:
    """获取每日学习时长趋势"""
    start_date, end_date = get_date_range(period)

    # 查询每日学习时长
    daily_times = db.query(
        models.TimeLog.log_date,
        func.sum(models.TimeLog.duration_seconds).label('duration')
    ).filter(models.TimeLog.user_id == user_id)\
     .filter(models.TimeLog.log_date >= start_date)\
     .filter(models.TimeLog.log_date <= end_date)\
     .group_by(models.TimeLog.log_date)\
     .order_by(models.TimeLog.log_date)\
     .all()

    return [
        schemas.DailyTrend(
            date=str(dt.log_date),
            duration=dt.duration or 0
        )
        for dt in daily_times
    ]


def get_energy_distribution(db: Session, user_id: str, period: str = 'week') -> list[schemas.EnergyDistribution]:
    """获取精力分配对比"""
    start_date, end_date = get_date_range(period)

    # 查询所有项目
    projects = db.query(models.Project)\
        .filter(models.Project.user_id == user_id)\
        .all()

    results = []

    for project in projects:
        # 获取当前目标精力（从预算表）
        budget = db.query(models.ProjectBudget)\
            .filter(models.ProjectBudget.project_id == project.id)\
            .filter(models.ProjectBudget.valid_to == None)\
            .first()

        target_energy = budget.target_percentage if budget else 0

        # 计算该时间段内的总学习时长
        total_duration = db.query(func.sum(models.TimeLog.duration_seconds))\
            .filter(models.TimeLog.project_id == project.id)\
            .filter(models.TimeLog.log_date >= start_date)\
            .filter(models.TimeLog.log_date <= end_date)\
            .scalar() or 0

        # 获取任务统计
        total_tasks = db.query(func.count(models.Task.id))\
            .filter(models.Task.project_id == project.id)\
            .scalar() or 0

        completed_tasks = db.query(func.count(models.Task.id))\
            .filter(models.Task.project_id == project.id)\
            .filter(models.Task.status == 'done')\
            .scalar() or 0

        # 计算实际精力分配百分比
        # 需要获取该时间段内所有项目的总时长
        all_duration = db.query(func.sum(models.TimeLog.duration_seconds))\
            .filter(models.TimeLog.user_id == user_id)\
            .filter(models.TimeLog.log_date >= start_date)\
            .filter(models.TimeLog.log_date <= end_date)\
            .scalar() or 0

        actual_energy = int((total_duration / all_duration * 100)) if all_duration > 0 else 0

        results.append(schemas.EnergyDistribution(
            id=str(project.id),
            name=project.name,
            color_hex=project.color_hex,
            icon=project.icon,
            targetEnergy=target_energy,
            actualEnergy=actual_energy,
            totalDuration=total_duration,
            completedTasks=completed_tasks,
            totalTasks=total_tasks
        ))

    return results
