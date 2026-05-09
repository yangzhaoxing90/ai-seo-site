#!/usr/bin/env python3
"""AI SEO内容站生成器 - 调用Mimo API批量生成文章并构建静态站点"""
import os, sys, json, time, re, hashlib
from datetime import datetime

sys.path.insert(0, r"D:\codespace\GenericAgent")
import mykey

import urllib.request

# ── Config ──
SITE_DIR = os.path.dirname(os.path.abspath(__file__))
ARTICLES_DIR = os.path.join(SITE_DIR, "articles")
OUTPUT_DIR = os.path.join(SITE_DIR, "output")
SITE_TITLE = "AI工具指南"
SITE_DESC = "最全的AI工具使用教程，助你用AI提升效率10倍"

config = mykey.native_claude_config_mimo
API_BASE = config['apibase'].replace('/anthropic', '/v1/chat/completions')
API_KEY = config['apikey']
MODEL = config['model']
PROXY = getattr(mykey, 'proxy', None)

# ── Topics ──
TOPICS = [
    {"slug": "chatgpt-prompt-advanced", "title": "ChatGPT高级提示词技巧：10个让AI输出质量翻倍的方法", "keywords": ["ChatGPT提示词", "prompt技巧", "AI提示词", "ChatGPT教程"]},
    {"slug": "ai-writing-tools-2025", "title": "2025年最好用的AI写作工具对比：秘塔/讯飞/文心一言", "keywords": ["AI写作工具", "AI写作", "秘塔写作猫", "讯飞星火"]},
    {"slug": "midjourney-ai-painting", "title": "Midjourney AI绘画入门教程：从零开始生成专业图片", "keywords": ["Midjourney", "AI绘画", "AI绘图", "文生图"]},
    {"slug": "ai-ppt-tools", "title": "5款AI自动生成PPT工具测评：告别加班做PPT", "keywords": ["AI生成PPT", "AI PPT工具", "自动生成PPT"]},
    {"slug": "ai-code-assistant", "title": "AI编程助手全面对比：GitHub Copilot vs 通义灵码 vs Cursor", "keywords": ["AI编程", "GitHub Copilot", "通义灵码", "Cursor"]},
    {"slug": "ai-video-editing", "title": "AI视频剪辑工具推荐：自动字幕/配音/剪辑一条龙", "keywords": ["AI视频剪辑", "AI字幕", "AI配音", "剪映AI"]},
    {"slug": "ai-translation-tools", "title": "2025年AI翻译工具深度测评：DeepL/有道/百度翻译谁更强", "keywords": ["AI翻译", "DeepL", "有道翻译", "百度翻译"]},
    {"slug": "ai-search-engine", "title": "AI搜索引擎对比：秘塔AI搜索 vs 天工AI vs Perplexity", "keywords": ["AI搜索", "秘塔AI搜索", "天工AI", "AI搜索引擎"]},
    {"slug": "ai-excel-data", "title": "用AI处理Excel数据：10分钟搞定以前2小时的工作", "keywords": ["AI处理Excel", "AI数据分析", "AI表格"]},
    {"slug": "ai-meeting-summary", "title": "AI会议纪要工具推荐：自动记录+总结+提取待办", "keywords": ["AI会议", "会议纪要", "AI记录"]},
    {"slug": "stable-diffusion-local", "title": "Stable Diffusion本地部署教程：0成本跑AI绘画", "keywords": ["Stable Diffusion", "本地部署", "AI绘画"]},
    {"slug": "ai-clone-voice", "title": "AI语音克隆工具使用教程：3秒复制你的声音", "keywords": ["AI语音克隆", "AI配音", "声音克隆"]},
    {"slug": "ai-resume-writer", "title": "用AI写简历：ChatGPT帮你打造完美求职简历", "keywords": ["AI写简历", "ChatGPT简历", "AI求职"]},
    {"slug": "ai-study-assistant", "title": "AI学习助手使用指南：让AI成为你的私人辅导老师", "keywords": ["AI学习", "AI辅导", "AI教育"]},
    {"slug": "dify-ai-workflow", "title": "Dify零代码搭建AI工作流：从入门到实战", "keywords": ["Dify", "AI工作流", "零代码AI"]},
    {"slug": "coze-bot-make", "title": "扣子(Coze)搭建AI机器人教程：5分钟创建专属助手", "keywords": ["扣子", "Coze", "AI机器人", "AI助手"]},
    {"slug": "ai-productivity-tools", "title": "2025年提升工作效率的10个AI工具推荐", "keywords": ["AI效率工具", "AI工具推荐", "AI办公"]},
    {"slug": "ai-image-upscale", "title": "AI图片放大工具对比：免费无损放大4K不是梦", "keywords": ["AI图片放大", "无损放大", "图片修复"]},
    {"slug": "ai-music-generate", "title": "AI音乐生成工具测评：Suno/Udio零基础创作音乐", "keywords": ["AI音乐", "Suno", "Udio", "AI作曲"]},
    {"slug": "ai-agent-beginner", "title": "AI Agent入门：什么是AI智能体，如何搭建自己的Agent", "keywords": ["AI Agent", "AI智能体", "AI代理"]},
]


