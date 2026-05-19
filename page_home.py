"""
首页模块
显示总览仪表盘，包含所有模块的统计概览
"""

import streamlit as st
from utils import render_html
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

from db import (
    get_skill_stats, get_academic_stats, get_resource_stats,
    get_materials_stats, get_skill_list, get_recent_activities,
    get_skills_by_priority, get_lowest_progress_skill
)


def get_theme_colors() -> dict:
    """获取当前主题颜色"""
    is_dark = st.session_state.get('theme', 'dark') == 'dark'
    if is_dark:
        return {
            'bg_primary': '#0d1b2a',
            'bg_secondary': '#1b263b',
            'bg_tertiary': '#334155',
            'text_primary': '#e0e1dd',
            'text_secondary': '#a0aec0',
            'text_muted': '#64748b',
            'accent': '#60a5fa',
            'success': '#4ade80',
            'warning': '#facc15',
            'danger': '#ef4444',
            'card_border': '#415a77',
            'chart_success': '#4ade80',
            'chart_warning': '#facc15',
            'chart_muted': '#64748b',
            'paper_bgcolor': 'rgba(0,0,0,0)',
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'font_color': '#e0e1dd',
        }
    else:
        return {
            'bg_primary': '#f8fafc',
            'bg_secondary': '#ffffff',
            'bg_tertiary': '#e2e8f0',
            'text_primary': '#1e293b',
            'text_secondary': '#475569',
            'text_muted': '#94a3b8',
            'accent': '#3b82f6',
            'success': '#22c55e',
            'warning': '#eab308',
            'danger': '#ef4444',
            'card_border': '#cbd5e1',
            'chart_success': '#22c55e',
            'chart_warning': '#eab308',
            'chart_muted': '#94a3b8',
            'paper_bgcolor': 'rgba(0,0,0,0)',
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'font_color': '#1e293b',
        }


