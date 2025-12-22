from flask import Flask, send_from_directory
from flask_cors import CORS
import os
from typing import Optional
from config import Config
from db import Database

from routes.auth import auth_bp
from routes.artists import artists_bp
from routes.albums import albums_bp
from routes.songs import songs_bp
from routes.playlists import playlists_bp

app = Flask(__name__)
app.config.from_object(Config)

# 配置上传文件夹
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 启用CORS，允许前端跨域访问
CORS(app)

# 初始化数据库连接池
Database.initialize()

# 注册蓝图（路由）
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(artists_bp, url_prefix='/api/artists')
app.register_blueprint(albums_bp, url_prefix='/api/albums')
app.register_blueprint(songs_bp, url_prefix='/api/songs')
app.register_blueprint(playlists_bp, url_prefix='/api/playlists')


def _detect_audio_mimetype(file_path: str) -> Optional[str]:
    try:
        with open(file_path, 'rb') as f:
            head = f.read(32)
    except OSError:
        return None

    if len(head) < 12:
        return None

    # MP3: ID3 tag or MPEG frame sync
    if head[:3] == b'ID3' or (head[0:2] and head[0] == 0xFF and (head[1] & 0xE0) == 0xE0):
        return 'audio/mpeg'

    # WAV: RIFF....WAVE
    if head[:4] == b'RIFF' and head[8:12] == b'WAVE':
        return 'audio/wav'

    # FLAC
    if head[:4] == b'fLaC':
        return 'audio/flac'

    # MP4/M4A: ....ftypXXXX
    if head[4:8] == b'ftyp':
        brand = head[8:12]
        if brand in {b'M4A ', b'isom', b'iso2', b'mp41', b'mp42'}:
            return 'audio/mp4'

    return None

@app.route('/')
def index():
    return {'message': '音乐管理系统API', 'status': 'running'}

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    mimetype = _detect_audio_mimetype(file_path)
    if mimetype:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, mimetype=mimetype, conditional=True)
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, conditional=True)

# 兼容前端通过 /api 前缀访问上传文件（Vite 仅代理 /api）
@app.route('/api/uploads/<path:filename>')
def uploaded_file_api(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    mimetype = _detect_audio_mimetype(file_path)
    if mimetype:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, mimetype=mimetype, conditional=True)
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, conditional=True)

@app.route('/api/health')
def health():
    """健康检查接口"""
    try:
        conn = Database.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        cursor.close()
        Database.return_connection(conn)
        return {'status': 'ok', 'database': 'connected'}
    except Exception as e:
        return {'status': 'error', 'database': 'disconnected', 'error': str(e)}, 500

if __name__ == '__main__':
    try:
        # 关闭 reloader，避免在某些环境中子进程/父进程切换导致服务立刻退出
        app.run(debug=True, use_reloader=False, host='0.0.0.0', port=5000)
    finally:
        Database.close_all_connections()
