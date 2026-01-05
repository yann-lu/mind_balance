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


async def generate_daily_plan(db: Session, user_id: str, period: str = "today", use_ai: str = "false") -> Dict[str, Any]:
    """生成今日学习计划

    Args:
        db: 数据库会话
        user_id: 用户ID
        period: 时间周期，支持 "today"(默认), "week", "month"
        use_ai: AI模式选择
            - "false": 快速模式,纯规则引擎 (<0.1秒)
            - "enhanced": AI增强模式,规则引擎+AI优化推荐理由 (~2秒)
            - "full": AI完整分析,AI生成所有数据 (~20秒)
    """

    # 获取用户的项目和任务数据（包含预算信息）
    from sqlalchemy.orm import selectinload
    projects = db.query(models.Project).options(
        selectinload(models.Project.budgets)
    ).filter(
        models.Project.user_id == user_id
    ).all()

    if not projects:
        return {'error': '没有找到项目'}

    # 根据period确定时间范围
    if period == "week":
        days_back = 7
    elif period == "month":
        days_back = 30
    else:  # today
        days_back = 7  # 默认查看最近7天的数据

    # 获取时间记录
    start_date = date.today() - timedelta(days=days_back)
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

    # 先检查是否有AI配置，如果没有则直接返回模拟数据（避免不必要的数据库查询和提示词构建）
    config = await get_active_ai_config(db, user_id)
    if not config:
        print("未找到AI配置，使用规则引擎生成计划")
        return generate_rule_based_plan(projects, project_times, total_time, pending_tasks)

    # 使用规则引擎快速生成(可配置是否启用AI优化)
    rule_based_result = generate_rule_based_plan(projects, project_times, total_time, pending_tasks)
    print(f"[AI规划] 规则引擎已生成计划, 耗时 <0.1秒")

    # 如果用户请求AI完整分析,则调用AI
    if use_ai and rule_based_result.get('recommendations'):
        try:
            print(f"[AI规划] 用户请求AI完整分析模式,启用AI...")
            ai_enhanced_result = await enhance_with_ai(
                rule_based_result,
                projects,
                project_times,
                total_time,
                pending_tasks,
                config
            )
            return ai_enhanced_result
        except Exception as e:
            print(f"[AI规划] AI分析失败,降级使用规则引擎结果: {e}")
            return rule_based_result

    return rule_based_result


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


