"""
学术库模块
管理学术文献的CRUD操作
"""

import streamlit as st
from utils import render_html

from db import (
    get_academic_list, create_academic, get_academic_by_id,
    update_academic, delete_academic
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


def render_academic_page():
    """
    渲染学术库页面
    """
    colors = get_theme_colors()
    is_guest = st.session_state.get('guest_mode', False)
    
    # 页面标题
    render_html(f"""
    <div class="welcome-section" style="padding: 1.5rem;">
        <h1 style="margin: 0; color: {colors['text_primary']}; font-size: 1.8rem;">📖 学术库</h1>
        <p style="margin: 0.5rem 0 0 0; color: {colors['text_secondary']};">管理你的学术文献和研究资料</p>
    </div>
    """)
    
    # 搜索和筛选
    search_col1, search_col2, search_col3 = st.columns([3, 1, 1])
    
    with search_col1:
        search_query = st.text_input(
            "🔍 搜索文献",
            placeholder="输入标题、作者或关键词...",
            key="academic_search"
        )
    
    with search_col2:
        tag_filter = st.text_input("标签筛选", placeholder="标签", key="academic_tag_filter")
    
    with search_col3:
        render_html("<br>")
        if not is_guest:
            if st.button("➕ 添加文献", type="primary", use_container_width=True):
                st.session_state['show_add_academic'] = True
    
    # 添加文献表单
    if st.session_state.get('show_add_academic') and not is_guest:
        render_add_academic_form()
    
    # 文献列表
    st.markdown("---")
    st.markdown("### 📚 文献列表")
    
    academics = get_academic_list(
        search=search_query if search_query else "",
        tags=tag_filter if tag_filter else ""
    )
    
    if not academics:
        st.info("📭 暂无文献，添加一篇开始吧！")
    else:
        # 卡片式展示
        for academic in academics:
            render_academic_card(academic, is_guest)
    
    # 编辑文献模态框
    if st.session_state.get('edit_academic_id') and not is_guest:
        render_edit_academic_form(st.session_state['edit_academic_id'])


def render_academic_card(academic: dict, is_guest: bool):
    """
    渲染学术文献卡片
    
    Args:
        academic: 文献数据
        is_guest: 是否访客模式
    """
    colors = get_theme_colors()
    
    with st.container():
        card_html = f"""
        <div class="content-card" style="border-left: 4px solid {colors['accent']};">
            <h3 style="margin: 0 0 0.5rem 0; color: {colors['text_primary']};">📄 {academic['title']}</h3>
        """
        
        # 作者和日期
        meta_parts = []
        if academic.get('authors'):
            meta_parts.append(f"👥 {academic['authors']}")
        if academic.get('publish_date'):
            meta_parts.append(f"📅 {academic['publish_date']}")
        
        if meta_parts:
            card_html += f'<p style="margin: 0.5rem 0; color: {colors["text_secondary"]};">{" | ".join(meta_parts)}</p>'
        
        # 关键词
        if academic.get('keywords'):
            card_html += f'<p style="margin: 0.5rem 0; color: {colors["text_secondary"]};">🏷️ {academic["keywords"]}</p>'
        
        # 标签
        if academic.get('tags'):
            tags_html = " ".join([f'<span style="background: {colors["bg_tertiary"]}; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.8rem; color: {colors["accent"]}; margin-right: 0.3rem;">{tag.strip()}</span>' for tag in academic['tags'].split(',')])
            card_html += f'<div style="margin: 0.5rem 0;">📌 {tags_html}</div>'
        
        # 来源
        if academic.get('source'):
            card_html += f'<p style="margin: 0.5rem 0 0 0; color: {colors["text_muted"]};">📚 来源: {academic["source"]}</p>'
        
        card_html += '</div>'
        render_html(card_html)
        
        # 操作按钮
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("👁️ 查看详情", key=f"view_academic_{academic['id']}", type="primary", use_container_width=True):
                st.session_state['view_item_id'] = academic['id']
                st.session_state['view_item_type'] = 'academic'
                st.rerun()
        
        with col2:
            if st.button("✏️ 编辑", key=f"edit_btn_academic_{academic['id']}", use_container_width=True):
                st.session_state['edit_academic_id'] = academic['id']
                st.rerun()
        
        with col3:
            if not is_guest:
                if st.button("🗑️ 删除", key=f"delete_academic_{academic['id']}", use_container_width=True):
                    delete_academic(academic['id'])
                    st.success(f"已删除: {academic['title']}")
                    st.rerun()
        
        st.markdown("---")


def render_add_academic_form():
    """
    渲染添加文献表单
    """
    colors = get_theme_colors()
    
    with st.expander("➕ 添加新文献", expanded=True):
        with st.form(key="add_academic_form"):
            title = st.text_input("标题 *", key="add_academic_title")
            authors = st.text_input("作者", key="add_academic_authors")
            keywords = st.text_input("关键词 (逗号分隔)", key="add_academic_keywords")
            abstract = st.text_area("摘要", key="add_academic_abstract", height=100)
            notes = st.text_area("笔记", key="add_academic_notes", height=80)
            tags = st.text_input("标签 (逗号分隔)", key="add_academic_tags")
            source = st.text_input("来源", key="add_academic_source")
            publish_date = st.text_input("发布日期 (YYYY-MM-DD)", key="add_academic_date")
            
            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button("💾 保存", type="primary", use_container_width=True)
            with col2:
                cancelled = st.form_submit_button("❌ 取消", use_container_width=True)
            
            if submitted:
                if not title.strip():
                    st.error("标题不能为空")
                else:
                    create_academic(
                        title=title,
                        authors=authors,
                        keywords=keywords,
                        abstract=abstract,
                        notes=notes,
                        tags=tags,
                        source=source,
                        publish_date=publish_date
                    )
                    st.success("文献添加成功！")
                    st.session_state['show_add_academic'] = False
                    st.rerun()
            
            if cancelled:
                st.session_state['show_add_academic'] = False
                st.rerun()


def render_edit_academic_form(academic_id: int):
    """
    渲染编辑文献表单
    
    Args:
        academic_id: 文献ID
    """
    academic = get_academic_by_id(academic_id)
    colors = get_theme_colors()
    
    if not academic:
        st.error("文献不存在")
        st.session_state['edit_academic_id'] = None
        return
    
    with st.expander("✏️ 编辑文献", expanded=True):
        with st.form(key=f"edit_academic_form_{academic_id}"):
            title = st.text_input("标题 *", value=academic['title'], key=f"edit_title_{academic_id}")
            authors = st.text_input("作者", value=academic['authors'] or "", key=f"edit_authors_{academic_id}")
            keywords = st.text_input("关键词", value=academic['keywords'] or "", key=f"edit_keywords_{academic_id}")
            abstract = st.text_area("摘要", value=academic['abstract'] or "", 
                                    key=f"edit_abstract_{academic_id}", height=100)
            notes = st.text_area("笔记", value=academic['notes'] or "", 
                                key=f"edit_notes_{academic_id}", height=80)
            tags = st.text_input("标签", value=academic['tags'] or "", key=f"edit_tags_{academic_id}")
            source = st.text_input("来源", value=academic['source'] or "", key=f"edit_source_{academic_id}")
            publish_date = st.text_input("发布日期", value=academic['publish_date'] or "", 
                                        key=f"edit_date_{academic_id}")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                submitted = st.form_submit_button("💾 保存", type="primary", use_container_width=True)
            with col2:
                deleted = st.form_submit_button("🗑️ 删除", use_container_width=True)
            with col3:
                cancelled = st.form_submit_button("❌ 取消", use_container_width=True)
            
            if submitted:
                if not title.strip():
                    st.error("标题不能为空")
                else:
                    update_academic(academic_id,
                        title=title,
                        authors=authors,
                        keywords=keywords,
                        abstract=abstract,
                        notes=notes,
                        tags=tags,
                        source=source,
                        publish_date=publish_date
                    )
                    st.success("文献更新成功！")
                    st.session_state['edit_academic_id'] = None
                    st.rerun()
            
            if deleted:
                delete_academic(academic_id)
                st.success("文献已删除！")
                st.session_state['edit_academic_id'] = None
                st.rerun()
            
            if cancelled:
                st.session_state['edit_academic_id'] = None
                st.rerun()
