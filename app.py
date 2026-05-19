# 运行方式: streamlit run app.py
"""
个人数据库应用 - 主入口
包含登录页面、顶部Tab导航、AI助手、主题切换

运行: streamlit run app.py
"""

import streamlit as st
import os
from datetime import datetime
from utils import render_html

# 导入数据库模块
from db import (
    init_database, verify_password, has_password, set_password,
    get_skill_stats, get_academic_stats, get_resource_stats,
    get_materials_stats, get_achievements, get_recent_activities,
    check_achievements, get_recent_material_contents,
    get_skill_list, create_skill, create_academic, create_resource,
    update_skill_progress, get_connection, db_sync
)

# 自动填充模拟数据（数据库为空时）
def auto_seed_data():
    """如果数据库为空，自动填充模拟数据"""
    init_database()  # 确保表已创建
    try:
        stats = get_skill_stats()
        if stats.get('total', 0) >= 18:  # 技能数够了就跳过
            return
    except:
        pass
    
    conn = get_connection()
    cursor = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 技能 - 直接INSERT，不走create_skill
    skills_data = [
        ("Python数据分析", "编程开发", 100, "Pandas/NumPy/Matplotlib数据处理与分析", "P0", 68.0),
        ("机器学习基础", "人工智能", 80, "监督学习/非监督学习/模型评估", "P0", 45.0),
        ("SQL数据库", "数据技术", 90, "MySQL/PostgreSQL查询与优化", "P1", 55.0),
        ("产品经理方法论", "产品管理", 70, "需求分析/PRD/用户研究/A/B测试", "P1", 38.0),
        ("数据可视化", "数据分析", 85, "Plotly/ECharts/Tableau可视化设计", "P1", 50.0),
        ("LaTeX排版", "学术工具", 50, "论文排版/Beamer演示", "P2", 10.0),
        ("深度学习", "人工智能", 60, "CNN/RNN/Transformer/PyTorch", "P2", 25.0),
        ("R语言统计", "数据技术", 40, "ggplot2/dplyr/统计分析", "P2", 18.0),
        ("项目管理", "软技能", 75, "敏捷/Scrum/甘特图", "P3", 42.0),
        ("自然语言处理", "人工智能", 35, "文本分类/NER/大语言模型", "P2", 15.0),
        ("贝叶斯统计", "数学统计", 25, "先验分布/后验推断/MCMC", "P2", 15.0),
        ("假设检验", "数学统计", 30, "t检验/卡方检验/非参数检验", "P2", 15.0),
        ("两样本检验", "数学统计", 15, "独立样本/配对样本/方差分析", "P3", 15.0),
        ("Python科学计算", "编程开发", 20, "SciPy/SymPy/数值计算", "P2", 15.0),
        ("经济设计方法", "质量管理", 15, "Duncan模型/贝叶斯经济设计/控制图优化", "P2", 15.0),
        ("Swift开发", "编程开发", 10, "iOS应用开发/SwiftUI", "P3", 5.0),
        ("前端开发入门", "编程开发", 30, "HTML/CSS/JavaScript/React基础", "P3", 12.0),
        ("运筹学", "数学优化", 45, "线性规划/整数规划/排队论", "P2", 30.0),
    ]
    for name, cat, target, notes, pri, prog in skills_data:
        try:
            cursor.execute(
                "INSERT INTO growth (skill_name, category, target_level, notes, priority, progress, start_date) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (name, cat, target, notes, pri, prog, today)
            )
        except Exception as e:
            pass  # 跳过失败的，继续插入下一条

    # 学术文献
    academics_data = [
        ("Cost-Optimal Bayesian Control Chart Design for Process Monitoring", "Lam Y., Zhang L.", "Bayesian, economic design, control chart, process monitoring", "This paper proposes a Bayesian approach to the economic design of control charts.", "贝叶斯经济设计的经典文献，与毕业论文核心方法直接相关。", "贝叶斯,经济设计,质量控制,核心文献", "Quality and Reliability Engineering International", "2021-03-15"),
        ("A Deep Learning Approach for Anomaly Detection in Manufacturing Processes", "Wang J., Li X., Chen Y.", "deep learning, anomaly detection, manufacturing, autoencoder", "We propose a deep learning-based anomaly detection framework for manufacturing process monitoring.", "深度学习在质量监控中的前沿应用，可以作为论文的未来展望部分引用。", "深度学习,异常检测,制造过程", "Journal of Manufacturing Systems", "2023-06-20"),
        ("Economic Design of X-bar Control Charts: A Review and Future Directions", "Celano G., Castagliola P.", "economic design, X-bar chart, cost model, review", "This review paper summarizes the development of economic design of X-bar control charts since Duncan's seminal work in 1956.", "经济设计综述论文，覆盖了从Duncan到贝叶斯方法的完整脉络。", "经济设计,综述,控制图,必读", "Quality Engineering", "2022-09-10"),
        ("Large Language Models for Data Analysis: Capabilities and Limitations", "Chen M., Liu J., Zhao W.", "LLM, data analysis, GPT, automated analysis", "This paper investigates the capabilities and limitations of large language models in automated data analysis tasks.", "LLM做数据分析的评估论文，和信管专业数据分析和AI方向都很相关。", "大语言模型,数据分析,AI", "Proceedings of KDD 2024", "2024-08-05"),
        ("Information Systems Success Model: An Update and Extension", "DeLone W.H., McLean E.R.", "IS success model, system quality, information quality, service quality", "This paper updates and extends the DeLone and McLean IS Success Model originally proposed in 1992.", "信息系统成功模型的经典更新版，信管专业必读。", "信息系统,成功模型,经典文献", "Journal of Management Information Systems", "2003-01-01"),
        ("Attention Is All You Need", "Vaswani A., Shazeer N., Parmar N., et al.", "Transformer, attention mechanism, neural network, sequence modeling", "We propose a new simple network architecture, the Transformer, based solely on attention mechanisms.", "Transformer的开山之作，深度学习和NLP方向的基础论文。", "Transformer,注意力机制,NLP,必读", "NeurIPS 2017", "2017-06-12"),
        ("Product Management in the AI Era: Challenges and Opportunities", "Zhang R., Thompson K., Park S.", "product management, AI, agile, data-driven", "The emergence of AI-powered products creates new challenges and opportunities for product managers.", "AI时代产品管理的前沿论文，和产品经理方向高度相关。", "产品经理,AI,敏捷开发", "Harvard Business Review (Digital)", "2024-02-18"),
        ("A Survey on Bayesian Deep Learning for Quality Engineering", "Liu H., Tan M., Zhou S.", "Bayesian deep learning, quality engineering, uncertainty quantification", "We survey recent advances in Bayesian deep learning and their applications in quality engineering.", "贝叶斯深度学习在质量工程中的综述，和毕业论文方向非常契合。", "贝叶斯,深度学习,质量工程,综述", "IIE Transactions", "2023-11-25"),
    ]
    for title, authors, keywords, abstract, notes, tags, source, pub_date in academics_data:
        try:
            cursor.execute(
                "INSERT INTO academic (title, authors, keywords, abstract, notes, tags, source, publish_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (title, authors, keywords, abstract, notes, tags, source, pub_date)
            )
        except:
            pass

    # 资源
    resources_data = [
        ("Pandas官方文档 - User Guide", "编程文档", "https://pandas.pydata.org/docs/user_guide/index.html", "Pandas数据处理的官方教程", "P0", "在看"),
        ("Scikit-learn机器学习教程", "在线课程", "https://scikit-learn.org/stable/tutorial/index.html", "从基础分类到模型选择与评估的完整学习路径", "P1", "在看"),
        ("《精益数据分析》", "产品书籍", "", "数据分析驱动产品决策的经典书籍", "P1", "待看"),
        ("动手学深度学习 (d2l.ai)", "在线课程", "https://zh.d2l.ai/", "李沐团队，PyTorch版，含视频和可运行代码", "P1", "在看"),
        ("SQLZoo - SQL在线练习", "在线工具", "https://sqlzoo.net/", "交互式SQL练习平台", "P1", "已看"),
        ("《启示录：打造用户喜爱的产品》", "产品书籍", "", "产品经理圣经，Marty Cagan", "P1", "已看"),
        ("Plotly Python图表库文档", "编程文档", "https://plotly.com/python/", "交互式图表库完整文档", "P2", "待看"),
        ("LeetCode算法题库", "在线工具", "https://leetcode.cn/", "程序员面试必备算法练习平台", "P2", "在看"),
        ("《质量控制与质量管理》教材", "课程教材", "", "含SPC控制图、工序能力分析、抽样检验", "P1", "已看"),
        ("GitHub - 开源项目", "开发资源", "https://github.com/", "全球最大开源社区", "P2", "在看"),
        ("Figma - 产品原型设计", "在线工具", "https://www.figma.com/", "产品经理必备UI设计和原型工具", "P3", "待看"),
        ("贝叶斯统计入门视频 - StatQuest", "视频教程", "https://www.youtube.com/playlist?list=PLblh5JKOoLUJKCm3T02Nr6U0MIjF-4R4H", "用直觉方式讲解先验/后验/MCMC", "P2", "待看"),
    ]
    for title, cat, url, desc, pri, status in resources_data:
        try:
            cursor.execute(
                "INSERT INTO resource (title, category, url, description, priority, status) VALUES (?, ?, ?, ?, ?, ?)",
                (title, cat, url, desc, pri, status)
            )
        except:
            pass
    
    conn.commit()
    db_sync()
    conn.close()

