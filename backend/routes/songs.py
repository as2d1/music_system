from flask import Blueprint, request, jsonify, send_file
import io
import psycopg2
import jwt
from datetime import datetime
from config import Config
from db import get_db, close_db

songs_bp = Blueprint('songs', __name__)

def get_current_user_id():
    auth_header = request.headers.get('Authorization')
    try:
        token = None
        if auth_header:
            token = auth_header.split(" ")[1]
        if not token:
            token = request.args.get('token')
        if not token:
            return None
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
        return payload.get('user_id')
    except:
        return None

def _to_int_or_none(v):
    if v is None or v == '':
        return None
    try:
        return int(v)
    except (TypeError, ValueError):
        return None

@songs_bp.route('/', methods=['GET'])
def get_songs():
    """获取所有歌曲"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'error': '未授权'}), 401

    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT s.song_id, s.title, s.duration,
                   s.artist_id, ar.name as artist_name,
                   s.album_id, al.title as album_title,
                   CASE WHEN s.file_data IS NOT NULL THEN 1 ELSE 0 END as has_file
            FROM songs s
            LEFT JOIN artists ar ON s.artist_id = ar.artist_id
            LEFT JOIN albums al ON s.album_id = al.album_id
            WHERE s.user_id = %s
            ORDER BY s.song_id
        ''', (user_id,))
        songs = cursor.fetchall()
        
        base_url = request.host_url.rstrip('/')
        result = [{
            'song_id': row[0],
            'title': row[1],
            'duration': row[2],
            'artist_id': row[3],
            'artist_name': row[4],
            'album_id': row[5],
            'album_title': row[6],
            'file_url': f"{base_url}/api/songs/{row[0]}/stream" if row[7] else None
        } for row in songs]
        
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        close_db(conn)

@songs_bp.route('/<int:song_id>', methods=['GET'])
def get_song(song_id):
    """获取单个歌曲信息（仅限当前用户自己的歌曲）"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'error': '未授权'}), 401

    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT s.song_id, s.title, s.duration,
                   s.artist_id, ar.name as artist_name,
                   s.album_id, al.title as album_title,
                   CASE WHEN s.file_data IS NOT NULL THEN 1 ELSE 0 END as has_file
            FROM songs s
            LEFT JOIN artists ar ON s.artist_id = ar.artist_id
            LEFT JOIN albums al ON s.album_id = al.album_id
            WHERE s.song_id = %s AND s.user_id = %s
        ''', (song_id, user_id))
        song = cursor.fetchone()
        
        if not song:
            return jsonify({'error': '歌曲不存在或无权访问'}), 404
        
        base_url = request.host_url.rstrip('/')
        return jsonify({
            'song_id': song[0],
            'title': song[1],
            'duration': song[2],
            'artist_id': song[3],
            'artist_name': song[4],
            'album_id': song[5],
            'album_title': song[6],
            'file_url': f"{base_url}/api/songs/{song[0]}/stream" if song[7] else None
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        close_db(conn)

@songs_bp.route('/', methods=['POST'])
def create_song():
    """创建新歌曲"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'error': '未授权'}), 401

    # 检查是否有文件上传
    if 'file' not in request.files:
        return jsonify({'error': '未上传文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '未选择文件'}), 400

    title = request.form.get('title')
    artist_id = _to_int_or_none(request.form.get('artist_id'))
    album_id = _to_int_or_none(request.form.get('album_id'))
    duration = _to_int_or_none(request.form.get('duration'))
    
    if not title:
        return jsonify({'error': '歌曲名称不能为空'}), 400
    
    if duration is None:
        return jsonify({'error': '时长必须为整数(秒)'}), 400

    file_data = file.read()
    if not file_data:
        return jsonify({'error': '文件为空'}), 400

    file_mime = file.mimetype or 'application/octet-stream'
    upload_time = datetime.now()

    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            'INSERT INTO songs (title, artist_id, album_id, duration, file_url, file_data, file_mime, user_id, upload_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING song_id',
            (title, artist_id, album_id, duration, None, psycopg2.Binary(file_data), file_mime, user_id, upload_time)
        )
        song_id = cursor.fetchone()[0]
        conn.commit()
        base_url = request.host_url.rstrip('/')
        full_file_url = f"{base_url}/api/songs/{song_id}/stream"
        return jsonify({'message': '创建成功', 'song_id': song_id, 'file_url': full_file_url}), 201
    
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        close_db(conn)


@songs_bp.route('/<int:song_id>', methods=['PUT'])
def update_song(song_id):
    """更新歌曲信息"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'error': '未授权'}), 401

    data = request.get_json() or {}
    title = data.get('title')
    artist_id = _to_int_or_none(data.get('artist_id'))
    album_id = _to_int_or_none(data.get('album_id'))
    duration = _to_int_or_none(data.get('duration'))
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            'UPDATE songs SET title = %s, artist_id = %s, album_id = %s, duration = %s WHERE song_id = %s AND user_id = %s',
            (title, artist_id, album_id, duration, song_id, user_id)
        )
        conn.commit()
        
        if cursor.rowcount == 0:
            return jsonify({'error': '歌曲不存在或无权修改'}), 404
        
        return jsonify({'message': '更新成功'}), 200
    
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        close_db(conn)

@songs_bp.route('/<int:song_id>', methods=['DELETE'])
def delete_song(song_id):
    """删除歌曲"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'error': '未授权'}), 401

    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            '''
            DELETE FROM playlist_songs ps
            USING playlists p
            WHERE ps.playlist_id = p.playlist_id
              AND ps.song_id = %s
              AND p.user_id = %s
            ''',
            (song_id, user_id)
        )

        cursor.execute('DELETE FROM songs WHERE song_id = %s AND user_id = %s', (song_id, user_id))
        conn.commit()
        
        if cursor.rowcount == 0:
            return jsonify({'error': '歌曲不存在或无权删除'}), 404
        
        return jsonify({'message': '删除成功'}), 200
    
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        close_db(conn)

@songs_bp.route('/<int:song_id>/stream', methods=['GET'])
def stream_song(song_id):
    """从数据库中读取歌曲并流式返回"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'error': '未授权'}), 401

    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute(
            'SELECT file_data, file_mime FROM songs WHERE song_id = %s AND user_id = %s',
            (song_id, user_id)
        )
        row = cursor.fetchone()
        if not row or not row[0]:
            return jsonify({'error': '歌曲文件不存在'}), 404

        file_data, file_mime = row
        return send_file(
            io.BytesIO(file_data),
            mimetype=file_mime or 'application/octet-stream',
            as_attachment=False,
            download_name=f"song_{song_id}",
            conditional=True
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        close_db(conn)
