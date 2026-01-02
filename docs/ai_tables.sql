-- AI配置表 (PostgreSQL语法)
CREATE TABLE IF NOT EXISTS ai_configs (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR NOT NULL,
    provider VARCHAR NOT NULL,  -- 'deepseek', 'qwen', 'openai', etc.
    api_key VARCHAR NOT NULL,
    api_base VARCHAR,  -- 自定义API端点
    model VARCHAR,  -- 使用的模型名称
    is_active BOOLEAN DEFAULT TRUE,  -- 是否为当前激活的配置
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AI对话历史表(用于上下文记忆)
CREATE TABLE IF NOT EXISTS ai_conversations (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR NOT NULL,
    role VARCHAR NOT NULL,  -- 'system', 'user', 'assistant'
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AI学习建议缓存表
CREATE TABLE IF NOT EXISTS ai_suggestions (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR NOT NULL,
    suggestion_type VARCHAR NOT NULL,  -- 'daily_plan', 'energy_warning', 'task_recommendation'
    content TEXT NOT NULL,  -- JSON格式的建议内容
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP  -- 缓存过期时间
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_ai_configs_user_active ON ai_configs(user_id, is_active);
CREATE INDEX IF NOT EXISTS idx_ai_conversations_user ON ai_conversations(user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_ai_suggestions_user_type ON ai_suggestions(user_id, suggestion_type);

-- 添加注释
COMMENT ON TABLE ai_configs IS 'AI服务配置表';
COMMENT ON TABLE ai_conversations IS 'AI对话历史记录';
COMMENT ON TABLE ai_suggestions IS 'AI生成的学习建议缓存';
