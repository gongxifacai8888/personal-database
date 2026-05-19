# -*- coding: utf-8 -*-
"""公共工具函数"""
import streamlit as st
import re


def render_html(html: str):
    """渲染HTML，自动压缩空白避免Streamlit当成代码块
    
    Streamlit的markdown渲染器会把4个以上空格开头的行当成代码块，
    所以必须去掉HTML内容中每行开头的缩进空格。
    """
    # 去掉每行开头的空白
    lines = html.strip().split('\n')
    cleaned_lines = [line.strip() for line in lines]
    cleaned = '\n'.join(cleaned_lines)
    st.markdown(cleaned, unsafe_allow_html=True)