def call_mimo(prompt, max_tokens=3000):
    """Call Mimo API (OpenAI compatible)"""
    payload = json.dumps({
        "model": MODEL,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}]
    }).encode('utf-8')
    
    req = urllib.request.Request(API_BASE, data=payload, headers={
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {API_KEY}'
    })
    
    if PROXY:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({'https': PROXY, 'http': PROXY}))
    else:
        opener = urllib.request.build_opener()
    
    resp = opener.open(req, timeout=120)
    result = json.loads(resp.read().decode('utf-8'))
    return result['choices'][0]['message']['content']


def generate_article(topic):
    """Generate a full SEO article for a topic"""
    prompt = f"""你是一位资深的AI科技博主。请写一篇关于"{topic['title']}"的高质量中文SEO文章。

要求：
1. 标题用 # H1，正文用 ## H2 和 ### H3 合理分层
2. 字数1000-1500字
3. 开头用1-2句话点明痛点（用户为什么要看这篇）
4. 包含具体操作步骤（1/2/3编号）
5. 包含优缺点对比或表格
6. 结尾总结+行动建议
7. 语言自然口语化，不要AI味
8. 在文中自然融入这些关键词：{', '.join(topic['keywords'])}
9. 只输出Markdown正文，不要额外说明

关键词：{', '.join(topic['keywords'])}"""
    
    return call_mimo(prompt, max_tokens=3000)


def slug_to_title(slug):
    """Get title from TOPICS by slug"""
    for t in TOPICS:
        if t['slug'] == slug:
            return t['title']
    return slug


def build_site(article_files):
    """Build static HTML site from article markdown files"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Sort by date (newest first)
    articles = []
    for f in article_files:
        fpath = os.path.join(ARTICLES_DIR, f)
        with open(fpath, 'r', encoding='utf-8') as fh:
            content = fh.read()
        # Extract first H1 as title
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else f
        slug = f.replace('.md', '')
        date = datetime.fromtimestamp(os.path.getmtime(fpath)).strftime('%Y-%m-%d')
        articles.append({'slug': slug, 'title': title, 'content': content, 'date': date, 'file': f})
    
    articles.sort(key=lambda x: x['date'], reverse=True)
    
    # Convert markdown to simple HTML
    def md_to_html(md):
        html = md
        # Headers
        html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        # Bold/italic
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
        # Links
        html = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', html)
        # Lists
        html = re.sub(r'^\- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
        html = re.sub(r'(<li>.*</li>\n?)+', lambda m: f'<ul>{m.group(0)}</ul>', html)
        # Paragraphs
        html = re.sub(r'\n\n', '</p><p>', html)
        html = f'<p>{html}</p>'
        html = html.replace('<p></p>', '').replace('<p><h', '<h').replace('</h1></p>', '</h1>').replace('</h2></p>', '</h2>').replace('</h3></p>', '</h3>')
        html = re.sub(r'<p><ul>', '<ul>', html)
        html = re.sub(r'</ul></p>', '</ul>', html)
        return html
    
    # Build index.html
    articles_html = ""
    for a in articles:
        articles_html += f"""
        <article class="card">
            <time>{a['date']}</time>
            <h2><a href="articles/{a['slug']}.html">{a['title']}</a></h2>
        </article>"""
    
    index_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="{SITE_DESC}">
<title>{SITE_TITLE} - {SITE_DESC}</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#f5f5f5;color:#333;line-height:1.8}}
.container{{max-width:800px;margin:0 auto;padding:20px}}
header{{text-align:center;padding:40px 0;border-bottom:2px solid #e0e0e0;margin-bottom:30px}}
header h1{{font-size:2em;color:#1a1a1a}}
header p{{color:#666;margin-top:8px}}
.card{{background:#fff;border-radius:8px;padding:20px;margin-bottom:16px;box-shadow:0 1px 3px rgba(0,0,0,0.08);transition:transform 0.2s}}
.card:hover{{transform:translateY(-2px);box-shadow:0 4px 12px rgba(0,0,0,0.12)}}
.card h2{{font-size:1.2em;margin-top:8px}}
.card a{{color:#1a1a1a;text-decoration:none}}
.card a:hover{{color:#0066cc}}
.card time{{color:#999;font-size:0.85em}}
footer{{text-align:center;padding:30px 0;color:#999;font-size:0.85em}}
</style>
</head>
<body>
<div class="container">
<header>
<h1>🚀 {SITE_TITLE}</h1>
<p>{SITE_DESC}</p>
</header>
<main>{articles_html}
</main>
<footer>© 2025 {SITE_TITLE} · 由AI辅助创作</footer>
</div>
</body>
</html>"""
    
    with open(os.path.join(OUTPUT_DIR, "index.html"), 'w', encoding='utf-8') as f:
        f.write(index_html)
    
    # Build article pages
    os.makedirs(os.path.join(OUTPUT_DIR, "articles"), exist_ok=True)
    for a in articles:
        article_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="{a['title']}">