auto_seed_data()

# 导入页面模块
from page_home import render_home_page
from page_academic import render_academic_page
from page_growth import render_growth_page
from page_resource import render_resource_page
from page_materials import render_materials_page
from page_skill import render_skill_detail_page


# ============ 主题配置 ============

def get_theme_colors(is_dark: bool = True) -> dict:
    if is_dark:
        return {
            'bg_primary': '#0f172a',
            'bg_secondary': '#1e293b',
            'bg_tertiary': '#334155',
            'text_primary': '#f1f5f9',
            'text_secondary': '#94a3b8',
            'text_muted': '#64748b',
            'accent': '#60a5fa',
            'accent_hover': '#3b82f6',
            'success': '#4ade80',
            'warning': '#facc15',
            'danger': '#f87171',
            'card_bg': '#1e293b',
            'card_border': '#334155',
            'input_bg': '#1e293b',
            'paper_bgcolor': 'rgba(0,0,0,0)',
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'chart_colors': ['#60a5fa', '#4ade80', '#facc15', '#f87171', '#a78bfa'],
        }
    else:
        return {
            'bg_primary': '#f8fafc',
            'bg_secondary': '#ffffff',
            'bg_tertiary': '#e2e8f0',
            'text_primary': '#0f172a',
            'text_secondary': '#475569',
            'text_muted': '#94a3b8',
            'accent': '#3b82f6',
            'accent_hover': '#2563eb',
            'success': '#22c55e',
            'warning': '#eab308',
            'danger': '#ef4444',
            'card_bg': '#ffffff',
            'card_border': '#e2e8f0',
            'input_bg': '#ffffff',
            'paper_bgcolor': 'rgba(0,0,0,0)',
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'chart_colors': ['#3b82f6', '#22c55e', '#eab308', '#ef4444', '#8b5cf6'],
        }


