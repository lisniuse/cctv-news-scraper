# cctv-news-scraper

一个 Claude Code Skill，用于从[东方财富网](https://www.eastmoney.com)抓取每日**央视新闻联播要闻集锦**。

## 功能

- 自动在东方财富网搜索当日"新闻联播"关键词
- 定位并打开当天的《央视新闻联播要闻集锦》文章
- 提取文章正文 HTML 内容（自动去除视频和无关属性）
- 支持指定日期和无头模式运行

## 环境要求

- Python 3.8+
- [Playwright](https://playwright.dev/python/)

```bash
pip install playwright
playwright install chromium
```

## 使用方式

### 作为 Claude Code Skill

将 `cctv-news-scraper.skill` 文件安装到 Claude Code 中即可使用。

### 作为独立脚本

```bash
# 抓取今天的新闻联播
python scripts/scrape_eastmoney.py

# 抓取指定日期
python scripts/scrape_eastmoney.py --date 2026-02-08

# 无头模式（不显示浏览器窗口）
python scripts/scrape_eastmoney.py --headless
```

## 项目结构

```
cctv-news-scraper/
├── SKILL.md                        # Skill 定义文件
├── README.md
└── scripts/
    └── scrape_eastmoney.py         # 抓取脚本
```

## 注意事项

- 新闻联播要闻集锦通常在每天 19:30（北京时间）之后发布
- 东方财富网页面结构可能变化，如抓取失败请检查页面选择器是否仍然有效
- 脚本使用 Playwright 模拟浏览器访问，需要已安装 Chromium

## License

MIT
