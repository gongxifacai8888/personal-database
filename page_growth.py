"""
成长库模块
管理技能和进度追踪
"""

import streamlit as st
from utils import render_html

from db import (
    get_skill_list, get_skill_stats, create_skill, update_skill,
    delete_skill, update_skill_progress
)


def get_theme_colors() -> dict:
    """获取当前主题颜色"""
    is_dark = st.session_state.get('theme', 'dark') == 'dark'
    if is_dark:
        return {
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
        }
    else:
        return {
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
        }


def render_growth_page():
    """
    渲染成长库页面
    """
    colors = get_theme_colors()
    is_guest = st.session_state.get('guest_mode', False)
    
    # 页面标题
    render_html(f"""
    <div class="welcome-section" style="padding: 1.5rem;">
        <h1 style="margin: 0; color: {colors['text_primary']}; font-size: 1.8rem;">🌱 成长库</h1>
        <p style="margin: 0.5rem 0 0 0; color: {colors['text_secondary']};">追踪你的技能学习和成长进度</p>
    </div>
    """)
    
    # 获取统计数据
    stats = get_skill_stats()
    
    # 顶部统计卡片
    stats_html = f"""
    <div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 1rem; margin-bottom: 1.5rem;">
        <div class="stat-card">
            <div class="stat-icon">🎯</div>
            <div class="stat-value" style="color: {colors['accent']};">{stats['total']}</div>
            <div class="stat-label">总技能</div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">🏆</div>
            <div class="stat-value" style="color: {colors['success']};">{stats['completed']}</div>
            <div class="stat-label">已完成</div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">🔄</div>
            <div class="stat-value" style="color: {colors['accent']};">{stats['in_progress']}</div>
            <div class="stat-label">进行中</div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">⏳</div>
            <div class="stat-value" style="color: {colors['text_muted']};">{stats['not_started']}</div>
            <div class="stat-label">未开始</div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">📈</div>
            <div class="stat-value" style="color: {colors['warning']};">{stats['avg_progress']:.1f}%</div>
            <div class="stat-label">平均进度</div>
        </div>
    </div>
    """
    render_html(stats_html)
    
    # 搜索和筛选
    search_col1, search_col2, search_col3 = st.columns([2, 1, 1])
    
    with search_col1:
        search_query = st.text_input(
            "🔍 搜索技能",
            placeholder="输入技能名称...",
            key="skill_search"
        )
    
    with search_col2:
        category_filter = st.selectbox(
            "分类",
            options=["全部", "编程", "AI", "语言", "创作", "艺术", "管理", "软技能", "其他"],
            key="skill_category_filter"
        )
    
    with search_col3:
        sort_by = st.selectbox(
            "排序",
            options=["最近更新", "名称", "进度", "优先级", "开始时间"],
            key="skill_sort"
        )
    
    # 映射排序选项
    sort_mapping = {
        "最近更新": "updated_at",
        "名称": "skill_name",
        "进度": "progress",
        "优先级": "priority",
        "开始时间": "start_date"
    }
    
    # 添加按钮
    if not is_guest:
        add_col = st.columns([1])
        with add_col[0]:
            if st.button("➕ 添加新技能", type="primary", use_container_width=True):
                st.session_state['show_add_skill'] = True
    
    # 添加技能表单
    if st.session_state.get('show_add_skill') and not is_guest:
        render_add_skill_form()
    
    # 技能列表
    st.markdown("---")
    st.markdown("### 📋 技能列表")
    
    category = None if category_filter == "全部" else category_filter
    
    skills = get_skill_list(
        search=search_query if search_query else "",
        category=category,
        sort_by=sort_mapping.get(sort_by, "updated_at")
    )
    
    if not skills:
        st.info("🌱 还没有技能，添加一个开始成长吧！")
    else:
        # 分组展示
        for skill in skills:
            render_skill_card(skill, is_guest)


