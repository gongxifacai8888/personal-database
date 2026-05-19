"""
数据库核心模块
管理所有表的创建、CRUD操作和统计查询
"""

import sqlite3
import os
import hashlib
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple

# 获取数据库绝对路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "personal_database.db")


def get_connection() -> sqlite3.Connection:
    """
    获取数据库连接
    
    Returns:
        sqlite3.Connection: 数据库连接对象
    """
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_database() -> None:
    """
    初始化数据库，创建所有表
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # 学术文献表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS academic (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            authors TEXT,
            keywords TEXT,
            abstract TEXT,
            notes TEXT,
            tags TEXT,
            source TEXT,
            publish_date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 成长技能表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS growth (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            skill_name TEXT NOT NULL,
            category TEXT,
            current_level INTEGER DEFAULT 0,
            target_level INTEGER DEFAULT 100,
            progress REAL DEFAULT 0.0,
            notes TEXT,
            start_date TEXT,
            priority TEXT DEFAULT 'P2',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 资源库表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resource (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT,
            url TEXT,
            description TEXT,
            priority TEXT DEFAULT 'P2',
            status TEXT DEFAULT '待看',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 学习资料表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS learning_materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            skill_name TEXT,
            file_name TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_type TEXT,
            file_size INTEGER,
            description TEXT,
            upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_position INTEGER DEFAULT 0
        )
    """)
    
    # 添加 content_text 字段（如果不存在）
    try:
        cursor.execute("ALTER TABLE learning_materials ADD COLUMN content_text TEXT")
        conn.commit()
    except sqlite3.OperationalError:
        pass  # 字段已存在
    
    # 进度历史表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS progress_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            skill_id INTEGER NOT NULL,
            old_progress REAL,
            new_progress REAL,
            change_amount REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (skill_id) REFERENCES growth(id)
        )
    """)
    
    # 成就表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            achievement_key TEXT UNIQUE NOT NULL,
            achievement_name TEXT NOT NULL,
            achievement_desc TEXT,
            achievement_icon TEXT,
            unlocked_at TIMESTAMP,
            is_unlocked INTEGER DEFAULT 0
        )
    """)
    
    # 学习日志表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS learning_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            skill_id INTEGER NOT NULL,
            study_date TEXT,
            study_minutes INTEGER DEFAULT 0,
            xp_earned INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (skill_id) REFERENCES growth(id)
        )
    """)
    
    # 应用配置表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS app_config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            config_key TEXT UNIQUE NOT NULL,
            config_value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 技能笔记表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS skill_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            skill_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (skill_id) REFERENCES growth(id)
        )
    """)
    
    conn.commit()
    conn.close()


def hash_password(password: str) -> str:
    """
    对密码进行哈希
    
    Args:
        password: 明文密码
    
    Returns:
        str: 哈希后的密码
    """
    return hashlib.sha256(password.encode()).hexdigest()


# ============ 认证相关 ============

def get_password_hash() -> Optional[str]:
    """获取存储的密码哈希"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT config_value FROM app_config WHERE config_key = ?", ("password_hash",))
    result = cursor.fetchone()
    conn.close()
    return result["config_value"] if result else None


def set_password(password: str) -> None:
    """设置密码"""
    conn = get_connection()
    cursor = conn.cursor()
    password_hash = hash_password(password)
    cursor.execute("""
        INSERT INTO app_config (config_key, config_value, updated_at)
        VALUES (?, ?, ?)
        ON CONFLICT(config_key) DO UPDATE SET config_value = ?, updated_at = ?
    """, ("password_hash", password_hash, datetime.now(), password_hash, datetime.now()))
    conn.commit()
    conn.close()


def verify_password(password: str) -> bool:
    """验证密码"""
    stored_hash = get_password_hash()
    if not stored_hash:
        return False
    return hash_password(password) == stored_hash


def has_password() -> bool:
    """检查是否已设置密码"""
    return get_password_hash() is not None


# ============ 学术库 CRUD ============

def create_academic(title: str, authors: str = "", keywords: str = "", abstract: str = "",
                   notes: str = "", tags: str = "", source: str = "", publish_date: str = "") -> int:
    """
    创建学术文献
    
    Args:
        title: 标题
        authors: 作者
        keywords: 关键词
        abstract: 摘要
        notes: 笔记
        tags: 标签
        source: 来源
        publish_date: 发布日期
    
    Returns:
        int: 新建记录的ID
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO academic (title, authors, keywords, abstract, notes, tags, source, publish_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (title, authors, keywords, abstract, notes, tags, source, publish_date))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return new_id


