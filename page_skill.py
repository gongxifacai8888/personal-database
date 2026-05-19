"""
技能详情页模块
显示单个技能的详细信息，包含进度更新、笔记、番茄钟和学习资料
这是用户核心体验页面
"""

import streamlit as st
from utils import render_html
import time
import os
from datetime import datetime
from db import (
    get_skill_by_id, update_skill_progress, get_skill_notes, create_skill_note,
    delete_skill_note, get_progress_history, create_learning_log,
    get_learning_materials, update_material_position, delete_learning_material,
    check_achievements
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


def render_skill_detail_page(skill_id: int):
    """
    渲染技能详情页
    
    Args:
        skill_id: 技能ID
    """
    skill = get_skill_by_id(skill_id)
    colors = get_theme_colors()
    
    if not skill:
        st.error("技能不存在")
        if st.button("返回"):
            st.session_state['view_item_id'] = None
            st.session_state['view_item_type'] = None
            st.rerun()
        return
    
    is_guest = st.session_state.get('guest_mode', False)
    
    # 初始化番茄钟状态
    if 'pomodoro_running' not in st.session_state:
        st.session_state['pomodoro_running'] = False
    if 'pomodoro_time' not in st.session_state:
        st.session_state['pomodoro_time'] = 25 * 60
    if 'pomodoro_start_time' not in st.session_state:
        st.session_state['pomodoro_start_time'] = None
    
    # 返回按钮
    back_col, _ = st.columns([1, 4])
    with back_col:
        if st.button("← 返回成长库", key=f"back_to_growth_{skill_id}"):
            st.session_state['view_item_id'] = None
            st.session_state['view_item_type'] = None
            st.rerun()
    
    st.markdown("---")
    
    # 技能头部信息
    render_skill_header(skill)
    
    st.markdown("---")
    
    # 创建标签页
    tab1, tab2, tab3, tab4 = st.tabs(["📈 进度", "📝 笔记", "🍅 番茄钟", "📚 学习资料"])
    
    with tab1:
        render_progress_section(skill, is_guest)
    
    with tab2:
        render_notes_section(skill_id, is_guest)
    
    with tab3:
        render_pomodoro_section(skill_id, skill, is_guest)
    
    with tab4:
        render_materials_section(skill_id, skill['skill_name'], is_guest)


def render_skill_header(skill: dict):
    """
    渲染技能头部信息
    
    Args:
        skill: 技能数据
    """
    colors = get_theme_colors()
    progress = skill.get('progress', 0)
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
    
    # 大进度条
    header_html = f"""
    <div class="content-card" style="text-align: center; padding: 2rem;">
        <h1 style="color: {colors['text_primary']}; margin: 0; font-size: 2rem;">🌟 {skill['skill_name']}</h1>
        <div style="display: flex; justify-content: center; gap: 1rem; margin-top: 1rem;">
            <span style="background: {colors['bg_tertiary']}; padding: 0.4rem 1rem; border-radius: 20px; 
                        font-size: 0.9rem; color: {colors['text_secondary']};">
                📁 {skill.get('category', '未分类')}
            </span>
            <span style="background: {priority_color}; padding: 0.4rem 1rem; border-radius: 20px; 
                        font-size: 0.9rem; color: white;">
                {priority}
            </span>
        </div>
        <div style="margin-top: 2rem;">
            <span style="font-size: 4rem; color: {progress_color}; font-weight: bold;">{progress:.0f}%</span>
        </div>
        <div style="margin: 1.5rem 2rem;">
            <div class="progress-bar" style="height: 16px;">
                <div class="progress-fill" style="width: {min(progress, 100)}%;"></div>
            </div>
        </div>
        <p style="color: {colors['text_muted']}; margin: 0;">
            🗓️ 开始于 {skill.get('start_date', '未知')} · 
            🔄 更新于 {skill.get('updated_at', '')[:10] if skill.get('updated_at') else '未知'}
        </p>
    </div>
    """
    render_html(header_html)


def render_progress_section(skill: dict, is_guest: bool):
    """
    渲染进度区域
    
    Args:
        skill: 技能数据
        is_guest: 是否访客模式
    """
    colors = get_theme_colors()
    skill_id = skill['id']
    
    st.markdown("### 📈 更新进度")
    
    # 进度滑块 - 使用唯一的key
    col1, col2 = st.columns([3, 1])
    
    with col1:
        new_progress = st.slider(
            "拖动调整进度",
            min_value=0,
            max_value=100,
            value=int(skill['progress']),
            step=5,
            key=f"progress_slider_{skill_id}"
        )
    
    with col2:
        render_html("<br>")
        if st.button("✓ 更新", key=f"update_progress_btn_{skill_id}", type="primary", use_container_width=True):
            if new_progress != skill['progress']:
                update_skill_progress(skill_id, float(new_progress))
                st.success(f"进度已更新为 {new_progress}%")
                
                # 检查是否完成
                if new_progress >= 100 and skill['progress'] < 100:
                    st.balloons()
                    st.success("🎉 恭喜完成这个技能！")
                    # 检查成就
                    new_achievements = check_achievements()
                    for achievement in new_achievements:
                        st.toast(f"🏆 成就解锁: {achievement}")
                
                st.rerun()
            else:
                st.info("进度没有变化")
    
    # 进度历史
    st.markdown("---")
    st.markdown("### 📜 进度历史")
    
    history = get_progress_history(skill_id)
    
    if history:
        history_html = '<div class="content-card">'
        for h in history[:10]:
            change = h['new_progress'] - h['old_progress']
            change_str = f"+{change:.1f}" if change >= 0 else f"{change:.1f}"
            change_color = colors['success'] if change >= 0 else colors['danger']
            
            history_html += f"""
            <div style="display: flex; justify-content: space-between; padding: 0.75rem; 
                        background: {colors['bg_tertiary']}; border-radius: 8px; margin: 0.5rem 0;">
                <span style="color: {colors['text_muted']};">{h['created_at'][:19]}</span>
                <span style="color: {colors['text_primary']};">{h['old_progress']:.1f}% → {h['new_progress']:.1f}%</span>
                <span style="color: {change_color}; font-weight: bold;">{change_str}%</span>
            </div>
            """
        history_html += '</div>'
        render_html(history_html)
    else:
        st.info("暂无进度记录")


def render_notes_section(skill_id: int, is_guest: bool):
    """
    渲染笔记区域
    
    Args:
        skill_id: 技能ID
        is_guest: 是否访客模式
    """
    colors = get_theme_colors()
    st.markdown("### 📝 学习笔记")
    
    # 添加笔记
    if not is_guest:
        with st.expander("➕ 添加新笔记", expanded=False):
            new_note = st.text_area(
                "写下你的学习心得...",
                height=100,
                key=f"new_note_input_{skill_id}"
            )
            
            if st.button("💾 保存笔记", key=f"save_note_btn_{skill_id}", type="primary", use_container_width=True):
                if new_note.strip():
                    create_skill_note(skill_id, new_note.strip())
                    st.success("笔记已保存！")
                    st.rerun()
                else:
                    st.error("笔记内容不能为空")
    
    # 笔记列表
    st.markdown("---")
    st.markdown("**历史笔记**")
    
    notes = get_skill_notes(skill_id)
    
    if notes:
        notes_html = '<div>'
        for note in notes:
            notes_html += f"""
            <div class="content-card" style="border-left: 4px solid {colors['accent']};">
                <p style="color: {colors['text_primary']}; margin: 0;">{note['content']}</p>
                <p style="color: {colors['text_muted']}; font-size: 0.8rem; margin-top: 0.75rem;">
                    🕐 {note['created_at'][:19]}
                </p>
            </div>
            """
            if not is_guest:
                if st.button("🗑️ 删除笔记", key=f"delete_note_{note['id']}", use_container_width=True):
                    delete_skill_note(note['id'])
                    st.rerun()
        notes_html += '</div>'
        render_html(notes_html)
    else:
        st.info("还没有笔记，开始记录你的学习心得吧！")


def render_pomodoro_section(skill_id: int, skill: dict, is_guest: bool):
    """
    渲染番茄钟区域
    
    Args:
        skill_id: 技能ID
        skill: 技能数据
        is_guest: 是否访客模式
    """
    colors = get_theme_colors()
    st.markdown("### 🍅 番茄钟学习")
    
    # 状态显示
    pomodoro_time = st.session_state.get('pomodoro_time', 25 * 60)
    is_running = st.session_state.get('pomodoro_running', False)
    
    # 计时器显示
    minutes = pomodoro_time // 60
    seconds = pomodoro_time % 60
    
    # 进度百分比
    total_seconds = 25 * 60
    progress_percent = ((total_seconds - pomodoro_time) / total_seconds) * 100
    
    timer_html = f"""
    <div class="content-card" style="text-align: center; padding: 2rem;">
        <div style="font-size: 4.5rem; font-weight: bold; color: {colors['text_primary']}; 
                    font-family: 'Courier New', monospace;">
            {minutes:02d}:{seconds:02d}
        </div>
        <div class="progress-bar" style="margin: 1.5rem 2rem; height: 12px;">
            <div class="progress-fill" style="width: {progress_percent}%; background: {colors['danger']};"></div>
        </div>
    </div>
    """
    render_html(timer_html)
    
    # 控制按钮
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if not is_running:
            if st.button("▶️ 开始", key=f"start_pomodoro_{skill_id}", type="primary", use_container_width=True):
                st.session_state['pomodoro_running'] = True
                st.session_state['pomodoro_start_time'] = time.time()
                st.rerun()
        else:
            if st.button("⏸️ 暂停", key=f"pause_pomodoro_{skill_id}", type="secondary", use_container_width=True):
                st.session_state['pomodoro_running'] = False
                # 计算暂停时经过的时间
                if st.session_state.get('pomodoro_start_time'):
                    elapsed = time.time() - st.session_state['pomodoro_start_time']
                    st.session_state['pomodoro_time'] = max(0, int(25 * 60 - elapsed))
                st.rerun()
    
    with col2:
        if st.button("🔄 重置", key=f"reset_pomodoro_{skill_id}", use_container_width=True):
            st.session_state['pomodoro_time'] = 25 * 60
            st.session_state['pomodoro_running'] = False
            st.session_state['pomodoro_start_time'] = None
            st.rerun()
    
    with col3:
        time_options = [25, 15, 5]
        selected_time = st.selectbox(
            "时长(分钟)",
            options=time_options,
            index=0,
            key=f"time_select_{skill_id}"
        )
        if st.button("⏱️ 设置", key=f"set_time_{skill_id}", use_container_width=True):
            st.session_state['pomodoro_time'] = selected_time * 60
            st.session_state['pomodoro_running'] = False
            st.rerun()
    
    # 实时更新计时器
    if is_running:
        if st.session_state.get('pomodoro_start_time'):
            elapsed = time.time() - st.session_state['pomodoro_start_time']
            remaining = max(0, int(25 * 60 - elapsed))
            
            if remaining <= 0:
                # 计时完成
                st.session_state['pomodoro_running'] = False
                st.session_state['pomodoro_time'] = 0
                st.balloons()
                st.success("🎉 番茄钟完成！休息一下吧！")
                
                # 记录学习日志
                if not is_guest:
                    create_learning_log(skill_id, 25, 30)
                    update_skill_progress(skill_id, min(100, skill['progress'] + 2))
                    st.success("已记录25分钟学习时间，+30 XP，进度+2%")
                    check_achievements()
                
                st.rerun()
            else:
                st.session_state['pomodoro_time'] = remaining
        
        time.sleep(1)
        st.rerun()
    
    # 学习统计
    st.markdown("---")
    st.markdown("### 📊 学习统计")
    
    stats_html = f"""
    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem;">
        <div class="stat-card">
            <div class="stat-label">技能名称</div>
            <div class="stat-value" style="font-size: 1.2rem;">{skill['skill_name']}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">当前进度</div>
            <div class="stat-value" style="font-size: 1.2rem;">{skill['progress']:.1f}%</div>
        </div>
    </div>
    """
    render_html(stats_html)
    
    if not is_guest:
        st.markdown("---")
        st.success("💡 提示: 每完成一个25分钟番茄钟，获得30 XP和2%进度提升！")


def render_materials_section(skill_id: int, skill_name: str, is_guest: bool):
    """
    渲染学习资料区域
    
    Args:
        skill_id: 技能ID
        skill_name: 技能名称
        is_guest: 是否访客模式
    """
    colors = get_theme_colors()
    st.markdown("### 📚 学习资料")
    
    # 获取该技能关联的资料
    materials = get_learning_materials(skill_name=skill_name)
    
    if materials:
        st.markdown(f"**关联 {len(materials)} 个资料**")
        
        for material in materials:
            file_type = material.get('file_type', '').lower()
            
            # 文件类型图标
            file_icons = {
                'pdf': '📄',
                'doc': '📝', 'docx': '📝',
                'txt': '📃', 'md': '📃',
                'xlsx': '📊', 'xls': '📊',
                'pptx': '📽️', 'ppt': '📽️',
                'default': '📁'
            }
            icon = file_icons.get(file_type, file_icons['default'])
            
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.markdown(f"{icon} **{material['file_name']}**")
                    if material.get('last_position', 0) > 0:
                        st.markdown(f"📍 上次位置: 第 {material['last_position']} 页/行")
                
                with col2:
                    # 打开/下载按钮
                    file_path = material.get('file_path')
                    if file_path and os.path.exists(file_path):
                        try:
                            with open(file_path, 'rb') as f:
                                st.download_button(
                                    "📥 下载",
                                    data=f,
                                    file_name=material['file_name'],
                                    key=f"download_skill_material_{material['id']}"
                                )
                        except Exception as e:
                            st.error("无法打开")
                    else:
                        st.error("文件不存在")
                
                with col3:
                    if not is_guest:
                        if st.button("🗑️", key=f"delete_skill_material_{material['id']}"):
                            # 删除文件
                            if file_path and os.path.exists(file_path):
                                try:
                                    os.remove(file_path)
                                except:
                                    pass
                            delete_learning_material(material['id'])
                            st.rerun()
                
                st.markdown("---")
    else:
        st.info(f"还没有关联的学习资料")
    
    # 跳转到学习资料页面添加
    if st.button("📚 前往学习资料页面添加", key=f"go_to_materials_{skill_id}"):
        st.session_state['current_page'] = 'materials'
        st.session_state['view_item_id'] = None
        st.session_state['view_item_type'] = None
        st.rerun()
