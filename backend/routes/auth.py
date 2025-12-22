from flask import Blueprint, request, jsonify
import jwt
from datetime import datetime, timedelta
from config import Config
from db import get_db, close_db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': '用户名和密码不能为空'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # 检查用户名是否已存在
        cursor.execute('SELECT user_id FROM users WHERE username = %s', (username,))
        if cursor.fetchone():
            return jsonify({'error': '用户名已存在'}), 400
        
        # 插入新用户
        cursor.execute(
            'INSERT INTO users (username, password) VALUES (%s, %s) RETURNING user_id',
            (username, password)  # 实际项目中应该加密密码
        )
        user_id = cursor.fetchone()[0]
        conn.commit()
        
        return jsonify({'message': '注册成功', 'user_id': user_id}), 201
    
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        close_db(conn)

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': '用户名和密码不能为空'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            'SELECT user_id, username FROM users WHERE username = %s AND password = %s',
            (username, password)
        )
        user = cursor.fetchone()
        
        if not user:
            return jsonify({'error': '用户名或密码错误'}), 401
        
        # 生成JWT token
        token = jwt.encode({
            'user_id': user[0],
            'username': user[1],
            'exp': datetime.utcnow() + timedelta(days=1)
        }, Config.SECRET_KEY, algorithm='HS256')
        
        return jsonify({
            'message': '登录成功',
            'token': token,
            'user': {
                'user_id': user[0],
                'username': user[1]
            }
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        close_db(conn)