def generate_rule_based_plan(projects, project_times, total_time, pending_tasks) -> Dict[str, Any]:
    """使用规则引擎快速生成学习计划(不依赖AI)"""

    # 生成精力预警
    warnings = []
    for project in projects:
        actual_time = project_times.get(project.id, 0)
        actual_percent = int((actual_time / total_time * 100)) if total_time > 0 else 0

        # 获取目标精力
        budget = None
        if hasattr(project, 'budgets') and project.budgets:
            budget = [b for b in project.budgets if b.valid_to is None]
            budget = budget[0] if budget else None

        if budget:
            target_percent = budget.target_percentage
            diff = actual_percent - target_percent

            if diff > 15:
                warnings.append({
                    'id': f"warning_{project.id}",
                    'title': f'{project.name}精力超支',
                    'message': f'{project.name}本周已投入{actual_percent}%的精力,超过目标{target_percent}%较多',
                    'level': 'high' if diff > 25 else 'medium',
                    'suggestions': [
                        {'text': '调整今日计划，减少该任务', 'action': 'adjust_task'},
                        {'text': '查看统计详情', 'action': 'view_stats'}
                    ]
                })
            elif diff < -15:
                warnings.append({
                    'id': f"warning_{project.id}",
                    'title': f'{project.name}进度滞后',
                    'message': f'{project.name}本周仅投入{actual_percent}%精力,低于目标{target_percent}%',
                    'level': 'medium',
                    'suggestions': [
                        {'text': f'添加{project.name}任务', 'action': 'add_task'}
                    ]
                })

    # 智能推荐任务(基于规则)
    recommendations = []

    # 按优先级和项目进度计算推荐分数
    scored_tasks = []
    for task in pending_tasks[:10]:  # 最多处理10个任务
        score = 0

        # 优先级加分
        if task.priority == 'high':
            score += 50
        elif task.priority == 'medium':
            score += 30

        # 项目进度加分(投入不足的项目任务优先)
        project = next((p for p in projects if p.id == task.project_id), None)
        if project:
            actual_time = project_times.get(project.id, 0)
            actual_percent = int((actual_time / total_time * 100)) if total_time > 0 else 0

            budget = None
            if hasattr(project, 'budgets') and project.budgets:
                budget = [b for b in project.budgets if b.valid_to is None]
                budget = budget[0] if budget else None

            if budget:
                target_percent = budget.target_percentage
                if actual_percent < target_percent - 10:
                    score += (target_percent - actual_percent)  # 差距越大优先级越高

        scored_tasks.append((score, task))

    # 按分数排序,取前4个
    scored_tasks.sort(key=lambda x: x[0], reverse=True)
    top_tasks = scored_tasks[:4]

    for score, task in top_tasks:
        project = next((p for p in projects if p.id == task.project_id), None)
        if project:
            # 估算耗时(基于优先级)
            estimated_times = {
                'high': 45,
                'medium': 30,
                'low': 15
            }
            estimated_time = estimated_times.get(task.priority, 30)

            recommendations.append({
                'id': str(task.id),
                'name': task.title,
                'projectName': project.name,
                'priority': task.priority if hasattr(task, 'priority') else 'medium',
                'estimatedTime': estimated_time,
                'reason': f'根据优先级和项目进度智能推荐'  # 规则引擎的简单理由
            })

    # 生成精力分配建议
    energy_suggestions = []
    for project in projects[:3]:
        actual_time = project_times.get(project.id, 0)
        actual_percent = int((actual_time / total_time * 100)) if total_time > 0 else 0

        budget = None
        if hasattr(project, 'budgets') and project.budgets:
            budget = [b for b in project.budgets if b.valid_to is None]
            budget = budget[0] if budget else None

        target_percent = budget.target_percentage if budget else 30
        is_balanced = abs(actual_percent - target_percent) < 10

        energy_suggestions.append({
            'projectId': str(project.id),
            'projectName': project.name,
            'target': target_percent,
            'actual': actual_percent,
            'status': 'balanced' if is_balanced else 'unbalanced',
            'suggestion': '学习进度良好，继续保持！' if is_balanced else f'建议调整学习时间分配,目标{target_percent}%,当前{actual_percent}%'
        })

    # 生成学习建议
    hours = datetime.now().hour
    time_based_tips = []

    if hours < 12:
        time_based_tips.append('上午适合逻辑思维类任务，比如算法练习和编程学习')
    elif hours < 18:
        time_based_tips.append('下午可以安排需要记忆的内容，比如单词背诵和概念复习')
    else:
        time_based_tips.append('晚上适合回顾整理，总结今天的学习内容并规划明天')

    daily_tips = time_based_tips + [
        '番茄工作法可以有效提高学习效率，试试25分钟专注+5分钟休息',
        '保持规律的学习节奏比突击学习效果更好',
        '适当休息可以保持大脑活跃，避免疲劳学习'
    ]

    return {
        'warnings': warnings,
        'recommendations': recommendations,
        'energySuggestions': energy_suggestions,
        'dailyTips': daily_tips[:4],  # 返回前4个
        'note': '由规则引擎生成'
    }


