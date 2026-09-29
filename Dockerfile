# D2C - Docker to Compose
# 国内可用镜像源（支持通过 --build-arg BASE_IMAGE=... 自定义，默认使用 DaoCloud 国内加速源）
# 备用国内源推荐：
# - 华为云：swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/library/python:3.13-slim
# - 1Panel：docker.1panel.live/library/python:3.13-slim
ARG BASE_IMAGE=docker.m.daocloud.io/library/python:3.13-slim
FROM ${BASE_IMAGE}

WORKDIR /app

# 构建参数
ARG TARGETPLATFORM
ARG BUILDPLATFORM

RUN echo "Building for $TARGETPLATFORM on $BUILDPLATFORM"

# 安装系统运行依赖
# 优化减重策略：
# 1. 移除 build-essential 和 gcc（所有 Python 依赖在 PyPI 均有预编译二进制 Wheel，无需编译环境，节省 ~220MB）
# 2. 移除 docker-compose-plugin（D2C 仅通过 docker socket 转换生成 yaml，不执行 compose 运行，节省 ~60MB）
# 3. 剥离 requirements.txt 中的 mypy/pytest/black/ruff 等测试代码质量工具（节省 ~180MB）
# 4. 配置 Docker GPG 后自动 purge 卸载 gnupg 并合并清理层（节省 ~25MB）
RUN echo "deb http://mirrors.aliyun.com/debian/ bookworm main non-free contrib" > /etc/apt/sources.list \
    && echo "deb http://mirrors.aliyun.com/debian-security bookworm-security main" >> /etc/apt/sources.list \
    && echo "deb http://mirrors.aliyun.com/debian/ bookworm-updates main non-free contrib" >> /etc/apt/sources.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        ca-certificates \
        gnupg \
    && mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://mirrors.aliyun.com/docker-ce/linux/debian/gpg \
        | gpg --dearmor -o /etc/apt/keyrings/docker.gpg \
    && chmod a+r /etc/apt/keyrings/docker.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
        https://mirrors.aliyun.com/docker-ce/linux/debian \
        $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
        | tee /etc/apt/sources.list.d/docker.list > /dev/null \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        docker-ce-cli \
    && apt-get purge -y --auto-remove gnupg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# 复制并安装 Python 运行时依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# 复制应用代码与入口脚本
COPY backend/ /app/
COPY entrypoint.sh /app/entrypoint.sh

# 创建必要目录、修复换行符、赋予权限并清理临时缓存（合并为单层）
RUN mkdir -p /app/config /app/compose /app/logs /app/templates /app/static /app/web \
    && sed -i 's/\r$//' /app/entrypoint.sh \
    && chmod +x /app/entrypoint.sh /app/*.sh /app/*.py 2>/dev/null || true \
    && find /app -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true \
    && find /app -name "*.pyc" -delete 2>/dev/null || true

# 暴露端口
EXPOSE 5000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" || exit 1

# 使用入口脚本启动
ENTRYPOINT ["/app/entrypoint.sh"]