def render_home_page():
    """
    渲染首页仪表盘
    """
    colors = get_theme_colors()
    
    # 获取统计数据
    skill_stats = get_skill_stats()
    academic_stats = get_academic_stats()
    resource_stats = get_resource_stats()
    materials_stats = get_materials_stats()
    
    # 欢迎信息区域
    welcome_html = f"""
    <div class="welcome-section">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h1 class="welcome-title">👋 欢迎回来！</h1>
                <p class="welcome-subtitle">
                    📅 {datetime.now().strftime('%Y年%m月%d日 %A')} · 
                    <span style="color: {colors['accent']};">继续你的学习之旅</span>
                </p>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 2.5rem;">🌟</div>
                <p style="color: {colors['text_muted']}; font-size: 0.85rem;">保持学习热情</p>
            </div>
        </div>
    </div>
    """
    render_html(welcome_html)
    
    # 概览统计卡片
    st.markdown("### 📊 数据概览")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # 学术文献卡片
    with col1:
        render_html(f"""
        <div class="stat-card" style="border-left: 4px solid {colors['accent']};">
            <div class="stat-icon">📖</div>
            <div class="stat-value">{academic_stats['total']}</div>
            <div class="stat-label">学术文献</div>
        </div>
        """)
    
    # 成长技能卡片
    with col2:
        render_html(f"""
        <div class="stat-card" style="border-left: 4px solid {colors['success']};">
            <div class="stat-icon">🌱</div>
            <div class="stat-value">{skill_stats['total']}</div>
            <div class="stat-label">成长技能 · {skill_stats['completed']}已完成</div>
        </div>
        """)
    
    # 学习资源卡片
    with col3:
        render_html(f"""
        <div class="stat-card" style="border-left: 4px solid {colors['warning']};">
            <div class="stat-icon">🔗</div>
            <div class="stat-value">{resource_stats['total']}</div>
            <div class="stat-label">学习资源 · {resource_stats['watched']}已看</div>
        </div>
        """)
    
    # 学习资料卡片
    with col4:
        total_size = materials_stats['total_size'] or 0
        if total_size > 1024 * 1024:
            size_str = f"{total_size / (1024 * 1024):.1f} MB"
        elif total_size > 1024:
            size_str = f"{total_size / 1024:.1f} KB"
        else:
            size_str = f"{total_size} B"
        
        render_html(f"""
        <div class="stat-card" style="border-left: 4px solid #a855f7;">
            <div class="stat-icon">📚</div>
            <div class="stat-value">{materials_stats['total']}</div>
            <div class="stat-label">学习资料 · {size_str}</div>
        </div>
        """)
    
    st.markdown("---")
    
    # 成长库进度概览
    st.markdown("### 🌱 成长进度")
    
    # 技能进度统计
    skill_progress_col1, skill_progress_col2 = st.columns([1, 2])
    
    with skill_progress_col1:
        # 进度圆环图 - 修复paper_bgcolor问题
        fig_progress = go.Figure()
        
        # 计算各状态数量
        completed = skill_stats['completed']
        in_progress = skill_stats['in_progress']
        not_started = skill_stats['not_started']
        total = skill_stats['total'] if skill_stats['total'] > 0 else 1
        
        fig_progress.add_trace(go.Pie(
            labels=['已完成', '进行中', '未开始'],
            values=[completed, in_progress, not_started],
            hole=0.6,
            marker=dict(colors=[colors['chart_success'], colors['chart_warning'], colors['chart_muted']]),
            textinfo='label+percent',
            textposition='outside',
            textfont=dict(color=colors['font_color'], size=12),
            hovertemplate='%{label}<br>%{percent}<extra></extra>'
        ))
        
        # 使用正确的透明背景设置
        fig_progress.update_layout(
            height=280,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5,
                font=dict(color=colors['font_color'])
            ),
            margin=dict(t=20, b=60, l=20, r=20),
            paper_bgcolor=colors['paper_bgcolor'],
            plot_bgcolor=colors['plot_bgcolor'],
            font=dict(color=colors['font_color'])
        )
        
        st.plotly_chart(fig_progress, use_container_width=True)
    
    with skill_progress_col2:
        # 按优先级显示技能
        skills_by_priority = get_skills_by_priority()
        
        for priority in ['P0', 'P1', 'P2', 'P3']:
            skills = skills_by_priority.get(priority, [])
            if skills:
                # 优先级颜色
                priority_color = {'P0': colors['danger'], 'P1': '#f97316', 'P2': colors['warning'], 'P3': colors['text_muted']}.get(priority, colors['text_muted'])
                
                st.markdown(f"**{priority} 优先级** ({len(skills)}个技能)")
                
                # 显示进度条
                for skill in skills[:3]:  # 最多显示3个
                    progress = skill['progress']
                    # 进度颜色
                    if progress < 30:
                        progress_color = colors['danger']
                    elif progress < 70:
                        progress_color = colors['warning']
                    else:
                        progress_color = colors['success']
                    
                    render_html(f"""
                    <div style="margin: 0.5rem 0; padding: 0.5rem; background: {colors['bg_secondary']}; border-radius: 8px;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 0.3rem;">
                            <span style="color: {colors['text_primary']};">{skill['skill_name']}</span>
                            <span style="color: {progress_color}; font-weight: bold;">{progress:.0f}%</span>
                        </div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: {progress}%;"></div>
                        </div>
                    </div>
                    """)
                
                if len(skills) > 3:
                    render_html(f"<span style='color: {colors['text_muted']}; font-size: 0.85rem;'>...还有{len(skills)-3}个技能</span>")
    
    st.markdown("---")
    
    # 今日推荐和最近活动
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown("### 🎯 今日推荐学习")
        
        # 获取P0优先级进度最低的技能
        recommended_skill = get_lowest_progress_skill()
        
        if recommended_skill:
            progress = recommended_skill['progress']
            
            # 颜色根据进度变化
            if progress < 30:
                color = colors['danger']
            elif progress < 70:
                color = colors['warning']
            else:
                color = colors['success']
            
            recommend_html = f"""
            <div class="content-card" style="border-left: 4px solid {color};">
                <h3 style="margin: 0 0 0.5rem 0; color: {colors['text_primary']};">🔥 {recommended_skill['skill_name']}</h3>
                <div style="display: flex; gap: 1rem; margin-bottom: 1rem;">
                    <span style="background: {colors['bg_tertiary']}; padding: 0.3rem 0.8rem; border-radius: 20px; color: {colors['text_secondary']}; font-size: 0.85rem;">
                        📁 {recommended_skill.get('category', '未分类')}
                    </span>
                    <span style="background: {colors['accent']}; padding: 0.3rem 0.8rem; border-radius: 20px; color: white; font-size: 0.85rem;">
                        {recommended_skill.get('priority', 'P2')}
                    </span>
                </div>
                <div style="margin-bottom: 0.5rem;">
                    <div class="progress-bar" style="height: 12px;">
                        <div class="progress-fill" style="width: {progress}%; background: {color};"></div>
                    </div>
                </div>
                <p style="color: {colors['text_secondary']}; margin: 0.5rem 0 0 0; text-align: center;">
                    当前进度: <strong style="color: {color};">{progress:.1f}%</strong>
                </p>
            </div>
            """
            render_html(recommend_html)
            
            # 跳转按钮
            if st.button("📖 继续学习", key="go_to_recommended_skill", type="primary"):
                st.session_state['view_item_id'] = recommended_skill['id']
                st.session_state['view_item_type'] = 'skill'
                st.session_state['current_page'] = 'growth'
                st.rerun()
        else:
            st.info("🌱 还没有技能，创建一个开始学习吧！")
    
    with col_right:
        st.markdown("### 📜 最近活动")
        
        activities = get_recent_activities(8)
        
        if activities:
            activities_html = '<div class="content-card">'
            for i, activity in enumerate(activities):
                # 根据类型选择图标
                if activity['type'] == 'study':
                    icon = "📚"
                    color = colors['accent']
                else:
                    icon = "📈"
                    color = colors['success']
                
                border_style = "border-bottom: 1px solid {0};".format(colors['card_border']) if i < len(activities) - 1 else ""
                
                activities_html += f"""
                <div style="display: flex; align-items: center; padding: 0.75rem 0; {border_style}">
                    <span style="font-size: 1.5rem; margin-right: 0.75rem; color: {color};">{icon}</span>
                    <div style="flex: 1;">
                        <p style="margin: 0; color: {colors['text_primary']}; font-weight: 500;">{activity['title']}</p>
                        <p style="margin: 0.2rem 0 0 0; color: {colors['text_muted']}; font-size: 0.85rem;">{activity['detail']}</p>
                    </div>
                </div>
                """
            activities_html += '</div>'
            render_html(activities_html)
        else:
            st.info("暂无活动记录")
    
    st.markdown("---")
    
    # 成长库详细统计
    st.markdown("### 📊 成长库详细统计")
    
    stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)
    
    with stats_col1:
        render_html(f"""
        <div class="stat-card">
            <div class="stat-icon">🎯</div>
            <div class="stat-value" style="color: {colors['accent']};">{skill_stats['total']}</div>
            <div class="stat-label">总技能数</div>
        </div>
        """)
    
    with stats_col2:
        render_html(f"""
        <div class="stat-card">
            <div class="stat-icon">🔄</div>
            <div class="stat-value" style="color: {colors['accent']};">{skill_stats['in_progress']}</div>
            <div class="stat-label">进行中</div>
        </div>
        """)
    
    with stats_col3:
        render_html(f"""
        <div class="stat-card">
            <div class="stat-icon">📈</div>
            <div class="stat-value" style="color: {colors['warning']};">{skill_stats['avg_progress']:.1f}%</div>
            <div class="stat-label">平均进度</div>
        </div>
        """)
    
    with stats_col4:
        render_html(f"""
        <div class="stat-card">
            <div class="stat-icon">🏆</div>
            <div class="stat-value" style="color: {colors['success']};">{skill_stats['completed']}</div>
            <div class="stat-label">已完成</div>
        </div>
        """)
