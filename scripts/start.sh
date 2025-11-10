#!/bin/bash

# 随机阅读电子书应用启动脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        log_error "$1 命令未找到，请先安装 $1"
        exit 1
    fi
}

# 检查Docker和Docker Compose
check_dependencies() {
    log_info "检查依赖..."

    check_command "docker"
    check_command "docker-compose"

    # 检查Docker服务是否运行
    if ! docker info &> /dev/null; then
        log_error "Docker服务未运行，请启动Docker服务"
        exit 1
    fi

    log_success "依赖检查完成"
}

# 创建必要的目录
create_directories() {
    log_info "创建必要的目录..."

    mkdir -p data
    mkdir -p app/static/uploads
    mkdir -p app/logs
    mkdir -p ssl

    log_success "目录创建完成"
}

# 生成随机密钥
generate_secret_key() {
    if [ ! -f .env ]; then
        log_info "生成随机密钥..."
        SECRET_KEY=$(openssl rand -hex 32)
        sed "s/please-change-this-in-production/$SECRET_KEY/" .env.example > .env
        log_success "随机密钥已生成"
    else
        log_info "环境配置文件已存在"
    fi
}

# 构建和启动服务
start_services() {
    log_info "构建和启动服务..."

    # 构建镜像
    docker-compose build

    # 启动服务
    docker-compose up -d

    log_success "服务启动完成"
}

# 检查服务状态
check_services() {
    log_info "检查服务状态..."

    # 等待服务启动
    sleep 10

    # 检查应用健康状态
    if curl -f http://localhost:8000/health &> /dev/null; then
        log_success "应用运行正常"
    else
        log_error "应用启动失败"
        docker-compose logs app
        exit 1
    fi
}

# 显示信息
show_info() {
    log_success "🎉 部署完成！"
    echo ""
    echo "应用访问地址:"
    echo "  - 主应用: http://localhost:8000"
    echo "  - API文档: http://localhost:8000/docs"
    echo "  - 健康检查: http://localhost:8000/health"
    echo ""
    echo "常用命令:"
    echo "  - 查看日志: docker-compose logs -f"
    echo "  - 停止服务: docker-compose down"
    echo "  - 重启服务: docker-compose restart"
    echo "  - 查看状态: docker-compose ps"
    echo ""
}

# 主函数
main() {
    echo "🚀 随机阅读电子书应用部署脚本"
    echo "=================================="
    echo ""

    check_dependencies
    create_directories
    generate_secret_key
    start_services
    check_services
    show_info
}

# 脚本入口
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi