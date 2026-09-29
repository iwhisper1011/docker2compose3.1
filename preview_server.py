#!/usr/bin/env python3
"""
Docker2Compose 本地交互式预览服务器
用于在本地无需运行 Docker daemon 的环境下直接预览和体验重构后的全新现代化 Web UI。
"""

import os
import sys
import time
from pathlib import Path
from flask import Flask, render_template, jsonify, request, session

# 确保能找到 templates 与 static
BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / 'backend' / 'web' / 'templates'
STATIC_DIR = BASE_DIR / 'backend' / 'web' / 'static'
COMPOSE_DIR = BASE_DIR / 'compose'
COMPOSE_DIR.mkdir(parents=True, exist_ok=True)

app = Flask(
    __name__,
    template_folder=str(TEMPLATES_DIR),
    static_folder=str(STATIC_DIR)
)
app.secret_key = 'd2c-preview-secret-key-local'

# --- 模拟容器与运行状态数据 ---
MOCK_CONTAINERS = [
    {
        'id': 'group_web',
        'name': 'web-tier-network',
        'type': 'group',
        'count': 2,
        'containers': [
            {
                'id': 'c_nginx_proxy',
                'name': 'nginx-reverse-proxy',
                'image': 'nginx:alpine-slim',
                'status': 'running',
                'network_mode': 'web-tier-network'
            },
            {
                'id': 'c_web_frontend',
                'name': 'frontend-dashboard',
                'image': 'node:20-alpine',
                'status': 'running',
                'network_mode': 'web-tier-network'
            }
        ]
    },
    {
        'id': 'group_data',
        'name': 'database-bridge',
        'type': 'group',
        'count': 2,
        'containers': [
            {
                'id': 'c_postgres_db',
                'name': 'postgres-master-db',
                'image': 'postgres:16-alpine',
                'status': 'running',
                'network_mode': 'database-bridge'
            },
            {
                'id': 'c_redis_cache',
                'name': 'redis-session-cache',
                'image': 'redis:7.2-alpine',
                'status': 'running',
                'network_mode': 'database-bridge'
            }
        ]
    },
    {
        'id': 'group_nas',
        'name': 'media-services',
        'type': 'group',
        'count': 2,
        'containers': [
            {
                'id': 'c_jellyfin_nas',
                'name': 'jellyfin-media-server',
                'image': 'jellyfin/jellyfin:latest',
                'status': 'running',
                'network_mode': 'host'
            },
            {
                'id': 'c_qbittorrent',
                'name': 'qbittorrent-nox',
                'image': 'linuxserver/qbittorrent:latest',
                'status': 'running',
                'network_mode': 'host'
            }
        ]
    },
    {
        'id': 'group_tools',
        'name': 'management-tools',
        'type': 'group',
        'count': 2,
        'containers': [
            {
                'id': 'c_portainer_ce',
                'name': 'portainer-ce-console',
                'image': 'portainer/portainer-ce:latest',
                'status': 'running',
                'network_mode': 'bridge'
            },
            {
                'id': 'c_dockge_mgr',
                'name': 'dockge-manager',
                'image': 'louislam/dockge:latest',
                'status': 'stopped',
                'network_mode': 'bridge'
            }
        ]
    }
]

# --- 模拟执行日志 ---
MOCK_LOGS = [
    {
        'timestamp': '2026-09-28T02:00:01',
        'level': 'info',
        'message': '[SCHEDULER] 触发启动备份任务: CRON (0 2 * * *)'
    },
    {
        'timestamp': '2026-09-28T02:00:02',
        'level': 'info',
        'message': '[SCANNER] 扫描检测到 8 个活跃容器，4 个自定义网络拓扑'
    },
    {
        'timestamp': '2026-09-28T02:00:03',
        'level': 'info',
        'message': '[CONVERTER] 成功解析 nginx-reverse-proxy、postgres-master-db 端口映射与环境变量'
    },
    {
        'timestamp': '2026-09-28T02:00:04',
        'level': 'info',
        'message': '[STORAGE] 已生成备份目录 /app/compose/2026_09_28_02_00'
    },
    {
        'timestamp': '2026-09-28T02:00:05',
        'level': 'info',
        'message': '[SCHEDULER] 全量 Compose 备份任务执行完毕，耗时 3.8s'
    }
]

CURRENT_SETTINGS = {
    'cron': '0 2 * * *',
    'network': True,
    'show_healthcheck': True,
    'show_cap_add': True,
    'show_command': True,
    'show_entrypoint': True,
    'env_filter_keywords': 'VERSION,NODE_ENV,YARN_VERSION',
    'timezone': 'Asia/Shanghai'
}