def get_theme_css(is_dark: bool) -> str:
    c = get_theme_colors(is_dark)
    return f"""
<style>
    /* 隐藏Streamlit默认元素 */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    .stDeployButton {{display: none !important;}}

    /* 全局 */
    .stApp {{
        background-color: {c['bg_primary']};
        color: {c['text_primary']};
    }}

    /* Tab样式 */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 4px;
        background-color: {c['bg_secondary']};
        border-radius: 12px;
        padding: 4px;
        margin-bottom: 1rem;
    }}
    .stTabs [data-baseweb="tab"] {{
        border-radius: 8px;
        padding: 8px 20px;
        font-size: 0.95rem;
        font-weight: 500;
        color: {c['text_secondary']};
        background-color: transparent;
        border: none;
        transition: all 0.2s;
    }}
    .stTabs [data-baseweb="tab"]:hover {{
        background-color: {c['bg_tertiary']};
        color: {c['text_primary']};
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {c['accent']} !important;
        color: white !important;
    }}

    /* 卡片 */
    .stat-card {{
        background: {c['card_bg']};
        border: 1px solid {c['card_border']};
        border-radius: 12px;
        padding: 1.2rem;
        transition: all 0.2s;
        text-align: center;
    }}
    .stat-icon {{
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }}
    .stat-value {{
        font-size: 2rem;
        font-weight: 700;
        color: {c['accent']};
        line-height: 1.2;
    }}
    .stat-label {{
        color: {c['text_secondary']};
        font-size: 0.85rem;
        margin-top: 0.25rem;
    }}
    .content-card {{
        background: {c['card_bg']};
        border: 1px solid {c['card_border']};
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
        transition: all 0.2s;
    }}
    .content-card:hover {{
        border-color: {c['accent']};
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }}

    /* 欢迎区域 */
    .welcome-section {{
        background: {c['card_bg']};
        border: 1px solid {c['card_border']};
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    }}
    .welcome-title {{
        font-size: 1.8rem;
        font-weight: 600;
        color: {c['text_primary']};
        margin: 0;
    }}
    .welcome-subtitle {{
        color: {c['text_secondary']};
        font-size: 1rem;
        margin: 0.5rem 0 0 0;
    }}

    /* 输入框 */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {{
        background-color: {c['input_bg']};
        color: {c['text_primary']};
        border-color: {c['card_border']};
        border-radius: 8px;
    }}

    /* 按钮 */
    .stButton > button {{
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.2s;
    }}
    .stButton > button:hover {{
        transform: translateY(-1px);
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
    }}

    /* 进度条 */
    .stProgress > div > div > div {{
        border-radius: 8px;
    }}
    .progress-bar {{
        background: {c['bg_tertiary']};
        border-radius: 8px;
        overflow: hidden;
        height: 8px;
    }}
    .progress-fill {{
        height: 100%;
        background: linear-gradient(90deg, {c['accent']}, {c['success']});
        border-radius: 8px;
        transition: width 0.3s ease;
    }}

    /* 活动列表 */
    .activity-item {{
        display: flex;
        align-items: center;
        padding: 0.75rem 0;
        border-bottom: 1px solid {c['card_border']};
    }}
    .activity-icon {{
        font-size: 1.5rem;
        margin-right: 0.75rem;
    }}
    .activity-content {{
        flex: 1;
    }}
    .activity-title {{
        color: {c['text_primary']};
        font-weight: 500;
    }}
    .activity-meta {{
        color: {c['text_muted']};
        font-size: 0.85rem;
    }}

    /* 选择框 */
    .stSelectbox > div > div {{
        background-color: {c['input_bg']};
        color: {c['text_primary']};
    }}

    /* 对话框 */
    .ai-chat-box {{
        background: {c['bg_secondary']};
        border: 1px solid {c['card_border']};
        border-radius: 12px;
        padding: 1rem;
        max-height: 400px;
        overflow-y: auto;
    }}
    .ai-msg-user {{
        background: {c['accent']};
        color: white;
        padding: 0.6rem 1rem;
        border-radius: 12px 12px 4px 12px;
        margin: 0.5rem 0;
        max-width: 80%;
        margin-left: auto;
    }}
    .ai-msg-bot {{
        background: {c['bg_tertiary']};
        color: {c['text_primary']};
        padding: 0.6rem 1rem;
        border-radius: 12px 12px 12px 4px;
        margin: 0.5rem 0;
        max-width: 80%;
    }}
</style>
"""