def get_academic_list(search: str = "", tags: str = "") -> List[Dict]:
    """
    获取学术文献列表
    
    Args:
        search: 搜索关键词
        tags: 标签筛选
    
    Returns:
        List[Dict]: 文献列表
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM academic WHERE 1=1"
    params = []
    
    if search:
        query += " AND (title LIKE ? OR authors LIKE ? OR keywords LIKE ? OR abstract LIKE ?)"
        search_pattern = f"%{search}%"
        params.extend([search_pattern, search_pattern, search_pattern, search_pattern])
    
    if tags:
        query += " AND tags LIKE ?"
        params.append(f"%{tags}%")
    
    query += " ORDER BY created_at DESC"
    
    cursor.execute(query, params)
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results


def get_academic_by_id(academic_id: int) -> Optional[Dict]:
    """获取单个学术文献"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM academic WHERE id = ?", (academic_id,))
    result = cursor.fetchone()
    conn.close()
    return dict(result) if result else None


def update_academic(academic_id: int, **kwargs) -> None:
    """更新学术文献"""
    allowed_fields = ['title', 'authors', 'keywords', 'abstract', 'notes', 'tags', 'source', 'publish_date']
    updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
    
    if not updates:
        return
    
    conn = get_connection()
    cursor = conn.cursor()
    set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
    values = list(updates.values()) + [academic_id]
    cursor.execute(f"UPDATE academic SET {set_clause} WHERE id = ?", values)
    conn.commit()
    conn.close()


def delete_academic(academic_id: int) -> None:
    """删除学术文献"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM academic WHERE id = ?", (academic_id,))
    conn.commit()
    conn.close()


def get_academic_stats() -> Dict:
    """获取学术库统计"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM academic")
    result = cursor.fetchone()
    conn.close()
    return {"total": result["count"] if result else 0}


# ============ 成长库 CRUD ============

def create_skill(skill_name: str, category: str = "", target_level: int = 100,
                notes: str = "", priority: str = "P2") -> int:
    """
    创建技能
    
    Args:
        skill_name: 技能名称
        category: 分类
        target_level: 目标等级
        notes: 备注
        priority: 优先级
    
    Returns:
        int: 新建记录的ID
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO growth (skill_name, category, target_level, notes, priority, start_date)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (skill_name, category, target_level, notes, priority, datetime.now().strftime("%Y-%m-%d")))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return new_id


def get_skill_list(search: str = "", category: str = "", sort_by: str = "updated_at") -> List[Dict]:
    """
    获取技能列表
    
    Args:
        search: 搜索关键词
        category: 分类筛选
        sort_by: 排序字段
    
    Returns:
        List[Dict]: 技能列表
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM growth WHERE 1=1"
    params = []
    
    if search:
        query += " AND skill_name LIKE ?"
        params.append(f"%{search}%")
    
    if category:
        query += " AND category = ?"
        params.append(category)
    
    # 安全排序字段
    allowed_sorts = ["updated_at", "skill_name", "progress", "priority", "start_date"]
    if sort_by not in allowed_sorts:
        sort_by = "updated_at"
    
    query += f" ORDER BY {sort_by} DESC"
    
    cursor.execute(query, params)
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results