SCHEDULER_STATUS = {
    'running': True,
    'cron': '0 2 * * *',
    'next_run': '2026-09-29T02:00:00',
    'last_run': '2026-09-28T02:00:00'
}

# 预置几个示例备份文件
def seed_sample_files():
    sample_dir = COMPOSE_DIR / '2026_09_28_13_12'
    sample_dir.mkdir(parents=True, exist_ok=True)
    sample_file = sample_dir / 'all-containers-compose.yaml'
    if not sample_file.exists():
        sample_file.write_text("""version: '3.8'

services:
  nginx-reverse-proxy:
    image: nginx:alpine-slim
    container_name: nginx-reverse-proxy
    ports:
      - "80:80"
      - "443:443"
    restart: unless-stopped
    networks:
      - web-tier-network

  postgres-master-db:
    image: postgres:16-alpine
    container_name: postgres-master-db
    environment:
      POSTGRES_USER: root
      POSTGRES_PASSWORD: secretpassword
      POSTGRES_DB: appdb
    volumes:
      - /data/postgres:/var/lib/postgresql/data
    restart: always
    networks:
      - database-bridge

networks:
  web-tier-network:
    external: true
  database-bridge:
    external: true
""", encoding='utf-8')

seed_sample_files()


# =============================================================================
# 路由定义
# =============================================================================

@app.route('/')
def index():
    return render_template('index.html')


# --- 认证相关 ---
@app.route('/api/auth/me', methods=['GET'])
def auth_me():
    # 预览模式默认已登录为 admin
    return jsonify({
        'success': True,
        'data': {
            'username': 'admin',
            'is_admin': True
        }
    })

@app.route('/api/auth/login', methods=['POST'])
def auth_login():
    return jsonify({
        'success': True,
        'data': {
            'user': {
                'username': 'admin',
                'is_admin': True
            },
            'require_password_change': False
        }
    })

@app.route('/api/auth/logout', methods=['POST'])
def auth_logout():
    return jsonify({'success': True, 'data': {}})

@app.route('/api/auth/change-password', methods=['POST'])
def auth_change_password():
    return jsonify({'success': True, 'message': '密码修改成功'})


# --- 容器与 Compose 接口 ---
@app.route('/api/containers', methods=['GET'])
def get_containers():
    return jsonify({
        'success': True,
        'data': MOCK_CONTAINERS
    })

@app.route('/api/compose', methods=['POST'])
def generate_compose():
    req = request.get_json() or {}
    container_ids = req.get('containers', [])
    
    # 根据勾选的容器模拟生成 compose
    selected_names = []
    for g in MOCK_CONTAINERS:
        for c in g['containers']:
            if c['id'] in container_ids:
                selected_names.append(c)
    
    if not selected_names:
        # 默认使用几个作为展示
        selected_names = [MOCK_CONTAINERS[0]['containers'][0]]

    services_yaml = ""
    for c in selected_names:
        services_yaml += f"""  {c['name']}:
    image: {c['image']}
    container_name: {c['name']}
    restart: unless-stopped
    networks:
      - {c['network_mode']}
    environment:
      - APP_ENV=production
      - TZ={CURRENT_SETTINGS['timezone']}

"""

    generated = f"""version: '3.8'

services:
{services_yaml}networks:
  default:
    driver: bridge
"""
    return jsonify({
        'success': True,
        'data': {
            'yaml': generated,
            'filename': f"{selected_names[0]['name']}-compose.yaml"
        }
    })

@app.route('/api/generate-all-compose', methods=['POST'])
def generate_all_compose():
    timestamp = time.strftime("%Y_%m_%d_%H_%M")
    out_dir = COMPOSE_DIR / timestamp
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / 'all-containers-compose.yaml'
    
    content = """version: '3.8'

services:
  nginx-reverse-proxy:
    image: nginx:alpine-slim
    ports:
      - "80:80"
    restart: unless-stopped

  postgres-master-db:
    image: postgres:16-alpine
    restart: always

  jellyfin-media-server:
    image: jellyfin/jellyfin:latest
    network_mode: host
"""
    out_file.write_text(content, encoding='utf-8')
    return jsonify({
        'success': True,
        'message': '全量 Compose 文件已生成',
        'data': {
            'yaml': content,
            'filepath': str(out_file)
        }
    })