# ============ Session State ============

def init_session_state():
    defaults = {
        'logged_in': False,
        'guest_mode': False,
        'theme': 'dark',
        'current_page': 'home',
        'view_item_id': None,
        'view_item_type': None,
        'ai_expanded': False,
        'chat_messages': [],
        'show_password_change': False,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


# ============ 登录页 ============

def render_login_page():
    """渲染登录页面"""
    is_dark = st.session_state.get('theme', 'dark') == 'dark'
    colors = get_theme_colors(is_dark)

    # 居中布局
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        render_html(f"""
        <div style="text-align: center; padding: 3rem 0;">
            <h1 style="font-size: 2.5rem; margin-bottom: 0.5rem;">🗄️ 个人数据库</h1>
            <p style="color: {colors['text_secondary']}; font-size: 1.1rem;">你的学习 · 研究 · 成长管理中心</p>
        </div>
        """)

        # 主题切换
        theme_col1, theme_col2, theme_col3 = st.columns([2, 1, 2])
        with theme_col2:
            if st.button("☀️/🌙 切换主题", use_container_width=True):
                st.session_state['theme'] = 'light' if st.session_state['theme'] == 'dark' else 'dark'
                st.rerun()

        st.markdown("---")

        if not has_password():
            # 首次设置密码
            st.markdown("### 🔑 首次使用，请设置密码")
            pwd1 = st.text_input("设置密码", type="password", key="login_pwd1")
            pwd2 = st.text_input("确认密码", type="password", key="login_pwd2")

            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("✅ 确认设置", type="primary", use_container_width=True):
                    if not pwd1:
                        st.error("请输入密码")
                    elif pwd1 != pwd2:
                        st.error("两次密码不一致")
                    elif len(pwd1) < 4:
                        st.error("密码至少4位")
                    else:
                        set_password(pwd1)
                        st.session_state['logged_in'] = True
                        st.session_state['guest_mode'] = False
                        st.success("设置成功！")
                        st.rerun()
            with col_btn2:
                if st.button("👁️ 访客模式进入", use_container_width=True):
                    st.session_state['logged_in'] = True
                    st.session_state['guest_mode'] = True
                    st.rerun()
        else:
            # 密码登录
            st.markdown("### 🔐 登录")
            password = st.text_input("密码", type="password", key="login_pwd")

            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("🔓 登录", type="primary", use_container_width=True):
                    if verify_password(password):
                        st.session_state['logged_in'] = True
                        st.session_state['guest_mode'] = False
                        st.rerun()
                    else:
                        st.error("密码错误")
            with col_btn2:
                if st.button("👁️ 访客模式", use_container_width=True):
                    st.session_state['logged_in'] = True
                    st.session_state['guest_mode'] = True
                    st.rerun()


# ============ AI 助手 ============

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")


def get_ai_response(messages: list) -> str:
    """调用DeepSeek API获取回复"""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)

        # 获取最近上传的资料内容
        recent_materials = get_recent_material_contents(limit=5)
        materials_summary = ""
        if recent_materials:
            materials_summary = "\n\n最近上传的学习资料：\n"
            for m in recent_materials:
                title = m.get('file_name', '未知文件')
                content = m.get('content_text', '')
                if content and len(content) > 500:
                    content = content[:500] + "..."
                elif not content:
                    content = "(未提取到文本内容)"
                materials_summary += f"【{title}】\n{content}\n\n"

        # 构建系统提示
        db_stats = f"""
你是一个学习管理AI助手。用户的学习数据概况：
- 技能统计：{get_skill_stats()}
- 学术文献：{get_academic_stats()}篇
- 资源数量：{get_resource_stats()}个
- 学习资料：{get_materials_stats()}份{materials_summary}

请用简洁、亲切的语气回答，给出可操作的建议。如果用户询问关于学习资料的问题，请参考上述资料摘要内容进行回答。
"""
        system_msg = {"role": "system", "content": db_stats}
        full_messages = [system_msg] + messages[-10:]  # 保留最近10条

        response = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=full_messages,
            max_tokens=800,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"抱歉，AI服务暂时不可用。错误信息：{str(e)}"


