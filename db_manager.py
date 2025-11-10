#!/usr/bin/env python3
"""
数据库管理脚本
使用方法:
    python db_manager.py list            # 查看所有数据
    python db_manager.py books           # 查看书籍
    python db_manager.py users           # 查看用户
    python db_manager.py add-user <name> # 添加用户
    python db_manager.py add-book <title> <owner_id> <description> # 添加书籍
    python db_manager.py delete-book <id> # 删除书籍
    python db_manager.py backup          # 备份数据库
"""

import sys
import sqlite3
from datetime import datetime
import os

DATABASE_URL = "test.db"

def get_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row  # 让结果可以按列名访问
    return conn

def list_all_data():
    """查看所有数据"""
    conn = get_connection()

    print("📊 数据库完整内容")
    print("=" * 50)

    # 显示用户
    print("\n👥 用户表 (users):")
    users = conn.execute("SELECT * FROM users ORDER BY id").fetchall()
    for user in users:
        print(f"  ID: {user['id']}, 用户名: {user['username']}, 邮箱: {user['email'] or '无'}, 创建时间: {user['created_at']}")

    # 显示书籍
    print("\n📚 书籍表 (books):")
    books = conn.execute("SELECT b.*, u.username as owner_name FROM books b JOIN users u ON b.owner_id = u.id ORDER BY b.created_at DESC").fetchall()
    for book in books:
        print(f"  ID: {book['id']}, 书名: {book['title']}, 所有者: {book['owner_name']}, 创建时间: {book['created_at']}")
        print(f"    描述: {book['description'] or '无'}")
        print(f"    封面: {book['cover_url'] or '无'}")
        print()

    # 显示阅读会话
    print("\n📖 阅读会话表 (reading_sessions):")
    sessions = conn.execute("SELECT COUNT(*) as count FROM reading_sessions").fetchone()
    print(f"  总会话数: {sessions['count']}")

    conn.close()

def list_books():
    """查看书籍"""
    conn = get_connection()
    books = conn.execute("""
        SELECT b.*, u.username as owner_name
        FROM books b
        JOIN users u ON b.owner_id = u.id
        ORDER BY b.created_at DESC
    """).fetchall()

    print("📚 书籍列表")
    print("=" * 50)
    for book in books:
        print(f"📖 ID: {book['id']} | {book['title']}")
        print(f"   👤 所有者: {book['owner_name']} (ID: {book['owner_id']})")
        print(f"   📝 描述: {book['description'] or '无描述'}")
        print(f"   🖼️  封面: {book['cover_url'] or '无封面'}")
        print(f"   🕒 创建: {book['created_at']}")
        print("-" * 50)

    conn.close()

def list_users():
    """查看用户"""
    conn = get_connection()
    users = conn.execute("SELECT * FROM users ORDER BY id").fetchall()

    print("👥 用户列表")
    print("=" * 50)
    for user in users:
        # 统计用户的书籍数量
        book_count = conn.execute("SELECT COUNT(*) as count FROM books WHERE owner_id = ?", (user['id'],)).fetchone()['count']
        print(f"👤 ID: {user['id']} | {user['username']}")
        print(f"   📧 邮箱: {user['email'] or '未设置'}")
        print(f"   📚 拥有书籍: {book_count} 本")
        print(f"   🕒 创建时间: {user['created_at']}")
        print("-" * 50)

    conn.close()

def add_user(username, email=None):
    """添加用户"""
    conn = get_connection()
    try:
        # 生成简单密码哈希 (仅用于管理)
        hashed_password = "test_hash_" + username

        conn.execute("""
            INSERT INTO users (username, email, hashed_password, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
        """, (username, email, hashed_password, datetime.now(), datetime.now()))
        conn.commit()
        print(f"✅ 用户 '{username}' 添加成功")
    except sqlite3.IntegrityError as e:
        print(f"❌ 添加用户失败: {e}")
    finally:
        conn.close()

def add_book(title, owner_id, description=""):
    """添加书籍"""
    conn = get_connection()
    try:
        conn.execute("""
            INSERT INTO books (title, description, owner_id, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
        """, (title, description, int(owner_id), datetime.now(), datetime.now()))
        conn.commit()
        print(f"✅ 书籍 '{title}' 添加成功")
    except Exception as e:
        print(f"❌ 添加书籍失败: {e}")
    finally:
        conn.close()

def delete_book(book_id):
    """删除书籍"""
    conn = get_connection()
    try:
        # 先查看书籍信息
        book = conn.execute("SELECT title FROM books WHERE id = ?", (int(book_id),)).fetchone()
        if not book:
            print(f"❌ 未找到ID为 {book_id} 的书籍")
            return

        conn.execute("DELETE FROM books WHERE id = ?", (int(book_id),))
        conn.commit()
        print(f"✅ 书籍 '{book['title']}' (ID: {book_id}) 删除成功")
    except Exception as e:
        print(f"❌ 删除书籍失败: {e}")
    finally:
        conn.close()

def backup_database():
    """备份数据库"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"test_backup_{timestamp}.db"

    try:
        import shutil
        shutil.copy2(DATABASE_URL, backup_file)
        print(f"✅ 数据库已备份到: {backup_file}")
    except Exception as e:
        print(f"❌ 备份失败: {e}")

def show_help():
    """显示帮助信息"""
    print(__doc__)

def main():
    if len(sys.argv) < 2:
        show_help()
        return

    command = sys.argv[1].lower()

    if command == "list":
        list_all_data()
    elif command == "books":
        list_books()
    elif command == "users":
        list_users()
    elif command == "add-user" and len(sys.argv) >= 3:
        username = sys.argv[2]
        email = sys.argv[3] if len(sys.argv) > 3 else None
        add_user(username, email)
    elif command == "add-book" and len(sys.argv) >= 4:
        title = sys.argv[2]
        owner_id = sys.argv[3]
        description = sys.argv[4] if len(sys.argv) > 4 else ""
        add_book(title, owner_id, description)
    elif command == "delete-book" and len(sys.argv) >= 3:
        delete_book(sys.argv[2])
    elif command == "backup":
        backup_database()
    else:
        show_help()

if __name__ == "__main__":
    main()