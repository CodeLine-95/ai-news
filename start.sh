#!/bin/bash
# 启动 AI 资讯聚合服务
cd "$(dirname "$0")"
export PORT="${PORT:-8080}"
exec python3.11 server.py
