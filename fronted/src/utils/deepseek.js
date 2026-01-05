/**
 * DeepSeek API 测试工具
 * 用于测试 DeepSeek API 连接是否正常
 */

const DEEPSEEK_API_URL = 'https://api.deepseek.com/v1/chat/completions'
const DEEPSEEK_API_KEY = 'sk-a441e98ec8cb48539321b99033a037a5'

/**
 * 测试 DeepSeek API 连接
 * @param {string} testMessage - 测试消息
 * @returns {Promise<{success: boolean, message: string, data?: any}>}
 */
export async function testDeepSeekAPI(testMessage = '你好，请用一句话介绍你自己') {
  try {
    console.log('开始测试 DeepSeek API...')
    console.log('API URL:', DEEPSEEK_API_URL)
    console.log('测试消息:', testMessage)

    const requestBody = {
      model: 'deepseek-chat',
      messages: [
        {
          role: 'user',
          content: testMessage
        }
      ],
      temperature: 0.7,
      max_tokens: 1000
    }

    const response = await fetch(DEEPSEEK_API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${DEEPSEEK_API_KEY}`
      },
      body: JSON.stringify(requestBody)
    })

    console.log('响应状态:', response.status)

    if (!response.ok) {
      const errorText = await response.text()
      console.error('API 错误响应:', errorText)

      return {
        success: false,
        message: `API 请求失败: ${response.status} ${response.statusText}`,
        error: errorText
      }
    }

    const data = await response.json()
    console.log('API 响应数据:', data)

    if (data.choices && data.choices.length > 0) {
      const reply = data.choices[0].message.content
      console.log('AI 回复:', reply)

      return {
        success: true,
        message: 'API 调用成功！',
        data: {
          reply: reply,
          fullResponse: data
        }
      }
    } else {
      return {
        success: false,
        message: 'API 返回数据格式异常',
        data: data
      }
    }
  } catch (error) {
    console.error('DeepSeek API 测试失败:', error)

    return {
      success: false,
      message: `网络错误: ${error.message}`,
      error: error
    }
  }
}

/**
 * 生成学习计划的 API 调用示例
 * @param {Object} params - 计划参数
 * @returns {Promise<{success: boolean, message: string, data?: any}>}
 */
export async function generateStudyPlan(params = {}) {
  try {
    console.log('生成学习计划，参数:', params)

    const prompt = `请根据以下信息为我生成学习计划：
时间段：${params.period || '今天'}
学习目标：${params.goals || '提高学习效率'}
注意：请以JSON格式返回，包含推荐任务、精力预警和学习建议`

    const response = await fetch(DEEPSEEK_API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${DEEPSEEK_API_KEY}`
      },
      body: JSON.stringify({
        model: 'deepseek-chat',
        messages: [
          {
            role: 'system',
            content: '你是一个专业的学习规划助手，擅长根据用户情况制定个性化学习计划。'
          },
          {
            role: 'user',
            content: prompt
          }
        ],
        temperature: 0.8,
        max_tokens: 2000
      })
    })

    if (!response.ok) {
      throw new Error(`API 请求失败: ${response.status}`)
    }

    const data = await response.json()

    return {
      success: true,
      message: '学习计划生成成功',
      data: {
        reply: data.choices[0].message.content,
        fullResponse: data
      }
    }
  } catch (error) {
    console.error('生成学习计划失败:', error)

    return {
      success: false,
      message: `生成失败: ${error.message}`,
      error: error
    }
  }
}
