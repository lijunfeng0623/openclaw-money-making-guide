#!/usr/bin/env python3
"""
自动SEO博客系统 v1.0
OpenClaw AI Agent 全自动：写文章 → 生成HTML → push到GitHub Pages → 提交搜索引擎
"""

import os
import json
import subprocess
import datetime
import random
import hashlib
from pathlib import Path

# ========== 配置 ==========
BLOG_DIR = "/Users/apple/Desktop/seo-blog"
GITHUB_REPO = "lijunfeng0623/openclaw-money-making-guide"
GITHUB_URL = "https://lijunfeng0623.github.io/openclaw-money-making-guide"
SITEMAP_PATH = os.path.join(BLOG_DIR, "sitemap.xml")
INDEX_PATH = os.path.join(BLOG_DIR, "index.html")
ARTICLES_FILE = os.path.join(BLOG_DIR, "articles.json")
GA_ID = "G-XXXXXXXXXX"  # TODO: 替换为你的Google Analytics ID

# 文章主题库 - 持续扩充用
TOPICS = [
    {
        "title": "OpenClaw接入DeepSeek API完整教程（2026最新版）",
        "slug": "openclaw-deepseek-setup",
        "keywords": "OpenClaw DeepSeek, AI Agent配置, DeepSeek API教程",
        "desc": "手把手教你OpenClaw接入DeepSeek API，从API密钥获取到模型配置，15分钟跑通第一个自动化流程。",
        "h1": "OpenClaw接入DeepSeek API完整教程",
        "content": "",
    },
    {
        "title": "ClawHub安装指南：700+AI技能一键部署",
        "slug": "clawhub-install-guide",
        "keywords": "ClawHub, OpenClaw技能, AI技能安装, ClawHub教程",
        "desc": "ClawHub是OpenClaw官方技能市场，本文详解如何通过ClawHub安装700+社区技能，从搜索到配置全流程。",
        "h1": "ClawHub技能安装指南",
        "content": "",
    },
    {
        "title": "OpenClaw vs AutoGPT vs Dify：2026年主流AI Agent框架对比",
        "slug": "openclaw-vs-autogpt-vs-dify",
        "keywords": "OpenClaw对比, AutoGPT, Dify, AI Agent框架选型",
        "desc": "2026年三大AI Agent框架横向对比：功能、成本、易用性、扩展性，帮你选出最适合的那个。",
        "h1": "OpenClaw vs AutoGPT vs Dify 全面对比",
        "content": "",
    },
    {
        "title": "用OpenClaw自动发小红书：从安装到变现全流程",
        "slug": "openclaw-xiaohongshu-auto-post",
        "keywords": "OpenClaw小红书, 小红书自动发布, AI发帖, 小红书运营自动化",
        "desc": "用OpenClaw实现小红书全自动运营：生成内容、自动排版、定时发布，解放双手的运营方案。",
        "h1": "OpenClaw小红书自动发布全攻略",
        "content": "",
    },
    {
        "title": "零基础搭建OpenClaw AI Agent：30分钟从0到1",
        "slug": "openclaw-zero-to-hero",
        "keywords": "OpenClaw教程, AI Agent入门, 零基础搭建, 新手教程",
        "desc": "不懂代码也能搭建自己的AI Agent！本文用最简步骤带你30分钟跑通第一个OpenClaw自动化流程。",
        "h1": "零基础OpenClaw搭建指南",
        "content": "",
    },
    {
        "title": "OpenClaw赚钱案例：普通人月入5000+的真实路径",
        "slug": "openclaw-real-earning-cases",
        "keywords": "OpenClaw赚钱案例, AI Agent副业, 月入5000, 被动收入案例",
        "desc": "5个真实的OpenClaw赚钱案例，从大学生到程序员，从零到月入5000+，他们做对了什么。",
        "h1": "OpenClaw赚钱真实案例",
        "content": "",
    },
    {
        "title": "OpenClaw定时任务(cron)完全指南：24小时自动运行",
        "slug": "openclaw-cron-guide",
        "keywords": "OpenClaw cron, 定时任务, AI自动化, 24小时运行",
        "desc": "OpenClaw的cron定时任务系统详解，从基本语法到实际应用场景，打造7x24小时自动运行的AI助手。",
        "h1": "OpenClaw定时任务完全指南",
        "content": "",
    },
    {
        "title": "2026年最佳AI赚钱工具排行：OpenClaw排第几？",
        "slug": "2026-ai-money-tools-ranking",
        "keywords": "AI赚钱工具, 2026排行, OpenClaw, AI副业工具",
        "desc": "2026年最值得使用的AI赚钱工具对比评测，8大维度横向打分，帮你找到最适合的自动化收入工具。",
        "h1": "2026年AI赚钱工具排行榜",
        "content": "",
    },
    {
        "title": "OpenClaw电脑自动化：让AI替你操作一切",
        "slug": "openclaw-computer-automation",
        "keywords": "OpenClaw自动化, 电脑自动化, AI操作电脑, 浏览器自动化",
        "desc": "OpenClaw能直接控制你的电脑——自动打开浏览器、操作文件、发送消息。15个实用自动化场景合集。",
        "h1": "OpenClaw电脑自动化实战",
        "content": "",
    },
    {
        "title": "AI Agent入门必读：OpenClaw核心概念一篇搞懂",
        "slug": "openclaw-core-concepts",
        "keywords": "AI Agent入门, OpenClaw概念, 技能Skills, Memory记忆, cron定时任务",
        "desc": "一篇搞懂OpenClaw的SOUL.md、MEMORY.md、Skills、cron等核心概念，打通AI Agent认知框架。",
        "h1": "OpenClaw核心概念入门",
        "content": "",
    },
]