def render_ai_section():
    """渲染AI助手区域"""
    is_dark = st.session_state.get('theme', 'dark') == 'dark'

    # 切换按钮
    col1, col2 = st.columns([4, 1])
    with col2:
        btn_label = "✕ 关闭" if st.session_state.get('ai_expanded') else "🤖 AI助手"
        if st.button(btn_label, key="ai_toggle", use_container_width=True):
            st.session_state['ai_expanded'] = not st.session_state['ai_expanded']
            st.rerun()

    if not st.session_state.get('ai_expanded'):
        return

    st.markdown("---")

    # 快捷按钮
    q1, q2, q3 = st.columns(3)
    with q1:
        if st.button("📊 学习分析", use_container_width=True, key="q_analysis"):
            st.session_state['chat_messages'].append(
                {"role": "user", "content": "请分析我当前的学习进度，给我一些提升建议。"}
            )
    with q2:
        if st.button("📚 今日推荐", use_container_width=True, key="q_recommend"):
            st.session_state['chat_messages'].append(
                {"role": "user", "content": "根据我的学习计划，推荐今天应该学习什么。"}
            )
    with q3:
        if st.button("📈 周报总结", use_container_width=True, key="q_weekly"):
            st.session_state['chat_messages'].append(
                {"role": "user", "content": "帮我总结本周的学习情况。"}
            )

    # 处理快捷消息
    if st.session_state['chat_messages'] and st.session_state['chat_messages'][-1]['role'] == 'user':
        last_msg = st.session_state['chat_messages'][-1]
        # 避免重复处理
        if not st.session_state.get('_ai_processing'):
            st.session_state['_ai_processing'] = True
            with st.spinner("AI思考中..."):
                response = get_ai_response(st.session_state['chat_messages'])
            st.session_state['chat_messages'].append({"role": "assistant", "content": response})
            st.session_state['_ai_processing'] = False
            st.rerun()

    # 显示对话历史
    colors = get_theme_colors(is_dark)
    for msg in st.session_state['chat_messages']:
        if msg['role'] == 'user':
            render_html(f'<div class="ai-msg-user">{msg["content"]}</div>')
        else:
            render_html(f'<div class="ai-msg-bot">{msg["content"]}</div>')

    # 输入框
    user_input = st.text_input("输入问题...", key="ai_input", placeholder="问我任何关于学习的问题...")
    if st.button("发送", key="ai_send", type="primary") and user_input:
        st.session_state['chat_messages'].append({"role": "user", "content": user_input})
        st.rerun()