def get_skill_by_id(skill_id: int) -> Optional[Dict]:
    """获取单个技能"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM growth WHERE id = ?", (skill_id,))
    result = cursor.fetchone()
    conn.close()
    return dict(result) if result else None


def update_skill_progress(skill_id: int, new_progress: float) -> None:
    """
    更新技能进度
    
    Args:
        skill_id: 技能ID
        new_progress: 新进度值
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # 获取旧进度
    cursor.execute("SELECT progress FROM growth WHERE id = ?", (skill_id,))
    result = cursor.fetchone()
    old_progress = result["progress"] if result else 0
    
    # 更新技能进度
    cursor.execute("""
        UPDATE growth SET progress = ?, updated_at = ? WHERE id = ?
    """, (new_progress, datetime.now(), skill_id))
    
    # 记录历史
    cursor.execute("""
        INSERT INTO progress_history (skill_id, old_progress, new_progress, change_amount)
        VALUES (?, ?, ?, ?)
    """, (skill_id, old_progress, new_progress, new_progress - old_progress))
    
    conn.commit()
    conn.close()


def update_skill(skill_id: int, **kwargs) -> None:
    """更新技能信息"""
    allowed_fields = ['skill_name', 'category', 'target_level', 'notes', 'priority']
    updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
    
    if not updates:
        return
    
    conn = get_connection()
    cursor = conn.cursor()
    updates['updated_at'] = datetime.now()
    set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
    values = list(updates.values()) + [skill_id]
    cursor.execute(f"UPDATE growth SET {set_clause} WHERE id = ?", values)
    conn.commit()
    conn.close()


def delete_skill(skill_id: int) -> None:
    """删除技能"""
    conn = get_connection()
    cursor = conn.cursor()
    # 删除关联的笔记、历史、日志
    cursor.execute("DELETE FROM skill_notes WHERE skill_id = ?", (skill_id,))
    cursor.execute("DELETE FROM progress_history WHERE skill_id = ?", (skill_id,))
    cursor.execute("DELETE FROM learning_log WHERE skill_id = ?", (skill_id,))
    cursor.execute("DELETE FROM growth WHERE id = ?", (skill_id,))
    conn.commit()
    conn.close()


def get_skill_stats() -> Dict:
    """获取成长库统计"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) as total FROM growth")
    total = cursor.fetchone()["total"]
    
    cursor.execute("SELECT COUNT(*) as completed FROM growth WHERE progress >= 100")
    completed = cursor.fetchone()["completed"]
    
    cursor.execute("SELECT COUNT(*) as in_progress FROM growth WHERE progress > 0 AND progress < 100")
    in_progress = cursor.fetchone()["in_progress"]
    
    cursor.execute("SELECT COUNT(*) as not_started FROM growth WHERE progress = 0")
    not_started = cursor.fetchone()["not_started"]
    
    cursor.execute("SELECT AVG(progress) as avg_progress FROM growth")
    avg_result = cursor.fetchone()
    avg_progress = avg_result["avg_progress"] if avg_result and avg_result["avg_progress"] else 0
    
    conn.close()
    
    return {
        "total": total,
        "completed": completed,
        "in_progress": in_progress,
        "not_started": not_started,
        "avg_progress": round(avg_progress, 1)
    }


def get_skills_by_priority() -> Dict[str, List[Dict]]:
    """按优先级获取技能"""
    conn = get_connection()
    cursor = conn.cursor()
    
    result = {}
    for priority in ["P0", "P1", "P2", "P3"]:
        cursor.execute("""
            SELECT * FROM growth WHERE priority = ? ORDER BY progress ASC
        """, (priority,))
        result[priority] = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return result


def get_lowest_progress_skill() -> Optional[Dict]:
    """获取进度最低的P0优先级技能"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM growth WHERE priority = 'P0' ORDER BY progress ASC LIMIT 1
    """)
    result = cursor.fetchone()
    conn.close()
    return dict(result) if result else None


# ============ 资源库 CRUD ============

def create_resource(title: str, category: str = "", url: str = "",
                   description: str = "", priority: str = "P2", status: str = "待看") -> int:
    """
    创建资源
    
    Args:
        title: 标题
        category: 分类
        url: 链接
        description: 描述
        priority: 优先级
        status: 状态
    
    Returns:
        int: 新建记录的ID
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO resource (title, category, url, description, priority, status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (title, category, url, description, priority, status))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return new_id


