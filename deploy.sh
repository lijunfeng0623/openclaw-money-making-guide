#!/bin/bash
# 自动SEO博客系统 - 部署脚本
# 用法: bash deploy.sh
# 由OpenClaw cron job调用

set -e

BLOG_DIR="/Users/apple/Desktop/seo-blog"
cd "$BLOG_DIR"

echo "=================================="
echo "🦞 SEO博客系统 - 开始自动更新"
echo "时间: $(date '+%Y-%m-%d %H:%M')"
echo "=================================="

# 1. 运行Python生成脚本
python3 auto-seo-blog.py
PYTHON_EXIT=$?

if [ $PYTHON_EXIT -ne 0 ]; then
    echo "⚠️ Python脚本失败，退出码: $PYTHON_EXIT"
    exit $PYTHON_EXIT
fi

# 2. git push (用gh CLI，自带auth)
echo "📤 推送到GitHub..."

# 检查是否有变更
CHANGED=$(git status --porcelain | wc -l)
if [ "$CHANGED" -eq "0" ]; then
    echo "ℹ️ 无变更，跳过推送"
    exit 0
fi

# 提交并推送
git add .
git commit -m "📝 自动更新: $(date '+%Y-%m-%d %H:%M')"
git push origin main 2>/dev/null || {
    echo "⚠️ 直连push失败，尝试gh..."
    gh repo sync lijunfeng0623/openclaw-money-making-guide --force 2>/dev/null || {
        echo "⚠️ gh sync也失败，备用方案:"
        git push https://x-access-token:$(gh auth token)@github.com/lijunfeng0623/openclaw-money-making-guide.git main 2>&1
    }
}

echo "✅ 推送完成"
echo "🏠 首页: https://lijunfeng0623.github.io/openclaw-money-making-guide/"
echo "=================================="
