from flask import Blueprint, request, jsonify
from db import get_db, close_db

playlists_bp = Blueprint('playlists', __name__)

@playlists_bp.route('/', methods=['GET'])
def get_playlists():
    """获取所有歌单"""
    user_id = request.args.get('user_id')
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        if user_id:
            cursor.execute('''
                SELECT p.playlist_id, p.name, p.user_id, u.username,
                       COUNT(ps.song_id) as song_count
                FROM playlists p
                LEFT JOIN users u ON p.user_id = u.user_id
                LEFT JOIN playlist_songs ps ON p.playlist_id = ps.playlist_id
                WHERE p.user_id = %s
                GROUP BY p.playlist_id, p.name, p.user_id, u.username
                ORDER BY p.playlist_id
            ''', (user_id,))
        else:
            cursor.execute('''
                SELECT p.playlist_id, p.name, p.user_id, u.username,
                       COUNT(ps.song_id) as song_count
                FROM playlists p
                LEFT JOIN users u ON p.user_id = u.user_id
                LEFT JOIN playlist_songs ps ON p.playlist_id = ps.playlist_id
                GROUP BY p.playlist_id, p.name, p.user_id, u.username
                ORDER BY p.playlist_id
            ''')
        
        playlists = cursor.fetchall()
        
        result = [{
            'playlist_id': row[0],
            'name': row[1],
            'user_id': row[2],
            'username': row[3],
            'song_count': row[4]
        } for row in playlists]
        
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        close_db(conn)

@playlists_bp.route('/<int:playlist_id>', methods=['GET'])
def get_playlist(playlist_id):
    """获取歌单详情（包含歌曲列表）"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # 获取歌单信息
        cursor.execute('''
            SELECT p.playlist_id, p.name, p.user_id, u.username
            FROM playlists p
            LEFT JOIN users u ON p.user_id = u.user_id
            WHERE p.playlist_id = %s
        ''', (playlist_id,))
        playlist = cursor.fetchone()
        
        if not playlist:
            return jsonify({'error': '歌单不存在'}), 404
        
        # 获取歌单中的歌曲
        cursor.execute('''
            SELECT s.song_id, s.title, s.duration,
                   ar.name as artist_name, al.title as album_title,
                   CASE WHEN s.file_data IS NOT NULL THEN 1 ELSE 0 END as has_file
            FROM playlist_songs ps
            JOIN songs s ON ps.song_id = s.song_id
            LEFT JOIN artists ar ON s.artist_id = ar.artist_id
            LEFT JOIN albums al ON s.album_id = al.album_id
            WHERE ps.playlist_id = %s
        ''', (playlist_id,))
        songs = cursor.fetchall()

        base_url = request.host_url.rstrip('/')
        
        result = {
            'playlist_id': playlist[0],
            'name': playlist[1],
            'user_id': playlist[2],
            'username': playlist[3],
            'songs': [{
                'song_id': song[0],
                'title': song[1],
                'duration': song[2],
                'artist_name': song[3],
                'album_title': song[4],
                'file_url': f"{base_url}/api/songs/{song[0]}/stream" if song[5] else None
            } for song in songs]
        }
        
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        close_db(conn)

@playlists_bp.route('/', methods=['POST'])
def create_playlist():
    """创建新歌单"""
    data = request.get_json()
    name = data.get('name')
    user_id = data.get('user_id')
    
    if not name:
        return jsonify({'error': '歌单名称不能为空'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            'INSERT INTO playlists (name, user_id) VALUES (%s, %s) RETURNING playlist_id',
            (name, user_id)
        )
        playlist_id = cursor.fetchone()[0]
        conn.commit()
        
        return jsonify({'message': '创建成功', 'playlist_id': playlist_id}), 201
    
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        close_db(conn)

@playlists_bp.route('/<int:playlist_id>/songs', methods=['POST'])
def add_song_to_playlist(playlist_id):
    """向歌单添加歌曲"""
    data = request.get_json()
    song_id = data.get('song_id')
    
    if not song_id:
        return jsonify({'error': '歌曲ID不能为空'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            'INSERT INTO playlist_songs (playlist_id, song_id) VALUES (%s, %s)',
            (playlist_id, song_id)
        )
        conn.commit()
        
        return jsonify({'message': '添加成功'}), 201
    
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        close_db(conn)

@playlists_bp.route('/<int:playlist_id>/songs/<int:song_id>', methods=['DELETE'])
def remove_song_from_playlist(playlist_id, song_id):
    """从歌单移除歌曲"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            'DELETE FROM playlist_songs WHERE playlist_id = %s AND song_id = %s',
            (playlist_id, song_id)
        )
        conn.commit()
        
        if cursor.rowcount == 0:
            return jsonify({'error': '歌曲不在歌单中'}), 404
        
        return jsonify({'message': '移除成功'}), 200
    
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        close_db(conn)

@playlists_bp.route('/<int:playlist_id>', methods=['DELETE'])
def delete_playlist(playlist_id):
    """删除歌单"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # 先删除歌单-歌曲关系
        cursor.execute('DELETE FROM playlist_songs WHERE playlist_id = %s', (playlist_id,))
        # 再删除歌单
        cursor.execute('DELETE FROM playlists WHERE playlist_id = %s', (playlist_id,))
        conn.commit()
        
        if cursor.rowcount == 0:
            return jsonify({'error': '歌单不存在'}), 404
        
        return jsonify({'message': '删除成功'}), 200
    
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        close_db(conn)