def get_resource_list(search: str = "", category: str = "", status: str = "") -> List[Dict]:
    """
    获取资源列表
    
    Args:
        search: 搜索关键词
        category: 分类筛选
        status: 状态筛选
    
    Returns:
        List[Dict]: 资源列表
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM resource WHERE 1=1"
    params = []
    
    if search:
        query += " AND (title LIKE ? OR description LIKE ?)"
        search_pattern = f"%{search}%"
        params.extend([search_pattern, search_pattern])
    
    if category:
        query += " AND category = ?"
        params.append(category)
    
    if status:
        query += " AND status = ?"
        params.append(status)
    
    query += " ORDER BY created_at DESC"
    
    cursor.execute(query, params)
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results


def get_resource_by_id(resource_id: int) -> Optional[Dict]:
    """获取单个资源"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM resource WHERE id = ?", (resource_id,))
    result = cursor.fetchone()
    conn.close()
    return dict(result) if result else None


def update_resource(resource_id: int, **kwargs) -> None:
    """更新资源"""
    allowed_fields = ['title', 'category', 'url', 'description', 'priority', 'status']
    updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
    
    if not updates:
        return
    
    conn = get_connection()
    cursor = conn.cursor()
    set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
    values = list(updates.values()) + [resource_id]
    cursor.execute(f"UPDATE resource SET {set_clause} WHERE id = ?", values)
    conn.commit()
    conn.close()


def delete_resource(resource_id: int) -> None:
    """删除资源"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM resource WHERE id = ?", (resource_id,))
    conn.commit()
    conn.close()


def get_resource_stats() -> Dict:
    """获取资源库统计"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) as count FROM resource")
    total = cursor.fetchone()["count"]
    
    cursor.execute("SELECT COUNT(*) as count FROM resource WHERE status = '已看'")
    watched = cursor.fetchone()["count"]
    
    conn.close()
    return {"total": total, "watched": watched}


# ============ 学习资料 CRUD ============

def create_learning_material(skill_name: str, file_name: str, file_path: str,
                            file_type: str = "", file_size: int = 0,
                            description: str = "", content_text: str = "") -> int:
    """
    创建学习资料
    
    Args:
        skill_name: 关联技能名
        file_name: 文件名
        file_path: 文件路径
        file_type: 文件类型
        file_size: 文件大小(字节)
        description: 描述
        content_text: 提取的文件文本内容
    
    Returns:
        int: 新建记录的ID
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO learning_materials (skill_name, file_name, file_path, file_type, file_size, description, content_text)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (skill_name, file_name, file_path, file_type, file_size, description, content_text))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return new_id


def get_learning_materials(skill_name: str = "") -> List[Dict]:
    """
    获取学习资料列表
    
    Args:
        skill_name: 技能名筛选
    
    Returns:
        List[Dict]: 资料列表
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    if skill_name:
        cursor.execute("""
            SELECT * FROM learning_materials WHERE skill_name = ? ORDER BY upload_time DESC
        """, (skill_name,))
    else:
        cursor.execute("SELECT * FROM learning_materials ORDER BY upload_time DESC")
    
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results


def get_material_by_id(material_id: int) -> Optional[Dict]:
    """获取单个学习资料"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM learning_materials WHERE id = ?", (material_id,))
    result = cursor.fetchone()
    conn.close()
    return dict(result) if result else None


def update_material_position(material_id: int, position: int) -> None:
    """更新学习位置"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE learning_materials SET last_position = ? WHERE id = ?
    """, (position, material_id))
    conn.commit()
    conn.close()


def delete_learning_material(material_id: int) -> None:
    """删除学习资料"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM learning_materials WHERE id = ?", (material_id,))
    conn.commit()
    conn.close()