# --- 备份文件管理 ---
@app.route('/api/files', methods=['GET'])
def list_files():
    folders = []
    root_files = []
    
    for item in sorted(COMPOSE_DIR.glob('*'), reverse=True):
        if item.is_dir():
            files_in_dir = []
            for f in sorted(item.glob('*.yaml'), reverse=True):
                stat = f.stat()
                files_in_dir.append({
                    'name': f.name,
                    'path': str(f.relative_to(BASE_DIR)),
                    'size': stat.st_size,
                    'modified': int(stat.st_mtime)
                })
            stat = item.stat()
            folders.append({
                'name': item.name,
                'path': str(item.relative_to(BASE_DIR)),
                'files': files_in_dir,
                'modified': int(stat.st_mtime)
            })
        elif item.suffix in ('.yaml', '.yml'):
            stat = item.stat()
            root_files.append({
                'name': item.name,
                'path': str(item.relative_to(BASE_DIR)),
                'size': stat.st_size,
                'modified': int(stat.st_mtime)
            })

    return jsonify({
        'success': True,
        'data': {
            'root': root_files,
            'folders': folders
        }
    })

@app.route('/api/files/content', methods=['POST'])
def file_content():
    req = request.get_json() or {}
    rel_path = req.get('path', '')
    target = BASE_DIR / rel_path
    if target.exists() and target.is_file():
        return jsonify({
            'success': True,
            'data': {
                'content': target.read_text(encoding='utf-8'),
                'path': rel_path
            }
        })
    return jsonify({'success': False, 'error': '文件不存在'}), 404

@app.route('/api/save-compose', methods=['POST'])
def save_compose():
    req = request.get_json() or {}
    filename = req.get('filename', 'compose.yaml').strip() or 'compose.yaml'
    content = req.get('content', '')
    
    target = COMPOSE_DIR / filename
    target.write_text(content, encoding='utf-8')
    return jsonify({
        'success': True,
        'message': f'文件 {filename} 保存成功'
    })

@app.route('/api/files/delete', methods=['POST'])
def delete_file():
    req = request.get_json() or {}
    rel_path = req.get('path', '')
    target = BASE_DIR / rel_path
    if target.exists():
        if target.is_file():
            target.unlink()
        elif target.is_dir():
            import shutil
            shutil.rmtree(target)
        return jsonify({'success': True, 'message': '删除成功'})
    return jsonify({'success': False, 'error': '文件或目录不存在'}), 404


# --- 系统设置 ---
@app.route('/api/settings', methods=['GET', 'POST'])
def handle_settings():
    global CURRENT_SETTINGS
    if request.method == 'POST':
        req = request.get_json() or {}
        new_settings = req.get('settings', {})
        CURRENT_SETTINGS.update(new_settings)
        return jsonify({'success': True, 'message': '设置保存成功'})
    
    return jsonify({
        'success': True,
        'data': CURRENT_SETTINGS
    })


# --- 定时任务调度器与日志 ---
@app.route('/api/scheduler/status', methods=['GET'])
def scheduler_status():
    return jsonify({
        'success': True,
        'data': SCHEDULER_STATUS
    })

@app.route('/api/scheduler/start', methods=['POST'])
def scheduler_start():
    SCHEDULER_STATUS['running'] = True
    return jsonify({'success': True, 'message': '启动任务已开启'})

@app.route('/api/scheduler/stop', methods=['POST'])
def scheduler_stop():
    SCHEDULER_STATUS['running'] = False
    return jsonify({'success': True, 'message': '启动任务已停止'})

@app.route('/api/scheduler/run-once', methods=['POST'])
def scheduler_run_once():
    MOCK_LOGS.append({
        'timestamp': time.strftime("%Y-%m-%dT%H:%M:%S"),
        'level': 'info',
        'message': '[MANUAL] 用户手动触发一次全量配置备份任务'
    })
    return jsonify({'success': True, 'message': '任务已启动'})

@app.route('/api/scheduler/logs', methods=['GET'])
def scheduler_logs():
    return jsonify({
        'success': True,
        'data': {
            'logs': MOCK_LOGS
        }
    })

@app.route('/api/scheduler/clear-logs', methods=['POST'])
def clear_logs():
    MOCK_LOGS.clear()
    return jsonify({'success': True, 'message': '日志已清空'})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5050))
    print(f"==================================================")
    print(f"🚀 Docker2Compose 本地交互式预览服务器已启动!")
    print(f"👉 浏览器访问: http://localhost:{port}")
    print(f"==================================================")
    app.run(host='0.0.0.0', port=port, debug=False)