# ============ 详情页 ============

def render_academic_detail_page(academic_id: int):
    """渲染学术文献详情页"""
    from db import get_academic_by_id, update_academic, delete_academic

    academic = get_academic_by_id(academic_id)
    if not academic:
        st.error("文献不存在")
        if st.button("返回"):
            st.session_state['view_item_id'] = None
            st.session_state['view_item_type'] = None
            st.rerun()
        return

    is_guest = st.session_state.get('guest_mode', False)

    if st.button("← 返回列表", key=f"back_aca_{academic_id}"):
        st.session_state['view_item_id'] = None
        st.session_state['view_item_type'] = None
        st.rerun()

    st.markdown("---")
    st.markdown(f"### 📄 {academic['title']}")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"**👥 作者**: {academic.get('authors', '未知')}")
    with col2:
        st.markdown(f"**📅 日期**: {academic.get('publish_date', '未知')}")
    with col3:
        st.markdown(f"**📚 来源**: {academic.get('source', '未知')}")

    if academic.get('keywords'):
        st.markdown(f"**🏷️ 关键词**: {academic['keywords']}")
    if academic.get('tags'):
        st.markdown(f"**📌 标签**: {academic['tags']}")
    if academic.get('abstract'):
        st.markdown("**📝 摘要**")
        st.markdown(academic['abstract'])
    if academic.get('notes'):
        st.markdown("**📒 笔记**")
        st.markdown(academic['notes'])

    # 编辑
    if not is_guest:
        st.markdown("---")
        with st.expander("✏️ 编辑文献"):
            with st.form(key=f"edit_aca_form_{academic_id}"):
                title = st.text_input("标题", value=academic['title'], key="ed_aca_title")
                authors = st.text_input("作者", value=academic.get('authors', ''), key="ed_aca_authors")
                keywords = st.text_input("关键词", value=academic.get('keywords', ''), key="ed_aca_kw")
                abstract = st.text_area("摘要", value=academic.get('abstract', ''), key="ed_aca_abs", height=150)
                notes = st.text_area("笔记", value=academic.get('notes', ''), key="ed_aca_notes", height=100)
                tags = st.text_input("标签", value=academic.get('tags', ''), key="ed_aca_tags")
                source = st.text_input("来源", value=academic.get('source', ''), key="ed_aca_src")
                publish_date = st.text_input("发布日期", value=academic.get('publish_date', ''), key="ed_aca_date")

                if st.form_submit_button("💾 保存修改", type="primary"):
                    update_academic(academic_id,
                        title=title, authors=authors, keywords=keywords,
                        abstract=abstract, notes=notes, tags=tags,
                        source=source, publish_date=publish_date
                    )
                    st.success("修改已保存！")
                    st.rerun()

        if st.button("🗑️ 删除文献", key=f"del_aca_{academic_id}", type="secondary"):
            delete_academic(academic_id)
            st.session_state['view_item_id'] = None
            st.session_state['view_item_type'] = None
            st.success("已删除")
            st.rerun()


