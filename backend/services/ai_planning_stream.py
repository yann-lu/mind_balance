"""
AI规划服务 - 流式输出版本
使用SSE (Server-Sent Events) 实现分块加载
"""
from sqlalchemy.orm import Session
from typing import AsyncGenerator
import json
import models
from services import ai_planning


async def generate_daily_plan_stream(
    db: Session,
    user_id: str,
    period: str = "today",
    use_ai: str = "false"
) -> AsyncGenerator[str, None]:
    """流式生成学习计划

    Args:
        db: 数据库会话
        user_id: 用户ID
        period: 时间周期
        use_ai: AI模式 ("false", "enhanced", "full")

    Yields:
        SSE格式的数据流
    """

    def sse_event(event: str, data: dict):
        """生成SSE事件格式"""
        return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"

    # 1. 立即返回规则引擎的基础数据
    try:
        # 查询项目时预加载预算信息
        from sqlalchemy.orm import selectinload
        projects = db.query(models.Project).options(
            selectinload(models.Project.budgets)
        ).filter(
            models.Project.user_id == user_id
        ).all()

        if not projects:
            yield sse_event("error", {"message": "没有找到项目"})
            return

        # 计算时间统计数据
        from datetime import date, timedelta
        start_date = date.today() - timedelta(days=7)

        time_logs = db.query(models.TimeLog).filter(
            models.TimeLog.user_id == user_id,
            models.TimeLog.log_date >= start_date
        ).all()

        project_times = {}
        for log in time_logs:
            if log.project_id not in project_times:
                project_times[log.project_id] = 0
            project_times[log.project_id] += log.duration_seconds

        total_time = sum(project_times.values()) or 1

        pending_tasks = db.query(models.Task).filter(
            models.Task.project_id.in_([p.id for p in projects]),
            models.Task.status.in_(['todo', 'pending'])
        ).all()

        # 生成规则引擎数据
        rule_result = ai_planning.generate_rule_based_plan(
            projects, project_times, total_time, pending_tasks
        )

        # 立即发送规则引擎结果
        yield sse_event("init", {
            "message": "基础数据已加载",
            "data": rule_result
        })

        # 如果不需要AI,直接结束
        if use_ai == "false":
            yield sse_event("complete", {
                "message": "计划生成完成",
                "mode": "规则引擎"
            })
            return

        # 如果需要AI,开始流式输出
        config = await ai_planning.get_active_ai_config(db, user_id)
        if not config:
            yield sse_event("warning", {
                "message": "未配置AI,使用规则引擎结果"
            })
            yield sse_event("complete", {"mode": "规则引擎"})
            return

        # AI增强模式 - 只优化推荐理由
        if use_ai == "enhanced" and rule_result.get('recommendations'):
            yield sse_event("progress", {
                "message": "AI正在优化推荐理由...",
                "step": "enhancing"
            })

            enhanced_result = await ai_planning.enhance_with_ai(
                rule_result, projects, project_times, total_time,
                pending_tasks, config
            )

            yield sse_event("update", {
                "field": "recommendations",
                "data": enhanced_result.get('recommendations', [])
            })

            yield sse_event("complete", {
                "message": "AI增强完成",
                "mode": "规则引擎 + AI增强"
            })

        # AI完整分析模式 - AI生成所有数据
        elif use_ai == "full":
            yield sse_event("progress", {
                "message": "AI正在深度分析你的学习数据...",
                "step": "analyzing",
                "progress": 20
            })

            # 构建提示词
            prompt = ai_planning.build_learning_plan_prompt(
                projects, project_times, total_time, pending_tasks
            )

            yield sse_event("progress", {
                "message": "正在调用AI生成完整分析...",
                "step": "generating",
                "progress": 40
            })

            # 调用AI生成
            import time
            from services import ai_service

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

            start_time = time.time()
            response = await service.chat(messages, temperature=0.3)
            elapsed = time.time() - start_time

            # 解析AI响应
            cleaned_response = response.strip()
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:]
            elif cleaned_response.startswith('```'):
                cleaned_response = cleaned_response[3:]
            if cleaned_response.endswith('```'):
                cleaned_response = cleaned_response[:-3]
            cleaned_response = cleaned_response.strip()

            ai_result = json.loads(cleaned_response)
            await service.close()

            yield sse_event("progress", {
                "message": "AI分析完成,正在处理结果...",
                "step": "processing",
                "progress": 80
            })

            # 增强AI结果
            enhanced_result = ai_planning._enhance_ai_result(
                ai_result, projects, project_times, total_time
            )

            # 分块发送更新
            if enhanced_result.get('warnings'):
                yield sse_event("update", {
                    "field": "warnings",
                    "data": enhanced_result['warnings']
                })

            if enhanced_result.get('recommendations'):
                yield sse_event("update", {
                    "field": "recommendations",
                    "data": enhanced_result['recommendations']
                })

            if enhanced_result.get('energySuggestions'):
                yield sse_event("update", {
                    "field": "energySuggestions",
                    "data": enhanced_result['energySuggestions']
                })

            if enhanced_result.get('dailyTips'):
                yield sse_event("update", {
                    "field": "dailyTips",
                    "data": enhanced_result['dailyTips']
                })

            yield sse_event("complete", {
                "message": f"AI完整分析完成 (耗时{elapsed:.1f}秒)",
                "mode": "AI完整分析"
            })

    except Exception as e:
        import traceback
        traceback.print_exc()
        yield sse_event("error", {
            "message": f"生成失败: {str(e)}"
        })