def get_materials_stats() -> Dict:
    """获取学习资料统计"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) as count FROM learning_materials")
    total = cursor.fetchone()["count"]
    
    cursor.execute("SELECT SUM(file_size) as total_size FROM learning_materials")
    size_result = cursor.fetchone()
    total_size = size_result["total_size"] if size_result and size_result["total_size"] else 0
    
    conn.close()
    return {"total": total, "total_size": total_size}


def get_material_content(material_id: int) -> Optional[str]:
    """
    获取学习资料的文本内容
    
    Args:
        material_id: 资料ID
    
    Returns:
        str: 提取的文本内容，如果不存在返回 None
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT content_text FROM learning_materials WHERE id = ?", (material_id,))
    result = cursor.fetchone()
    conn.close()
    if result and result['content_text']:
        return result['content_text']
    return None


def get_recent_material_contents(limit: int = 5) -> List[Dict]:
    """
    获取最近上传的资料及其文本内容摘要
    
    Args:
        limit: 返回数量上限
    
    Returns:
        List[Dict]: 最近资料列表，包含 id, file_name, file_type, content_text
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, file_name, file_type, content_text, upload_time 
        FROM learning_materials 
        WHERE content_text IS NOT NULL AND content_text != ''
        ORDER BY upload_time DESC 
        LIMIT ?
    """, (limit,))
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results


def update_material_content(material_id: int, content_text: str) -> None:
    """
    更新学习资料的文本内容
    
    Args:
        material_id: 资料ID
        content_text: 提取的文本内容
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE learning_materials SET content_text = ? WHERE id = ?
    """, (content_text, material_id))
    conn.commit()
    conn.close()


# ============ 技能笔记 CRUD ============

def create_skill_note(skill_id: int, content: str) -> int:
    """
    创建技能笔记
    
    Args:
        skill_id: 技能ID
        content: 笔记内容
    
    Returns:
        int: 新建记录的ID
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO skill_notes (skill_id, content) VALUES (?, ?)
    """, (skill_id, content))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return new_id


def get_skill_notes(skill_id: int) -> List[Dict]:
    """获取技能的所有笔记"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM skill_notes WHERE skill_id = ? ORDER BY created_at DESC
    """, (skill_id,))
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results


def delete_skill_note(note_id: int) -> None:
    """删除笔记"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM skill_notes WHERE id = ?", (note_id,))
    conn.commit()
    conn.close()


# ============ 进度历史 ============

def get_progress_history(skill_id: int) -> List[Dict]:
    """获取技能进度历史"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM progress_history WHERE skill_id = ? ORDER BY created_at DESC
    """, (skill_id,))
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results


# ============ 学习日志 ============

def create_learning_log(skill_id: int, study_minutes: int, xp_earned: int) -> int:
    """
    创建学习日志
    
    Args:
        skill_id: 技能ID
        study_minutes: 学习分钟数
        xp_earned: 获得经验值
    
    Returns:
        int: 新建记录的ID
    """
    conn = get_connection()
    cursor = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("""
        INSERT INTO learning_log (skill_id, study_date, study_minutes, xp_earned)
        VALUES (?, ?, ?, ?)
    """, (skill_id, today, study_minutes, xp_earned))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return new_id


def get_recent_activities(limit: int = 10) -> List[Dict]:
    """获取最近活动"""
    conn = get_connection()
    cursor = conn.cursor()
    
    activities = []
    
    # 学习日志
    cursor.execute("""
        SELECT ll.*, g.skill_name FROM learning_log ll
        JOIN growth g ON ll.skill_id = g.id
        ORDER BY ll.created_at DESC LIMIT ?
    """, (limit,))
    for row in cursor.fetchall():
        activities.append({
            "type": "study",
            "title": f"学习了 {row['skill_name']}",
            "detail": f"{row['study_minutes']}分钟, +{row['xp_earned']}XP",
            "time": row['created_at']
        })
    
    # 进度更新
    cursor.execute("""
        SELECT ph.*, g.skill_name FROM progress_history ph
        JOIN growth g ON ph.skill_id = g.id
        ORDER BY ph.created_at DESC LIMIT ?
    """, (limit,))
    for row in cursor.fetchall():
        activities.append({
            "type": "progress",
            "title": f"更新 {row['skill_name']} 进度",
            "detail": f"{row['old_progress']:.1f}% → {row['new_progress']:.1f}%",
            "time": row['created_at']
        })
    
    # 按时间排序
    activities.sort(key=lambda x: x["time"], reverse=True)
    conn.close()
    return activities[:limit]


# ============ 成就系统 ============

def init_achievements() -> None:
    """初始化成就"""
    achievements = [
        ("first_skill", "初学者", "创建第一个技能", "🎯"),
        ("first_material", "资料收集者", "上传第一个学习资料", "📚"),
        ("study_10min", "开始学习", "累计学习10分钟", "⏱️"),
        ("study_60min", "学习达人", "累计学习60分钟", "🔥"),
        ("skill_100", "技能完成", "完成一个技能学习", "🏆"),
        ("all_p0_done", "优先完成", "完成所有P0优先级技能", "⭐"),
    ]
    
    conn = get_connection()
    cursor = conn.cursor()
    
    for key, name, desc, icon in achievements:
        cursor.execute("""
            INSERT OR IGNORE INTO achievements 
            (achievement_key, achievement_name, achievement_desc, achievement_icon, is_unlocked)
            VALUES (?, ?, ?, ?, 0)
        """, (key, name, desc, icon))
    
    conn.commit()
    conn.close()


def get_achievements() -> List[Dict]:
    """获取所有成就"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM achievements ORDER BY is_unlocked DESC, id ASC")
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results


