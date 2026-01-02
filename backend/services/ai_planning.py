"""
AI规划服务 - 使用AI生成学习建议和任务推荐
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, String
from services import ai_service
import models
from datetime import date, timedelta, datetime
from typing import List, Dict, Any
import json


async def get_active_ai_config(db: Session, user_id: str) -> Dict[str, Any]:
    """获取用户激活的AI配置"""
    config = db.query(models.AIConfig).filter(
        cast(models.AIConfig.user_id, String) == str(user_id),
        models.AIConfig.is_active == True
    ).first()

    if not config:
        return None

    return {
        'provider': config.provider,
        'api_key': config.api_key,
        'api_base': config.api_base,
        'model': config.model
    }


async def generate_daily_plan(db: Session, user_id: str) -> Dict[str, Any]:
    """生成今日学习计划"""

    # 获取用户的项目和任务数据
    projects = db.query(models.Project).filter(
        models.Project.user_id == user_id
    ).all()

    if not projects:
        return {'error': '没有找到项目'}

    # 获取本周的时间记录
    start_date = date.today() - timedelta(days=7)
    time_logs = db.query(models.TimeLog).filter(
        models.TimeLog.user_id == user_id,
        models.TimeLog.log_date >= start_date
    ).all()

    # 计算每个项目的实际投入时间
    project_times = {}
    for log in time_logs:
        if log.project_id not in project_times:
            project_times[log.project_id] = 0
        project_times[log.project_id] += log.duration_seconds

    total_time = sum(project_times.values()) or 1

    # 获取待办任务
    pending_tasks = db.query(models.Task).filter(
        models.Task.project_id.in_([p.id for p in projects]),
        models.Task.status.in_(['todo', 'pending'])
    ).all()

    # 构建提示词
    prompt = build_learning_plan_prompt(projects, project_times, total_time, pending_tasks)

    # 调用AI
    config = await get_active_ai_config(db, user_id)
    if not config:
        return {'error': '请先配置AI服务'}

    try:
        service = ai_service.get_ai_service(
            config['provider'],
            config['api_key'],
            config['api_base'],
            config['model']
        )

        messages = [
            {"role": "system", "content": "你是一个专业的学习规划助手，帮助学生制定合理的学习计划。"},
            {"role": "user", "content": prompt}
        ]

        response = await service.chat(messages, temperature=0.7)

        # 解析AI返回的JSON响应
        try:
            ai_result = json.loads(response)
            await service.close()
            return ai_result
        except json.JSONDecodeError:
            await service.close()
            return {'error': 'AI返回格式错误', 'raw_response': response}

    except Exception as e:
        return {'error': f'AI服务调用失败: {str(e)}'}


def build_learning_plan_prompt(projects, project_times, total_time, pending_tasks) -> str:
    """构建学习计划提示词"""

    project_info = []
    for project in projects:
        actual_time = project_times.get(project.id, 0)
        actual_percent = int((actual_time / total_time * 100)) if total_time > 0 else 0

        # 获取预算
        budget = None
        if hasattr(project, 'budgets') and project.budgets:
            budget = [b for b in project.budgets if b.valid_to is None]
            budget = budget[0] if budget else None

        target_percent = budget.target_percentage if budget else 0

        project_info.append({
            'name': project.name,
            'target_percent': target_percent,
            'actual_percent': actual_percent,
            'status': 'over' if actual_percent > target_percent + 10 else 'under' if actual_percent < target_percent - 10 else 'normal'
        })

    tasks_info = [
        {'id': str(t.id), 'title': t.title, 'project_id': str(t.project_id), 'priority': t.priority}
        for t in pending_tasks[:10]  # 限制任务数量
    ]

    prompt = f"""
作为学习规划助手,请根据以下信息分析并生成今日学习建议:

## 项目情况
{json.dumps(project_info, ensure_ascii=False, indent=2)}

## 待办任务
{json.dumps(tasks_info, ensure_ascii=False, indent=2)}

请返回JSON格式的建议,包含以下字段:
{{
    "warnings": [  // 精力预警
        {{
            "title": "预警标题",
            "message": "详细说明",
            "level": "high|medium|low",
            "suggestions": [
                {{"text": "建议文本", "action": "action类型"}}
            ]
        }}
    ],
    "recommendations": [  // 今日推荐任务
        {{
            "id": "任务ID",
            "name": "任务名称",
            "projectName": "项目名称",
            "priority": "high|medium|low",
            "estimatedTime": "预计耗时(分钟)",
            "reason": "推荐理由"
        }}
    ],
    "energySuggestions": [  // 精力分配建议
        {{
            "projectName": "项目名称",
            "target": 目标百分比,
            "actual": 实际百分比,
            "status": "balanced|unbalanced",
            "suggestion": "建议内容"
        }}
    ],
    "dailyTips": [  // 学习建议
        "建议文本1",
        "建议文本2"
    ]
}}

注意:
1. 推荐任务应该是真实的待办任务ID
2. 优先推荐投入不足的项目任务
3. 建议要具体、可操作
4. 返回纯JSON,不要有其他文字
"""

    return prompt


async def get_energy_warnings(db: Session, user_id: str) -> List[Dict[str, Any]]:
    """获取精力预警(基于规则,不需要AI)"""
    start_date = date.today() - timedelta(days=7)

    # 获取用户项目
    projects = db.query(models.Project).filter(
        models.Project.user_id == user_id
    ).all()

    warnings = []

    for project in projects:
        # 获取目标精力
        budget = db.query(models.ProjectBudget).filter(
            models.ProjectBudget.project_id == project.id,
            models.ProjectBudget.valid_to == None
        ).first()

        if not budget:
            continue

        target_percent = budget.target_percentage

        # 计算实际投入
        actual_seconds = db.query(func.sum(models.TimeLog.duration_seconds)).filter(
            models.TimeLog.project_id == project.id,
            models.TimeLog.log_date >= start_date
        ).scalar() or 0

        # 获取总时长
        total_seconds = db.query(func.sum(models.TimeLog.duration_seconds)).filter(
            models.TimeLog.user_id == user_id,
            models.TimeLog.log_date >= start_date
        ).scalar() or 1

        actual_percent = int((actual_seconds / total_seconds * 100)) if total_seconds > 0 else 0

        # 判断是否需要预警
        if actual_percent > target_percent + 10:
            warnings.append({
                'id': f"warning_{project.id}",
                'title': f'{project.name}精力超支',
                'message': f'{project.name}本周已投入{actual_percent}%的精力,超过目标{target_percent}%较多',
                'level': 'high' if actual_percent > target_percent + 20 else 'medium',
                'suggestions': [
                    {'text': '调整今日计划', 'action': 'adjust_task'},
                    {'text': '查看统计详情', 'action': 'view_stats'}
                ]
            })
        elif actual_percent < target_percent - 10:
            warnings.append({
                'id': f"warning_{project.id}",
                'title': f'{project.name}进度滞后',
                'message': f'{project.name}本周仅投入{actual_percent}%精力,低于目标{target_percent}%',
                'level': 'medium',
                'suggestions': [
                    {'text': f'添加{project.name}任务', 'action': 'add_task'}
                ]
            })

    return warnings