def render_resource_detail_page(resource_id: int):
    """渲染资源详情页"""
    from db import get_resource_by_id, update_resource, delete_resource

    resource = get_resource_by_id(resource_id)
    if not resource:
        st.error("资源不存在")
        if st.button("返回"):
            st.session_state['view_item_id'] = None
            st.session_state['view_item_type'] = None
            st.rerun()
        return

    is_guest = st.session_state.get('guest_mode', False)

    if st.button("← 返回列表", key=f"back_res_{resource_id}"):
        st.session_state['view_item_id'] = None
        st.session_state['view_item_type'] = None
        st.rerun()

    st.markdown("---")
    st.markdown(f"### 🔗 {resource['title']}")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"**📁 分类**: {resource.get('category', '未分类')}")
    with col2:
        st.markdown(f"**⭐ 优先级**: {resource.get('priority', 'P2')}")
    with col3:
        st.markdown(f"**📊 状态**: {resource.get('status', '待看')}")

    if resource.get('url'):
        st.markdown(f"**🔗 链接**: [{resource['url']}]({resource['url']})")
    if resource.get('description'):
        st.markdown("**📝 描述**")
        st.markdown(resource['description'])

    # 状态切换
    if not is_guest:
        st.markdown("---")
        statuses = ["待看", "在看", "已看", "收藏"]
        s_cols = st.columns(len(statuses))
        for i, status in enumerate(statuses):
            with s_cols[i]:
                is_current = resource.get('status') == status
                if st.button(
                    status,
                    type="primary" if is_current else "secondary",
                    key=f"res_status_{resource_id}_{status}",
                    use_container_width=True
                ):
                    update_resource(resource_id, status=status)
                    st.rerun()

        with st.expander("✏️ 编辑资源"):
            with st.form(key=f"edit_res_form_{resource_id}"):
                title = st.text_input("标题", value=resource['title'], key="ed_res_title")
                category = st.text_input("分类", value=resource.get('category', ''), key="ed_res_cat")
                url = st.text_input("链接", value=resource.get('url', ''), key="ed_res_url")
                desc = st.text_area("描述", value=resource.get('description', ''), key="ed_res_desc")
                priority = st.selectbox("优先级", ["P0", "P1", "P2", "P3"],
                    index=["P0","P1","P2","P3"].index(resource.get('priority', 'P2')),
                    key="ed_res_pri")

                if st.form_submit_button("💾 保存修改", type="primary"):
                    update_resource(resource_id, title=title, category=category,
                        url=url, description=desc, priority=priority)
                    st.success("修改已保存！")
                    st.rerun()

        if st.button("🗑️ 删除资源", key=f"del_res_{resource_id}", type="secondary"):
            delete_resource(resource_id)
            st.session_state['view_item_id'] = None
            st.session_state['view_item_type'] = None
            st.success("已删除")
            st.rerun()