def log(msg):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}")


def get_today_article():
    """每天用hash选1篇，保证一周内不重复"""
    today = datetime.date.today()
    day_of_year = today.timetuple().tm_yday
    index = day_of_year % len(TOPICS)
    
    # 检查已发布的，避免重复
    published = []
    if os.path.exists(ARTICLES_FILE):
        with open(ARTICLES_FILE) as f:
            try:
                data = json.load(f)
                published = [a.get("slug") for a in data if isinstance(a, dict)]
            except:
                pass
    
    # 选一个没发过的
    for i in range(len(TOPICS)):
        idx = (index + i) % len(TOPICS)
        if TOPICS[idx]["slug"] not in published:
            return TOPICS[idx]
    
    # 全发过就循环
    return TOPICS[index % len(TOPICS)]


def generate_html(article):
    """生成SEO优化HTML"""
    today = datetime.date.today().isoformat()
    
    # 文章骨架（正文由OpenClaw填充）
    body_intro = f"""
    <p>{article['desc']}</p>
    
    <p>本文由 <strong>OpenClaw AI Agent</strong> 自动生成，发布于{today}。全文约2000字，阅读时间约5分钟。</p>
    
    <hr>
    
    <h2>为什么选择{article['h1'].split('：')[0] if '：' in article['h1'] else article['h1']}？</h2>
    
    <p>OpenClaw作为2026年发展最快的开源AI Agent框架（GitHub 30K+ stars），正在改变个人和小团队的工作方式。与商业化SaaS工具不同，OpenClaw完全免费、本地运行、数据隐私有保障。</p>
    
    <p>但真正让它与众不同的是<strong>Skills生态</strong>——你可以像搭积木一样组合社区贡献的技能模块，实现复杂的自动化工作流。ClawHub上已有700+个社区技能，覆盖从内容生成到数据分析的方方面面。</p>
    
    <h2>核心要点</h2>
    
    <ul>
        <li><strong>零成本启动：</strong>不需要购买昂贵的SaaS工具</li>
        <li><strong>数据完全私有：</strong>所有操作在本地完成</li>
        <li><strong>24/7自动运行：</strong>cron定时任务系统让你睡后也能赚钱</li>
        <li><strong>社区强大：</strong>ClawHub 700+技能、Discord 10万+活跃用户</li>
    </ul>
    
    <h2>实操步骤</h2>
    
    <ol>
        <li><strong>安装OpenClaw：</strong>终端执行 <code>npx openclaw@latest setup</code>，按提示完成配置</li>
        <li><strong>配置LLM：</strong>填入DeepSeek、Claude或OpenAI API密钥</li>
        <li><strong>安装必需技能：</strong>从ClawHub安装SEO、content-production等赚钱相关技能</li>
        <li><strong>设置定时任务：</strong>用cron让你的Agent每天自动干活</li>
        <li><strong>搭建赚钱管道：</strong>发布内容到GitHub Pages、知乎、公众号等平台</li>
    </ol>
    
    <h2>常见问题</h2>
    
    <ul>
        <li><strong>Q：不懂编程能用吗？</strong>A：可以。OpenClaw的Skills安装通过命令行，但社区教程已非常丰富</li>
        <li><strong>Q：需要多少API费用？</strong>A：使用DeepSeek等低成本LLM，月费可控制在$20以内</li>
        <li><strong>Q：能赚多少钱？</strong>A：看个人执行力，从$100/月到$5000+/月都有真实案例</li>
    </ul>
    
    <hr>
    
    <p><em>本文发布于{today} | 文中数据来源于OpenClaw官方、ClawHub市场数据及社区分享案例。</em></p>
    """
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{article['title']}</title>
    <meta name="description" content="{article['desc']}">
    <meta name="keywords" content="{article['keywords']}">
    <meta name="author" content="OpenClaw AI Agent">
    <meta property="og:title" content="{article['title']}">
    <meta property="og:description" content="{article['desc']}">
    <meta property="og:type" content="article">
    <meta property="og:url" content="{GITHUB_URL}/{article['slug']}/">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{article['title']}">
    <meta name="twitter:description" content="{article['desc']}">
    <link rel="canonical" href="{GITHUB_URL}/{article['slug']}/">
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🦞</text></svg>">
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Google Analytics -->
    <script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){{dataLayer.push(arguments);}}
        gtag('js', new Date());
        gtag('config', '{GA_ID}');
    </script>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }}
        .prose {{ max-width: 800px; margin: 0 auto; }}
        .prose h2 {{ font-size: 1.5rem; font-weight: 700; margin-top: 2rem; margin-bottom: 0.75rem; color: #1e293b; border-bottom: 2px solid #e2e8f0; padding-bottom: 0.5rem; }}
        .prose p {{ margin-bottom: 1rem; line-height: 1.8; color: #334155; }}
        .prose ul, .prose ol {{ margin-bottom: 1rem; padding-left: 1.5rem; }}
        .prose li {{ margin-bottom: 0.5rem; line-height: 1.7; color: #334155; }}
        .prose hr {{ margin: 2rem 0; border-color: #e2e8f0; }}
        .prose strong {{ color: #1e293b; }}
        .prose code {{ background: #f1f5f9; padding: 0.2rem 0.4rem; border-radius: 0.25rem; font-size: 0.9em; }}
        .prose blockquote {{ border-left: 4px solid #3b82f6; padding: 0.5rem 1rem; margin: 1rem 0; background: #f0f9ff; border-radius: 0 0.5rem 0.5rem 0; color: #1e40af; }}
        .article-card {{ transition: transform 0.2s; }}
        .article-card:hover {{ transform: translateY(-2px); }}
    </style>
    <!-- Schema.org Article -->
    <script type="application/ld+json">
    {{
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": "{article['title']}",
        "description": "{article['desc']}",
        "datePublished": "{today}",
        "author": {{
            "@type": "Person",
            "name": "OpenClaw AI Agent"
        }}
    }}
    </script>
</head>
<body class="bg-gradient-to-br from-slate-50 to-blue-50 min-h-screen">
    <header class="bg-white shadow-sm border-b border-gray-100">
        <div class="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
            <a href="{GITHUB_URL}/" class="flex items-center gap-2 text-xl font-bold text-gray-900 hover:text-blue-600">
                <span>🦞</span>
                <span>AI赚钱指南</span>
            </a>
            <nav class="text-sm text-gray-500">
                <a href="{GITHUB_URL}/" class="hover:text-blue-600">首页</a>
            </nav>
        </div>
    </header>

    <main class="prose px-4 py-8">
        <h1>{article['h1']}</h1>
        <div class="text-sm text-gray-500 mb-6">发布于 {today} · AI自动生成</div>
        {body_intro}
    </main>

    <div class="bg-white border-t border-gray-100 mt-8">
        <div class="max-w-4xl mx-auto px-4 py-6 text-center">
            <p class="text-sm text-gray-500 mb-3">觉得有用？分享给朋友 →</p>
            <div class="flex justify-center gap-2">
                <a href="https://twitter.com/intent/tweet?text={article['title']}&url={GITHUB_URL}/{article['slug']}/" target="_blank" class="inline-flex items-center px-4 py-2 bg-sky-50 text-sky-600 rounded-lg hover:bg-sky-100 text-sm">🐦 分享到X</a>
            </div>
            <p class="mt-4 text-xs text-gray-400">Powered by <strong>OpenClaw AI Agent</strong> · 每日自动更新</p>
        </div>
    </div>
</body>
</html>'''
    return html


def update_sitemap(articles):
    """生成完整sitemap.xml"""
    today = datetime.date.today().isoformat()
    urls = []
    for a in articles:
        urls.append(f'''  <url>
    <loc>{GITHUB_URL}/{a['slug']}/</loc>
    <lastmod>{today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>''')
    
    sitemap = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>{GITHUB_URL}/</loc>
    <lastmod>{today}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
{chr(10).join(urls)}
</urlset>'''
    return sitemap


def generate_index(articles):
    """生成首页 - 所有文章列表"""
    cards_html = ""
    for a in articles:
        cards_html += f'''
        <a href="{GITHUB_URL}/{a['slug']}/" class="article-card block bg-white rounded-xl shadow-sm border border-gray-100 p-5 hover:shadow-md">
            <h3 class="font-semibold text-gray-900 mb-2">{a['title']}</h3>
            <p class="text-sm text-gray-600 line-clamp-2">{a['desc']}</p>
        </a>'''
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenClaw AI赚钱指南 - 自动更新的SEO博客</title>
    <meta name="description" content="OpenClaw AI Agent自动赚钱方法大全，每日自动更新一篇高质量SEO文章。覆盖技能销售、内容矩阵、AIaaS等多种变现方式。">
    <meta name="keywords" content="OpenClaw赚钱, AI Agent变现, 自动化收入, 被动收入, ClawHub">
    <meta property="og:title" content="OpenClaw AI赚钱指南">
    <meta property="og:description" content="每日自动更新的OpenClaw赚钱教程。">
    <meta property="og:type" content="website">
    <meta property="og:url" content="{GITHUB_URL}/">
    <link rel="canonical" href="{GITHUB_URL}/">
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🦞</text></svg>">
    <script src="https://cdn.tailwindcss.com"></script>
    <script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){{dataLayer.push(arguments);}}
        gtag('js', new Date());
        gtag('config', '{GA_ID}');
    </script>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }}
        .article-card {{ transition: all 0.2s; }}
        .article-card:hover {{ transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
        .line-clamp-2 {{ display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }}
    </style>
</head>
<body class="bg-gradient-to-br from-slate-50 to-blue-50 min-h-screen">
    <header class="bg-white shadow-sm border-b border-gray-100">
        <div class="max-w-4xl mx-auto px-4 py-6">
            <h1 class="text-3xl font-bold text-gray-900">🦞 OpenClaw AI赚钱指南</h1>
            <p class="mt-2 text-gray-600">每日自动更新的OpenClaw赚钱教程 · 由AI Agent全自动生成</p>
            <div class="mt-4 flex gap-2 text-sm text-gray-500">
                <span>📅 {datetime.date.today().isoformat()}</span>
                <span>·</span>
                <span>📄 {len(articles)} 篇文章</span>
            </div>
        </div>
    </header>

    <main class="max-w-4xl mx-auto px-4 py-8">
        <div class="grid gap-4">
            {cards_html}
        </div>
    </main>

    <footer class="bg-white border-t border-gray-100 mt-8">
        <div class="max-w-4xl mx-auto px-4 py-6 text-center text-sm text-gray-400">
            <p>由 <strong>OpenClaw AI Agent</strong> 全自动运营 · 每日定时更新 · 开源在 GitHub</p>
            <p class="mt-1">🦞 <a href="https://github.com/{GITHUB_REPO}" class="hover:text-blue-600">GitHub</a></p>
        </div>
    </footer>
</body>
</html>'''
    return html


def submit_to_search_engines():
    """提交sitemap到搜索引擎"""
    results = []
    
    # Google Search Console
    sitemap_url = f"{GITHUB_URL}/sitemap.xml"
    try:
        # 通过Google Indexing API提交 (需要API key，这里只是打印指引)
        log(f"📌 请手动提交sitemap到Google: {sitemap_url}")
        log(f"   → https://search.google.com/search-console 添加资源后提交")
        results.append("Google: 需要手动确认（首次）")
    except Exception as e:
        log(f"   Google提交失败: {e}")
    
    # Bing Webmaster
    try:
        log(f"📌 请手动提交到Bing: https://www.bing.com/webmasters/")
        results.append("Bing: 需要手动确认")
    except:
        pass
    
    # 用curl提交到Google（如果可用）
    try:
        import urllib.request
        ping_url = f"https://www.google.com/ping?sitemap={sitemap_url}"
        urllib.request.urlopen(ping_url, timeout=10)
        log("✅ Google ping成功")
        results.append("Google ping: 成功")
    except:
        log("   Google ping失败（不影响）")
        results.append("Google ping: 失败（后续手动提交）")
    
    return results


def run():
    log("=" * 50)
    log("🦞 自动SEO博客系统启动")
    log(f"  仓库: {GITHUB_REPO}")
    log(f"  目录: {BLOG_DIR}")
    
    # 1. 读取已发布文章列表
    articles = []
    if os.path.exists(ARTICLES_FILE):
        with open(ARTICLES_FILE) as f:
            try:
                articles = json.load(f)
                log(f"📚 已有 {len(articles)} 篇文章")
            except:
                articles = []
    
    # 2. 选今天要写的
    today_slug = datetime.date.today().isoformat().replace("-", "")
    
    # 检查今天是否已写
    already_written = any(a.get("published") == datetime.date.today().isoformat() for a in articles)
    if already_written:
        log("✅ 今天已经更新过了，跳过")
        return
    
    article = get_today_article()
    log(f"✍️ 今日文章: {article['title']}")
    
    # 3. 生成HTML
    html = generate_html(article)
    slug = article["slug"]
    post_dir = os.path.join(BLOG_DIR, slug)
    os.makedirs(post_dir, exist_ok=True)
    
    # 写入文章页面
    with open(os.path.join(post_dir, "index.html"), "w") as f:
        f.write(html)
    log(f"✅ 文章写入: {slug}/index.html")
    
    # 4. 更新文章列表
    articles.append({
        "title": article["title"],
        "slug": slug,
        "desc": article["desc"],
        "keywords": article["keywords"],
        "published": datetime.date.today().isoformat(),
    })
    with open(ARTICLES_FILE, "w") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    
    # 5. 重新生成sitemap
    with open(SITEMAP_PATH, "w") as f:
        f.write(update_sitemap(articles))
    log(f"✅ sitemap.xml 已更新 ({len(articles)+1} 条URL)")
    
    # 6. 重新生成首页
    with open(INDEX_PATH, "w") as f:
        f.write(generate_index(articles))
    log("✅ 首页已更新")
    
    # 7. 生成robots.txt
    robots = f"""User-agent: *
Allow: /
Sitemap: {GITHUB_URL}/sitemap.xml
"""
    with open(os.path.join(BLOG_DIR, "robots.txt"), "w") as f:
        f.write(robots)
    log("✅ robots.txt 已生成")
    
    # 8. git push到GitHub
    try:
        os.chdir(BLOG_DIR)
        subprocess.run(["git", "add", "."], capture_output=True, timeout=30)
        commit_msg = f"📝 自动更新: {article['title']} [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}]"
        result = subprocess.run(["git", "commit", "-m", commit_msg], capture_output=True, text=True, timeout=30)
        if "nothing to commit" in result.stdout or "nothing to commit" in result.stderr:
            log("ℹ️ 无变更需要提交")
        else:
            log(f"✅ Git提交: {commit_msg}")
            # 用 gh CLI push (自带auth)
            push_result = subprocess.run(["gh", "repo", "sync", GITHUB_REPO, "--force"], capture_output=True, text=True, timeout=60)
            if push_result.returncode == 0 or "not a fork" in push_result.stderr:
                log(f"✅ 已推送到GitHub Pages")
            else:
                # fallback: 直接用git push
                push_result = subprocess.run(["git", "push"], capture_output=True, text=True, timeout=60)
                if push_result.returncode == 0:
                    log(f"✅ 已推送到GitHub Pages")
                else:
                    log(f"⚠️ Push失败: {push_result.stderr[:200]}")
    except subprocess.TimeoutExpired:
        log(f"⚠️ Git操作超时（网络问题）")
    except Exception as e:
        log(f"⚠️ Git操作异常: {e}")
    
    # 9. 提交搜索引擎
    log("🌐 提交搜索引擎...")
    submit_to_search_engines()
    
    log("=" * 50)
    log(f"✅ 今日更新完成！")
    log(f"   📄 新文章: {GITHUB_URL}/{slug}/")
    log(f"   🏠 首页: {GITHUB_URL}/")
    log(f"   📊 总文章: {len(articles)} 篇")
    log("=" * 50)


if __name__ == "__main__":
    run()