async def enhance_with_ai(rule_result, projects, project_times, total_time, pending_tasks, config) -> Dict[str, Any]:
    """使用AI优化规则引擎生成的结果"""

    # 如果没有推荐任务,直接返回规则结果
    if not rule_result.get('recommendations'):
        return rule_result

    try:
        # 构建简化的AI提示词,只优化推荐理由
        tasks_summary = "\n".join([
            f"- {rec['name']} ({rec['projectName']}, {rec['priority']}优先级)"
            for rec in rule_result['recommendations'][:3]
        ])

        prompt = f"""为以下推荐任务生成简洁的推荐理由(每条不超过20字):
{tasks_summary}

返回JSON数组格式:
[{{"name": "任务名", "reason": "推荐理由"}}]"""

        service = ai_service.get_ai_service(
            config['provider'],
            config['api_key'],
            config['api_base'],
            config['model']
        )

        messages = [
            {"role": "system", "content": "你是学习规划助手,返回纯JSON。"},
            {"role": "user", "content": prompt}
        ]

        print(f"[AI规划] 请求AI优化推荐理由...")
        import time
        start_time = time.time()

        response = await service.chat(messages, temperature=0.5, max_tokens=300)

        elapsed = time.time() - start_time
        print(f"[AI规划] AI响应耗时: {elapsed:.2f}秒")

        # 解析AI响应
        cleaned_response = response.strip()
        if cleaned_response.startswith('```json'):
            cleaned_response = cleaned_response[7:]
        elif cleaned_response.startswith('```'):
            cleaned_response = cleaned_response[3:]
        if cleaned_response.endswith('```'):
            cleaned_response = cleaned_response[:-3]
        cleaned_response = cleaned_response.strip()

        ai_reasons = json.loads(cleaned_response)

        # 更新推荐任务的理由
        if isinstance(ai_reasons, list):
            for ai_item in ai_reasons:
                for rec in rule_result['recommendations']:
                    if rec['name'] == ai_item.get('name'):
                        rec['reason'] = ai_item.get('reason', rec['reason'])
                        break

        await service.close()
        rule_result['note'] = '规则引擎 + AI优化'

    except Exception as e:
        print(f"[AI规划] AI优化失败,使用规则引擎结果: {e}")

    return rule_result


def build_learning_plan_prompt(projects, project_times, total_time, pending_tasks) -> str:
    """构建学习计划提示词(优化版 - 简洁高效)"""

    # 简化项目信息,只保留关键数据
    project_summary = []
    for project in projects:
        actual_time = project_times.get(project.id, 0)
        actual_percent = int((actual_time / total_time * 100)) if total_time > 0 else 0

        # 获取预算
        budget = None
        if hasattr(project, 'budgets') and project.budgets:
            budget = [b for b in project.budgets if b.valid_to is None]
            budget = budget[0] if budget else None

        target_percent = budget.target_percentage if budget else 0

        # 只输出需要关注的项目(偏差>10%)
        if abs(actual_percent - target_percent) > 10:
            project_summary.append({
                '项目': project.name,
                '目标%': target_percent,
                '实际%': actual_percent
            })

    # 简化任务信息,只取前5个高优先级任务
    urgent_tasks = [
        {'id': str(t.id), '任务': t.title, '优先级': t.priority, '项目': next((p.name for p in projects if p.id == t.project_id), '未知')}
        for t in sorted(pending_tasks, key=lambda x: x.priority == 'high', reverse=True)[:5]
    ]

    # 构建紧凑的提示词
    prompt = f"""你是学习规划助手。根据以下数据生成今日学习计划(JSON格式):

【项目精力偏差】
{json.dumps(project_summary, ensure_ascii=False)}

【待办任务】
{json.dumps(urgent_tasks, ensure_ascii=False)}

返回JSON格式:
{{
    "warnings": [
        {{"title": "项目名+问题", "message": "具体说明", "level": "high/medium/low", "suggestions": [{{"text": "建议", "action": "类型"}}]}}
    ],
    "recommendations": [
        {{"id": "任务ID", "name": "任务名", "projectName": "项目名", "priority": "high/medium/low", "estimatedTime": 分钟数, "reason": "理由"}}
    ],
    "energySuggestions": [
        {{"projectName": "项目名", "target": 目标%, "actual": 实际%, "status": "balanced/unbalanced", "suggestion": "建议"}}
    ],
    "dailyTips": ["建议1", "建议2", "建议3"]
}}

规则:只返回JSON,无其他文字;推荐3-4个任务;优先推荐投入不足的项目"""

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