# ============ 主函数 ============

def main():
    """主函数"""
    st.set_page_config(
        page_title="个人数据库",
        page_icon="🗄️",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    init_database()
    init_session_state()

    is_dark = st.session_state.get('theme', 'dark') == 'dark'
    render_html(get_theme_css(is_dark))

    # 未登录
    if not st.session_state.get('logged_in', False):
        render_login_page()
        return

    # 顶部栏：标题 + 主题切换 + 退出
    hdr_col1, hdr_col2, hdr_col3, hdr_col4 = st.columns([3, 1, 1, 1])
    with hdr_col1:
        guest_tag = " 👁️访客" if st.session_state.get('guest_mode') else ""
        st.markdown(f"### 🗄️ 个人数据库{guest_tag}")
    with hdr_col2:
        theme_label = "☀️ 亮色" if is_dark else "🌙 暗色"
        if st.button(theme_label, key="theme_toggle", use_container_width=True):
            st.session_state['theme'] = 'light' if st.session_state['theme'] == 'dark' else 'dark'
            st.rerun()
    with hdr_col3:
        if st.button("🔑 改密码", key="change_pwd_btn", use_container_width=True):
            st.session_state['show_password_change'] = not st.session_state.get('show_password_change', False)
            st.rerun()
    with hdr_col4:
        if st.button("🚪 退出", key="logout_btn", use_container_width=True):
            st.session_state['logged_in'] = False
            st.session_state['guest_mode'] = False
            st.rerun()

    # 修改密码
    if st.session_state.get('show_password_change') and not st.session_state.get('guest_mode'):
        with st.expander("🔑 修改密码", expanded=True):
            old_pwd = st.text_input("当前密码", type="password", key="old_pwd")
            new_pwd = st.text_input("新密码", type="password", key="new_pwd")
            confirm_pwd = st.text_input("确认新密码", type="password", key="confirm_pwd")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("确认修改", type="primary", key="confirm_pwd_change"):
                    if not verify_password(old_pwd):
                        st.error("当前密码错误")
                    elif new_pwd != confirm_pwd:
                        st.error("两次密码不一致")
                    elif len(new_pwd) < 4:
                        st.error("新密码至少4位")
                    else:
                        set_password(new_pwd)
                        st.success("密码修改成功！")
                        st.session_state['show_password_change'] = False
                        st.rerun()
            with c2:
                if st.button("取消", key="cancel_pwd_change"):
                    st.session_state['show_password_change'] = False
                    st.rerun()

    # === 检查是否要显示详情页 ===
    view_item_id = st.session_state.get('view_item_id')
    view_item_type = st.session_state.get('view_item_type')

    if view_item_id is not None and view_item_type == 'skill':
        render_skill_detail_page(view_item_id)
        render_ai_section()
        return

    if view_item_id is not None and view_item_type == 'academic':
        render_academic_detail_page(view_item_id)
        render_ai_section()
        return

    if view_item_id is not None and view_item_type == 'resource':
        render_resource_detail_page(view_item_id)
        render_ai_section()
        return

    # === Tab导航 ===
    # 记住上次选中的Tab
    current_tab = st.session_state.get('current_tab', 0)

    tab_home, tab_academic, tab_growth, tab_resource, tab_materials = st.tabs(
        ["🏠 首页", "📖 学术库", "🌱 成长库", "🔗 资源库", "📚 学习资料"]
    )

    # 各Tab渲染并记录活跃Tab
    with tab_home:
        st.session_state['current_tab'] = 0
        render_home_page()

    with tab_academic:
        st.session_state['current_tab'] = 1
        render_academic_page()

    with tab_growth:
        st.session_state['current_tab'] = 2
        render_growth_page()

    with tab_resource:
        st.session_state['current_tab'] = 3
        render_resource_page()

    with tab_materials:
        st.session_state['current_tab'] = 4
        render_materials_page()

    # AI助手
    render_ai_section()


if __name__ == "__main__":
    main()