def render_skill_card(skill: dict, is_guest: bool):
    """
    渲染技能卡片
    
    Args:
        skill: 技能数据
        is_guest: 是否访客模式
    """
    colors = get_theme_colors()
    progress = skill['progress']
    priority = skill.get('priority', 'P2')
    
    # 优先级颜色
    priority_colors = {
        'P0': colors['danger'],
        'P1': '#f97316',
        'P2': colors['warning'],
        'P3': colors['text_muted']
    }
    priority_color = priority_colors.get(priority, colors['text_muted'])
    
    # 进度颜色
    if progress < 30:
        progress_color = colors['danger']
    elif progress < 70:
        progress_color = colors['warning']
    else:
        progress_color = colors['success']
    
    with st.container():
        # 技能卡片
        card_html = f"""
        <div class="content-card" style="border-left: 4px solid {progress_color};">
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div style="flex: 1;">
                    <h3 style="margin: 0; color: {colors['text_primary']};">🌟 {skill['skill_name']}</h3>
                    <div style="display: flex; gap: 0.5rem; margin-top: 0.5rem;">
                        <span style="background: {colors['bg_tertiary']}; padding: 0.25rem 0.6rem; border-radius: 6px; 
                                    font-size: 0.8rem; color: {colors['text_secondary']};">
                            📁 {skill.get('category', '未分类')}
                        </span>
                        <span style="background: {priority_color}; padding: 0.25rem 0.6rem; border-radius: 6px; 
                                    font-size: 0.8rem; color: white;">
                            {priority}
                        </span>
                    </div>
                </div>
                <div style="text-align: right;">
                    <span style="font-size: 2rem; color: {progress_color}; font-weight: bold;">{progress:.0f}%</span>
                </div>
            </div>
            
            <div style="margin: 1rem 0;">
                <div class="progress-bar" style="height: 10px;">
                    <div class="progress-fill" style="width: {min(progress, 100)}%;"></div>
                </div>
            </div>
            
            <div style="display: flex; justify-content: space-between; color: {colors['text_muted']}; font-size: 0.85rem;">
                <span>🗓️ 开始于: {skill.get('start_date', '未知')}</span>
                <span>🔄 更新于: {skill.get('updated_at', '未知')[:10]}</span>
            </div>
        </div>
        """
        render_html(card_html)
        
        # 操作按钮
        btn_col1, btn_col2, btn_col3, btn_col4 = st.columns([1, 1, 1, 1])
        
        with btn_col1:
            if st.button("📖 继续学习", key=f"learn_{skill['id']}", type="primary", use_container_width=True):
                st.session_state['view_item_id'] = skill['id']
                st.session_state['view_item_type'] = 'skill'
                st.rerun()
        
        with btn_col2:
            if st.button("👁️ 详情", key=f"view_skill_{skill['id']}", use_container_width=True):
                st.session_state['view_item_id'] = skill['id']
                st.session_state['view_item_type'] = 'skill'
                st.rerun()
        
        if not is_guest:
            with btn_col3:
                if st.button("⚡ 快速更新", key=f"quick_update_{skill['id']}", use_container_width=True):
                    st.session_state['quick_update_skill_id'] = skill['id']
                    st.rerun()
            
            with btn_col4:
                if st.button("🗑️", key=f"delete_skill_{skill['id']}", use_container_width=True):
                    delete_skill(skill['id'])
                    st.success(f"已删除: {skill['skill_name']}")
                    st.rerun()
        
        # 快速更新进度
        if st.session_state.get('quick_update_skill_id') == skill['id'] and not is_guest:
            render_quick_update_form(skill)
        
        st.markdown("---")


def render_quick_update_form(skill: dict):
    """
    渲染快速更新进度表单
    
    Args:
        skill: 技能数据
    """
    colors = get_theme_colors()
    
    st.markdown(f"**⚡ 快速更新 {skill['skill_name']} 进度**")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # 使用唯一的key
        new_progress = st.slider(
            "拖动调整进度",
            min_value=0,
            max_value=100,
            value=int(skill['progress']),
            step=5,
            key=f"slider_{skill['id']}_quick"
        )
    
    with col2:
        render_html("<br>")
        if st.button("✓ 确认", key=f"confirm_quick_{skill['id']}", type="primary"):
            if new_progress != skill['progress']:
                update_skill_progress(skill['id'], float(new_progress))
                st.success(f"进度已更新为 {new_progress}%")
                
                # 检查是否完成
                if new_progress >= 100 and skill['progress'] < 100:
                    st.balloons()
                    st.success("🎉 恭喜完成这个技能！")
                
                # 清除快速更新状态
                if st.session_state.get('quick_update_skill_id') == skill['id']:
                    st.session_state.pop('quick_update_skill_id')
                st.rerun()
    
    if st.button("✕ 取消", key=f"cancel_quick_{skill['id']}"):
        if st.session_state.get('quick_update_skill_id') == skill['id']:
            st.session_state.pop('quick_update_skill_id')
        st.rerun()


def render_add_skill_form():
    """
    渲染添加技能表单
    """
    colors = get_theme_colors()
    
    with st.expander("➕ 添加新技能", expanded=True):
        with st.form(key="add_skill_form"):
            skill_name = st.text_input("技能名称 *", key="add_skill_name")
            
            col1, col2 = st.columns(2)
            with col1:
                category = st.selectbox(
                    "分类",
                    options=["编程", "AI", "语言", "创作", "艺术", "管理", "软技能", "其他"],
                    key="add_skill_category"
                )
            with col2:
                priority = st.selectbox(
                    "优先级",
                    options=["P0", "P1", "P2", "P3"],
                    index=2,
                    key="add_skill_priority"
                )
            
            target_level = st.number_input("目标等级", min_value=10, max_value=1000, value=100, key="add_skill_target")
            notes = st.text_area("备注", key="add_skill_notes", height=80)
            
            col_save, col_cancel = st.columns(2)
            with col_save:
                submitted = st.form_submit_button("💾 保存", type="primary", use_container_width=True)
            with col_cancel:
                cancelled = st.form_submit_button("❌ 取消", use_container_width=True)
            
            if submitted:
                if not skill_name.strip():
                    st.error("技能名称不能为空")
                else:
                    create_skill(
                        skill_name=skill_name,
                        category=category,
                        target_level=target_level,
                        notes=notes,
                        priority=priority
                    )
                    st.success(f"技能 '{skill_name}' 添加成功！")
                    st.session_state['show_add_skill'] = False
                    st.rerun()
            
            if cancelled:
                st.session_state['show_add_skill'] = False
                st.rerun()
