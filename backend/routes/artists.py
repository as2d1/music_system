from flask import Blueprint, request, jsonify
import jwt
from config import Config
from db import get_db, close_db

artists_bp = Blueprint('artists', __name__)

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

@artists_bp.route('/', methods=['GET'])
def get_artists():
    """获取所有歌手"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'error': '未授权'}), 401

    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT artist_id, name FROM artists WHERE user_id = %s ORDER BY artist_id', (user_id,))
        artists = cursor.fetchall()
        
        result = [{'artist_id': row[0], 'name': row[1]} for row in artists]
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        close_db(conn)

@artists_bp.route('/<int:artist_id>', methods=['GET'])
def get_artist(artist_id):
    """获取单个歌手信息"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT artist_id, name FROM artists WHERE artist_id = %s', (artist_id,))
        artist = cursor.fetchone()
        
        if not artist:
            return jsonify({'error': '歌手不存在'}), 404
        
        return jsonify({'artist_id': artist[0], 'name': artist[1]}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        close_db(conn)

@artists_bp.route('/', methods=['POST'])
def create_artist():
    """创建新歌手"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'error': '未授权'}), 401

    data = request.get_json()
    name = data.get('name')
    
    if not name:
        return jsonify({'error': '歌手名称不能为空'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            'INSERT INTO artists (name, user_id) VALUES (%s, %s) RETURNING artist_id',
            (name, user_id)
        )
        artist_id = cursor.fetchone()[0]
        conn.commit()
        
        return jsonify({'message': '创建成功', 'artist_id': artist_id}), 201
    
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        close_db(conn)

@artists_bp.route('/<int:artist_id>', methods=['PUT'])
def update_artist(artist_id):
    """更新歌手信息"""
    data = request.get_json()
    name = data.get('name')
    
    if not name:
        return jsonify({'error': '歌手名称不能为空'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            'UPDATE artists SET name = %s WHERE artist_id = %s',
            (name, artist_id)
        )
        conn.commit()
        
        if cursor.rowcount == 0:
            return jsonify({'error': '歌手不存在'}), 404
        
        return jsonify({'message': '更新成功'}), 200
    
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        close_db(conn)

@artists_bp.route('/<int:artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
    """删除歌手"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'error': '未授权'}), 401

    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            'SELECT 1 FROM songs WHERE artist_id = %s LIMIT 1',
            (artist_id,)
        )
        if cursor.fetchone():
            return jsonify({'error': '请先删除该歌手相关的歌曲和专辑'}), 400

        cursor.execute(
            'SELECT 1 FROM albums WHERE artist_id = %s LIMIT 1',
            (artist_id,)
        )
        if cursor.fetchone():
            return jsonify({'error': '请先删除该歌手相关的歌曲和专辑'}), 400

        cursor.execute(
            'UPDATE albums SET artist_id = NULL WHERE artist_id = %s',
            (artist_id,)
        )
        cursor.execute(
            'UPDATE songs SET artist_id = NULL WHERE artist_id = %s',
            (artist_id,)
        )
        cursor.execute(
            'DELETE FROM artists WHERE artist_id = %s AND user_id = %s',
            (artist_id, user_id)
        )
        conn.commit()
        
        if cursor.rowcount == 0:
            return jsonify({'error': '歌手不存在'}), 404
        
        return jsonify({'message': '删除成功'}), 200
    
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        close_db(conn)
