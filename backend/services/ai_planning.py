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

    # 检查是否有AI配置，如果没有则返回模拟数据
    config = await get_active_ai_config(db, user_id)
    if not config:
        # 返回模拟数据
        return generate_mock_plan(projects, project_times, total_time, pending_tasks)

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
            # 清理可能的Markdown代码块标记
            cleaned_response = response.strip()
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:]  # 移除 ```json
            elif cleaned_response.startswith('```'):
                cleaned_response = cleaned_response[3:]  # 移除 ```
            if cleaned_response.endswith('```'):
                cleaned_response = cleaned_response[:-3]  # 移除结尾的 ```
            cleaned_response = cleaned_response.strip()

            ai_result = json.loads(cleaned_response)
            await service.close()
            # 添加缺失的字段
            return _enhance_ai_result(ai_result, projects, project_times, total_time)
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            await service.close()
            print(f"AI返回格式错误，使用模拟数据: {e}, 原始响应: {response[:200]}")
            return generate_mock_plan(projects, project_times, total_time, pending_tasks)

    except Exception as e:
        # AI调用失败时返回模拟数据
        print(f"AI调用失败，返回模拟数据: {e}")
        return generate_mock_plan(projects, project_times, total_time, pending_tasks)


def _enhance_ai_result(ai_result: Dict[str, Any], projects, project_times, total_time) -> Dict[str, Any]:
    """增强AI返回结果，添加缺失的字段"""
    # 为 warnings 添加 id 字段
    if 'warnings' in ai_result:
        for idx, warning in enumerate(ai_result['warnings']):
            if 'id' not in warning:
                warning['id'] = f"warning_{idx}"

    # 为 energySuggestions 添加 projectId 字段
    if 'energySuggestions' in ai_result:
        project_name_to_id = {p.name: str(p.id) for p in projects}
        for suggestion in ai_result['energySuggestions']:
            project_name = suggestion.get('projectName', '')
            if 'projectId' not in suggestion and project_name in project_name_to_id:
                suggestion['projectId'] = project_name_to_id[project_name]

    return ai_result


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


def generate_mock_plan(projects, project_times, total_time, pending_tasks):
    """生成模拟的AI计划数据"""
    import random

    # 生成预警
    warnings = []
    for project in projects[:2]:  # 只对前两个项目生成预警
        actual_time = project_times.get(project.id, 0)
        actual_percent = int((actual_time / total_time * 100)) if total_time > 0 else 0
        target_percent = 30  # 模拟目标百分比

        if actual_percent > target_percent + 10:
            warnings.append({
                'id': f"mock_warning_{project.id}",
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
                'id': f"mock_warning_{project.id}",
                'title': f'{project.name}进度滞后',
                'message': f'{project.name}本周仅投入{actual_percent}%精力,低于目标{target_percent}%',
                'level': 'medium',
                'suggestions': [
                    {'text': f'添加{project.name}任务', 'action': 'add_task'}
                ]
            })

    # 生成推荐任务
    recommendations = []
    if pending_tasks:
        for i, task in enumerate(pending_tasks[:4]):
            project_name = next((p.name for p in projects if p.id == task.project_id), '未知项目')
            recommendations.append({
                'id': str(task.id),
                'name': task.title,
                'projectName': project_name,
                'priority': task.priority if hasattr(task, 'priority') else ['high', 'medium', 'low'][i % 3],
                'estimatedTime': ['30分钟', '45分钟', '25分钟', '15分钟'][i % 4],
                'reason': f'{project_name}项目需要加强学习' if i % 2 == 0 else '巩固相关知识'
            })

    # 生成精力分配建议
    energy_suggestions = []
    for project in projects[:3]:
        actual_time = project_times.get(project.id, 0)
        actual_percent = int((actual_time / total_time * 100)) if total_time > 0 else random.randint(10, 40)
        target_percent = random.randint(20, 40)

        energy_suggestions.append({
            'projectId': str(project.id),
            'projectName': project.name,
            'target': target_percent,
            'actual': actual_percent,
            'status': 'balanced' if abs(actual_percent - target_percent) < 10 else 'unbalanced',
            'suggestion': '保持当前学习节奏' if abs(actual_percent - target_percent) < 10 else '建议调整学习时间分配'
        })

    # 生成每日建议
    daily_tips = [
        "晚上适合回顾整理，总结今天的学习内容",
        "根据你的学习习惯，下午是你的高效时段，建议安排难点内容",
        "本周已完成5天学习，保持这个节奏！",
        "番茄工作法可以有效提高学习效率，试试25分钟专注+5分钟休息"
    ]

    return {
        'warnings': warnings,
        'recommendations': recommendations,
        'energySuggestions': energy_suggestions,
        'dailyTips': daily_tips,
        'note': '这是模拟数据，实际使用时需要配置有效的AI API密钥'
    }