def unlock_achievement(achievement_key: str) -> bool:
    """
    解锁成就
    
    Returns:
        bool: 是否解锁成功（避免重复解锁）
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # 检查是否已解锁
    cursor.execute("SELECT is_unlocked FROM achievements WHERE achievement_key = ?", (achievement_key,))
    result = cursor.fetchone()
    
    if result and result["is_unlocked"] == 1:
        conn.close()
        return False
    
    cursor.execute("""
        UPDATE achievements SET is_unlocked = 1, unlocked_at = ? WHERE achievement_key = ?
    """, (datetime.now(), achievement_key))
    conn.commit()
    conn.close()
    return True


def check_achievements() -> List[str]:
    """检查并解锁可获得的成就"""
    unlocked = []
    
    # 初学者
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM growth")
    if cursor.fetchone()["count"] > 0:
        if unlock_achievement("first_skill"):
            unlocked.append("初学者")
    
    # 资料收集者
    cursor.execute("SELECT COUNT(*) as count FROM learning_materials")
    if cursor.fetchone()["count"] > 0:
        if unlock_achievement("first_material"):
            unlocked.append("资料收集者")
    
    # 学习达人
    cursor.execute("SELECT SUM(study_minutes) as total FROM learning_log")
    result = cursor.fetchone()
    total_minutes = result["total"] if result and result["total"] else 0
    if total_minutes >= 60:
        if unlock_achievement("study_60min"):
            unlocked.append("学习达人")
    elif total_minutes >= 10:
        if unlock_achievement("study_10min"):
            unlocked.append("开始学习")
    
    # 技能完成
    cursor.execute("SELECT COUNT(*) as count FROM growth WHERE progress >= 100")
    if cursor.fetchone()["count"] > 0:
        if unlock_achievement("skill_100"):
            unlocked.append("技能完成")
    
    # 优先完成
    cursor.execute("SELECT COUNT(*) as count FROM growth WHERE priority = 'P0' AND progress < 100")
    if cursor.fetchone()["count"] == 0:
        cursor.execute("SELECT COUNT(*) as count FROM growth WHERE priority = 'P0'")
        if cursor.fetchone()["count"] > 0:
            if unlock_achievement("all_p0_done"):
                unlocked.append("优先完成")
    
    conn.close()
    return unlocked
