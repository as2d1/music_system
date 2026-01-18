from flask import Blueprint, request, jsonify
import jwt
from config import Config
from db import get_db, close_db

albums_bp = Blueprint('albums', __name__)

def get_current_user_id():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None
    try:
        token = auth_header.split(" ")[1]
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
        return payload.get('user_id')
    except:
        return None

@albums_bp.route('/', methods=['GET'])
def get_albums():
    """获取所有专辑"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'error': '未授权'}), 401

    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT a.album_id, a.title, a.artist_id, ar.name as artist_name
            FROM albums a
            LEFT JOIN artists ar ON a.artist_id = ar.artist_id
            WHERE a.user_id = %s
            ORDER BY a.album_id
        ''', (user_id,))
        albums = cursor.fetchall()
        
        result = [{
            'album_id': row[0],
            'title': row[1],
            'artist_id': row[2],
            'artist_name': row[3]
        } for row in albums]
        
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        close_db(conn)

@albums_bp.route('/<int:album_id>', methods=['GET'])
def get_album(album_id):
    """获取单个专辑信息"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT a.album_id, a.title, a.artist_id, ar.name as artist_name
            FROM albums a
            LEFT JOIN artists ar ON a.artist_id = ar.artist_id
            WHERE a.album_id = %s
        ''', (album_id,))
        album = cursor.fetchone()
        
        if not album:
            return jsonify({'error': '专辑不存在'}), 404
        
        return jsonify({
            'album_id': album[0],
            'title': album[1],
            'artist_id': album[2],
            'artist_name': album[3]
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        close_db(conn)

@albums_bp.route('/', methods=['POST'])
def create_album():
    """创建新专辑"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'error': '未授权'}), 401

    data = request.get_json()
    title = data.get('title')
    artist_id = data.get('artist_id')
    
    if not title:
        return jsonify({'error': '专辑名称不能为空'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            'INSERT INTO albums (title, artist_id, user_id) VALUES (%s, %s, %s) RETURNING album_id',
            (title, artist_id, user_id)
        )
        album_id = cursor.fetchone()[0]
        conn.commit()
        
        return jsonify({'message': '创建成功', 'album_id': album_id}), 201
    
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        close_db(conn)

@albums_bp.route('/<int:album_id>', methods=['PUT'])
def update_album(album_id):
    """更新专辑信息"""
    data = request.get_json()
    title = data.get('title')
    artist_id = data.get('artist_id')
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            'UPDATE albums SET title = %s, artist_id = %s WHERE album_id = %s',
            (title, artist_id, album_id)
        )
        conn.commit()
        
        if cursor.rowcount == 0:
            return jsonify({'error': '专辑不存在'}), 404
        
        return jsonify({'message': '更新成功'}), 200
    
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        close_db(conn)

@albums_bp.route('/<int:album_id>', methods=['DELETE'])
def delete_album(album_id):
    """删除专辑"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'error': '未授权'}), 401

    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            'UPDATE songs SET album_id = NULL WHERE album_id = %s AND user_id = %s',
            (album_id, user_id)
        )
        cursor.execute(
            'DELETE FROM albums WHERE album_id = %s AND user_id = %s',
            (album_id, user_id)
        )
        conn.commit()
        
        if cursor.rowcount == 0:
            return jsonify({'error': '专辑不存在'}), 404
        
        return jsonify({'message': '删除成功'}), 200
    
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        close_db(conn)
