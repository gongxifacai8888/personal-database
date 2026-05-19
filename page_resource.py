"""
资源库模块
管理学习资源的链接和状态
"""

import streamlit as st
from utils import render_html

from db import (
    get_resource_list, create_resource, get_resource_by_id,
    update_resource, delete_resource, get_resource_stats
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
            'purple': '#a855f7',
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
            'purple': '#9333ea',
            'card_border': '#cbd5e1',
        }


def render_resource_page():
    """
    渲染资源库页面
    """
    colors = get_theme_colors()
    is_guest = st.session_state.get('guest_mode', False)
    
    # 编辑模式处理
    if st.session_state.get('edit_resource_mode') and st.session_state.get('edit_resource_id'):
        render_edit_resource_form(st.session_state['edit_resource_id'])
        st.session_state['edit_resource_mode'] = False
        st.session_state['edit_resource_id'] = None
        return
    
    # 页面标题
    render_html(f"""
    <div class="welcome-section" style="padding: 1.5rem;">
        <h1 style="margin: 0; color: {colors['text_primary']}; font-size: 1.8rem;">🔗 资源库</h1>
        <p style="margin: 0.5rem 0 0 0; color: {colors['text_secondary']};">管理你的学习资源和链接收藏</p>
    </div>
    """)
    
    # 统计信息
    stats = get_resource_stats()
    stats_html = f"""
    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; margin-bottom: 1.5rem;">
        <div class="stat-card">
            <div class="stat-icon">📦</div>
            <div class="stat-value" style="color: {colors['accent']};">{stats['total']}</div>
            <div class="stat-label">总资源数</div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">✅</div>
            <div class="stat-value" style="color: {colors['success']};">{stats['watched']}</div>
            <div class="stat-label">已看完</div>
        </div>
    </div>
    """
    render_html(stats_html)
    
    # 搜索和筛选
    search_col1, search_col2, search_col3 = st.columns([2, 1, 1])
    
    with search_col1:
        search_query = st.text_input(
            "🔍 搜索资源",
            placeholder="输入标题或描述...",
            key="resource_search"
        )
    
    with search_col2:
        category_filter = st.selectbox(
            "分类",
            options=["全部", "编程", "AI", "工具", "阅读", "视频", "文档", "其他"],
            key="resource_category_filter"
        )
    
    with search_col3:
        status_filter = st.selectbox(
            "状态",
            options=["全部", "待看", "在看", "已看", "收藏"],
            key="resource_status_filter"
        )
    
    # 添加按钮
    if not is_guest:
        add_col = st.columns([1])
        with add_col[0]:
            if st.button("➕ 添加资源", type="primary", use_container_width=True):
                st.session_state['show_add_resource'] = True
    
    # 添加资源表单
    if st.session_state.get('show_add_resource') and not is_guest:
        render_add_resource_form()
    
    # 资源列表
    st.markdown("---")
    st.markdown("### 📋 资源列表")
    
    category = None if category_filter == "全部" else category_filter
    status = None if status_filter == "全部" else status_filter
    
    resources = get_resource_list(
        search=search_query if search_query else "",
        category=category,
        status=status
    )
    
    if not resources:
        st.info("📭 还没有资源，添加一个开始吧！")
    else:
        for resource in resources:
            render_resource_card(resource, is_guest)