<title>{a['title']} - {SITE_TITLE}</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#f5f5f5;color:#333;line-height:1.8}}
.container{{max-width:800px;margin:0 auto;padding:20px}}
.breadcrumb{{margin-bottom:20px;font-size:0.9em}}
.breadcrumb a{{color:#0066cc;text-decoration:none}}
article{{background:#fff;border-radius:8px;padding:30px;box-shadow:0 1px 3px rgba(0,0,0,0.08)}}
h1{{font-size:1.8em;margin-bottom:10px;color:#1a1a1a}}
h2{{font-size:1.4em;margin:30px 0 15px;color:#1a1a1a;border-left:4px solid #0066cc;padding-left:12px}}
h3{{font-size:1.15em;margin:20px 0 10px;color:#333}}
p{{margin-bottom:15px}}
ul{{margin:10px 0 15px 20px}}
li{{margin-bottom:6px}}
strong{{color:#1a1a1a}}
a{{color:#0066cc}}
footer{{text-align:center;padding:30px 0;color:#999;font-size:0.85em}}
</style>
</head>
<body>
<div class="container">
<div class="breadcrumb"><a href="../index.html">← 首页</a></div>
<article>{md_to_html(a['content'])}</article>
<footer><a href="../index.html">← 返回首页</a> · © 2025 {SITE_TITLE}</footer>
</div>
</body>
</html>"""
        with open(os.path.join(OUTPUT_DIR, "articles", f"{a['slug']}.html"), 'w', encoding='utf-8') as f:
            f.write(article_html)
    
    print(f"Built {len(articles)} articles -> {OUTPUT_DIR}")


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "generate"
    
    if mode == "generate":
        # Generate articles for topics that don't have files yet
        existing = set(f.replace('.md', '') for f in os.listdir(ARTICLES_DIR) if f.endswith('.md'))
        to_gen = [t for t in TOPICS if t['slug'] not in existing]
        
        print(f"已有 {len(existing)} 篇，待生成 {len(to_gen)} 篇")
        
        for i, topic in enumerate(to_gen):
            print(f"[{i+1}/{len(to_gen)}] 生成: {topic['title']}...")
            try:
                content = generate_article(topic)
                fpath = os.path.join(ARTICLES_DIR, f"{topic['slug']}.md")
                with open(fpath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"  OK ({len(content)} chars)")
                if i < len(to_gen) - 1:
                    time.sleep(1)
            except Exception as e:
                print(f"  FAIL: {e}")
    
    elif mode == "build":
        files = [f for f in os.listdir(ARTICLES_DIR) if f.endswith('.md')]
        build_site(files)
        print("Build complete!")
    
    elif mode == "all":
        # Generate then build
        existing = set(f.replace('.md', '') for f in os.listdir(ARTICLES_DIR) if f.endswith('.md'))
        to_gen = [t for t in TOPICS if t['slug'] not in existing]
        print(f"[generate] {len(existing)} done, {len(to_gen)} to go")
        for i, topic in enumerate(to_gen):
            print(f"[{i+1}/{len(to_gen)}] {topic['title']}...")
            try:
                content = generate_article(topic)
                fpath = os.path.join(ARTICLES_DIR, f"{topic['slug']}.md")
                with open(fpath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"  OK ({len(content)} chars)")
                if i < len(to_gen) - 1:
                    time.sleep(1)
            except Exception as e:
                print(f"  FAIL: {e}")
        # Build
        files = [f for f in os.listdir(ARTICLES_DIR) if f.endswith('.md')]
        build_site(files)
        print(f"[build] {len(files)} articles -> {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