def render_resource_card(resource: dict, is_guest: bool):
    """
    渲染资源卡片
    
    Args:
        resource: 资源数据
        is_guest: 是否访客模式
    """
    colors = get_theme_colors()
    priority = resource.get('priority', 'P2')
    
    # 优先级颜色
    priority_colors = {
        'P0': colors['danger'],
        'P1': '#f97316',
        'P2': colors['warning'],
        'P3': colors['text_muted']
    }
    priority_color = priority_colors.get(priority, colors['text_muted'])
    
    # 状态颜色
    status_colors = {
        '待看': colors['text_muted'],
        '在看': colors['accent'],
        '已看': colors['success'],
        '收藏': colors['purple']
    }
    status_color = status_colors.get(resource.get('status', '待看'), colors['text_muted'])
    
    with st.container():
        card_html = f"""
        <div class="content-card">
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div style="flex: 1;">
                    <h3 style="margin: 0; color: {colors['text_primary']};">🔗 {resource['title']}</h3>
                    <div style="display: flex; gap: 0.5rem; margin-top: 0.5rem; flex-wrap: wrap;">
                        <span style="background: {colors['bg_tertiary']}; padding: 0.25rem 0.6rem; border-radius: 6px; 
                                    font-size: 0.8rem; color: {colors['text_secondary']};">
                            📁 {resource.get('category', '未分类')}
                        </span>
                        <span style="background: {priority_color}; padding: 0.25rem 0.6rem; border-radius: 6px; 
                                    font-size: 0.8rem; color: white;">
                            {priority}
                        </span>
                        <span style="background: {status_color}; padding: 0.25rem 0.6rem; border-radius: 6px; 
                                    font-size: 0.8rem; color: white;">
                            {resource.get('status', '待看')}
                        </span>
                    </div>
        """
        
        if resource.get('description'):
            card_html += f"""
                    <p style="color: {colors['text_secondary']}; margin: 0.75rem 0 0 0; font-size: 0.9rem;">
                        💬 {resource['description'][:120]}{'...' if len(resource.get('description', '')) > 120 else ''}
                    </p>
            """
        
        if resource.get('url'):
            card_html += f"""
                    <a href="{resource['url']}" target="_blank" style="color: {colors['accent']}; font-size: 0.85rem; 
                       display: inline-flex; align-items: center; gap: 0.3rem; margin-top: 0.5rem;">
                        🔗 {resource['url'][:60]}{'...' if len(resource.get('url', '')) > 60 else ''}
                    </a>
            """
        
        card_html += """
                </div>
            </div>
        </div>
        """
        render_html(card_html)
        
        # 操作按钮
        btn_col1, btn_col2, btn_col3, btn_col4 = st.columns([1, 1, 1, 1])
        
        with btn_col1:
            if resource.get('url') and st.button("🌐 访问", key=f"visit_{resource['id']}", type="primary", use_container_width=True):
                st.markdown(f"[打开链接]({resource['url']})")
        
        with btn_col2:
            if st.button("👁️ 详情", key=f"view_resource_{resource['id']}", use_container_width=True):
                st.session_state['view_item_id'] = resource['id']
                st.session_state['view_item_type'] = 'resource'
                st.rerun()
        
        if not is_guest:
            with btn_col3:
                # 快速状态切换
                statuses = ['待看', '在看', '已看', '收藏']
                current_status = resource.get('status', '待看')
                
                # 找到下一个状态
                current_idx = statuses.index(current_status) if current_status in statuses else 0
                next_status = statuses[(current_idx + 1) % len(statuses)]
                
                status_next_colors = {
                    '待看': colors['text_muted'],
                    '在看': colors['accent'],
                    '已看': colors['success'],
                    '收藏': colors['purple']
                }
                
                if st.button(f"📊 {next_status}", key=f"status_{resource['id']}", use_container_width=True):
                    update_resource(resource['id'], status=next_status)
                    st.rerun()
            
            with btn_col4:
                if st.button("✏️", key=f"edit_resource_{resource['id']}", use_container_width=True):
                    st.session_state['edit_resource_id'] = resource['id']
                    st.session_state['edit_resource_mode'] = True
                    st.rerun()
        
        st.markdown("---")


def render_add_resource_form():
    """
    渲染添加资源表单
    """
    colors = get_theme_colors()
    
    with st.expander("➕ 添加新资源", expanded=True):
        with st.form(key="add_resource_form"):
            title = st.text_input("标题 *", key="add_resource_title")
            url = st.text_input("链接 URL", key="add_resource_url")
            
            col1, col2 = st.columns(2)
            with col1:
                category = st.selectbox(
                    "分类",
                    options=["编程", "AI", "工具", "阅读", "视频", "文档", "其他"],
                    key="add_resource_category"
                )
            with col2:
                priority = st.selectbox(
                    "优先级",
                    options=["P0", "P1", "P2", "P3"],
                    index=2,
                    key="add_resource_priority"
                )
            
            status = st.selectbox(
                "状态",
                options=["待看", "在看", "已看", "收藏"],
                index=0,
                key="add_resource_status"
            )
            
            description = st.text_area("描述", key="add_resource_desc", height=80)
            
            col_save, col_cancel = st.columns(2)
            with col_save:
                submitted = st.form_submit_button("💾 保存", type="primary", use_container_width=True)
            with col_cancel:
                cancelled = st.form_submit_button("❌ 取消", use_container_width=True)
            
            if submitted:
                if not title.strip():
                    st.error("标题不能为空")
                else:
                    create_resource(
                        title=title,
                        url=url,
                        category=category,
                        priority=priority,
                        status=status,
                        description=description
                    )
                    st.success(f"资源 '{title}' 添加成功！")
                    st.session_state['show_add_resource'] = False
                    st.rerun()
            
            if cancelled:
                st.session_state['show_add_resource'] = False
                st.rerun()


def render_edit_resource_form(resource_id: int):
    """
    渲染编辑资源表单
    
    Args:
        resource_id: 资源ID
    """
    resource = get_resource_by_id(resource_id)
    colors = get_theme_colors()
    
    if not resource:
        st.error("资源不存在")
        return
    
    st.markdown("---")
    st.markdown("### ✏️ 编辑资源")
    
    with st.form(key=f"edit_resource_form_{resource_id}"):
        title = st.text_input("标题 *", value=resource['title'], key=f"edit_title_{resource_id}")
        url = st.text_input("链接 URL", value=resource.get('url', ''), key=f"edit_url_{resource_id}")
        
        col1, col2 = st.columns(2)
        with col1:
            category = st.selectbox(
                "分类",
                options=["编程", "AI", "工具", "阅读", "视频", "文档", "其他"],
                index=["编程", "AI", "工具", "阅读", "视频", "文档", "其他"].index(resource.get('category', '其他')) 
                      if resource.get('category', '其他') in ["编程", "AI", "工具", "阅读", "视频", "文档", "其他"] else 6,
                key=f"edit_category_{resource_id}"
            )
        with col2:
            priority = st.selectbox(
                "优先级",
                options=["P0", "P1", "P2", "P3"],
                index=["P0", "P1", "P2", "P3"].index(resource.get('priority', 'P2')) 
                      if resource.get('priority', 'P2') in ["P0", "P1", "P2", "P3"] else 2,
                key=f"edit_priority_{resource_id}"
            )
        
        status = st.selectbox(
            "状态",
            options=["待看", "在看", "已看", "收藏"],
            index=["待看", "在看", "已看", "收藏"].index(resource.get('status', '待看'))
                   if resource.get('status', '待看') in ["待看", "在看", "已看", "收藏"] else 0,
            key=f"edit_status_{resource_id}"
        )
        
        description = st.text_area("描述", value=resource.get('description', ''), 
                                  key=f"edit_desc_{resource_id}", height=80)
        
        col_save, col_del, col_cancel = st.columns(3)
        with col_save:
            submitted = st.form_submit_button("💾 保存", type="primary", use_container_width=True)
        with col_del:
            deleted = st.form_submit_button("🗑️ 删除", use_container_width=True)
        with col_cancel:
            cancelled = st.form_submit_button("❌ 取消", use_container_width=True)
        
        if submitted:
            if not title.strip():
                st.error("标题不能为空")
            else:
                update_resource(resource_id,
                    title=title, url=url, category=category,
                    priority=priority, status=status, description=description
                )
                st.success("资源更新成功！")
                st.session_state['edit_resource_mode'] = False
                st.session_state['edit_resource_id'] = None
                st.rerun()
        
        if deleted:
            delete_resource(resource_id)
            st.success("资源已删除！")
            st.session_state['edit_resource_mode'] = False
            st.session_state['edit_resource_id'] = None
            st.rerun()
        
        if cancelled:
            st.session_state['edit_resource_mode'] = False
            st.session_state['edit_resource_id'] = None
            st.rerun()
