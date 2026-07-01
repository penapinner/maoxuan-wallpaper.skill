# 毛选壁纸 · Mao Quote Wallpaper

每天一句毛泽东语录，生成书法艺术桌面壁纸。支持 Windows / macOS / Linux。

> **100 条精选语录**，涵盖《毛泽东选集》全四卷 +《毛泽东文集》+《毛泽东诗词集》，随每日轮换。

![Preview](preview.png)

---

## 效果展示

朱砂红书法字 + 羊皮纸暖色调 + 毛选印章 + 出处注释

---

## 快速开始

### 1. 安装依赖

```bash
pip install Pillow
```

**中文字体**：脚本会自动检测系统已安装的书法字体。如果没有，安装一个即可：
- Windows：华文行楷（系统自带）
- macOS：安装任意楷体/行书字体
- Linux：`sudo apt install fonts-noto-cjk` 或安装任意楷体

### 2. 一键生成

```bash
# 随机语录
python run.py

# 随机 + 直接设为壁纸
python run.py --set-wallpaper

# 指定第 52 条
python run.py 52

# 列出全部 100 条语录
python run.py --list
```

### 3. 精确控制

```bash
python gen_wallpaper.py \
  --quote "星星之火，可以燎原" \
  --volume "《毛泽东选集》第一卷" \
  --article "《星星之火，可以燎原》" \
  --date "一九三〇年一月五日" \
  --year "一九三〇" \
  --note "毛泽东致林彪的复信。指出革命力量虽处微弱..." \
  --output wallpaper.png \
  --set-wallpaper
```

参数说明：

| 参数 | 必填 | 说明 |
|------|:----:|------|
| `--quote` | ✅ | 主语录文本 |
| `--volume` | ✅ | 出处卷次 |
| `--article` | ✅ | 出处篇名 |
| `--date` | ✅ | 中文日期 |
| `--year` | ✅ | 左下角竖排年份 |
| `--note` | ✅ | 段落注释 |
| `--output` | | 输出路径（默认 `mao_quote_wallpaper.png`） |
| `--font` | | 主字体路径（自动检测） |
| `--font-size` | | 字号（自动适配语录长度） |
| `--width` | | 宽度（默认 1920） |
| `--height` | | 高度（默认 1080） |
| `--set-wallpaper` | | 生成后自动设为桌面壁纸 |

---

## 在 AI 智能体中使用

本工具**不依赖任何特定 AI 平台**，任何能执行 Shell 命令的 AI 编程助手都能使用：

### Claude Code / Claude Desktop

进入项目目录后，直接使用 slash command：

```
/mao-wallpaper              # 随机语录壁纸
/mao-wallpaper 52           # 指定第 52 条
/mao-wallpaper --set-wallpaper  # 随机 + 设为桌面壁纸
```

或手动操作：

```
Generate a Mao Zedong quote wallpaper for my desktop:
1. Read quotes.json and pick a random entry
2. Run: python gen_wallpaper.py --quote "..." --volume "..." --article "..." --date "..." --year "..." --note "..." --set-wallpaper
3. Report back which quote you chose
```

### GitHub Copilot / Codex

```
@terminal python run.py --set-wallpaper
```

### Cursor / Windsurf

直接让 AI 执行：
```
Run `python run.py --set-wallpaper` to generate a daily Mao quote wallpaper.
```

### WorkBuddy

技能已内置安装，对话中说：
```
换一张毛选壁纸
```

### 通用提示词（适用所有 AI 助手）

```
You are a helpful assistant. I need a Mao Zedong quote desktop wallpaper.

Steps:
1. Read the file `quotes.json` in this project
2. Pick one quote randomly
3. Run this command (replace the placeholder values with the actual quote):
   python gen_wallpaper.py \
     --quote "THE_QUOTE_TEXT" \
     --volume "THE_VOLUME" \
     --article "THE_ARTICLE" \
     --date "THE_DATE" \
     --year "THE_YEAR" \
     --note "THE_ANNOTATION" \
     --output "mao_quote_wallpaper.png" \
     --set-wallpaper
4. Tell me which quote was selected
```

---

## 每日自动化

### Linux / macOS（crontab）

```bash
# 每天早上 8:00 更换壁纸
0 8 * * * cd /path/to/mao-quote-wallpaper && python run.py --set-wallpaper
```

### Windows（任务计划程序）

```powershell
# 创建每日任务
schtasks /create /tn "MaoWallpaper" /tr "python C:\path\to\mao-quote-wallpaper\run.py --set-wallpaper" /sc daily /st 08:00
```

### GitHub Actions（每日自动推送到仓库）

```yaml
name: Daily Mao Wallpaper
on:
  schedule:
    - cron: '0 0 * * *'  # UTC 00:00 = 北京时间 08:00
jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: pip install Pillow
      - run: python run.py --output wallpaper.png
      - uses: stefanzweifel/git-auto-commit-action@v4
        with:
          commit_message: "Daily wallpaper update"
```

---

## 项目结构

```
mao-quote-wallpaper/
├── gen_wallpaper.py    # 核心生成器（跨平台）
├── run.py              # 一键随机入口
├── quotes.json         # 100 条语录库（JSON，方便 AI 解析）
└── requirements.txt    # Pillow
```

---

## 自定义

### 添加自己的语录

编辑 `quotes.json`，按格式追加：

```json
{
  "quote": "为人民服务",
  "volume": "《毛泽东选集》第三卷",
  "article": "《为人民服务》",
  "date": "一九四四年九月八日",
  "year": "一九四四",
  "note": "毛泽东在张思德追悼会上的讲演..."
}
```

### 修改视觉风格

编辑 `gen_wallpaper.py` 顶部的颜色变量：

```python
BG_CENTER = (250, 245, 232)  # 中心底色
INK_TOP   = (200, 35, 35)    # 字色上
INK_BOT   = (110, 16, 16)    # 字色下
SEAL_RED  = (200, 30, 30)    # 印章红
```

---

## 语录库覆盖

| 来源 | 数量 | 主题 |
|------|:----:|------|
| 《毛选》第一卷（1925-1937） | ~25 条 | 阶级分析、武装斗争、调查研究 |
| 《毛选》第二卷（1937-1941） | ~20 条 | 持久战、统一战线、党建 |
| 《毛选》第三卷（1941-1945） | ~20 条 | 整风、文艺、群众路线 |
| 《毛选》第四卷（1945-1949） | ~15 条 | 解放战争、建国方略 |
| 《毛泽东文集》 | ~10 条 | 建设、外交、青年 |
| 《毛泽东诗词集》 | ~10 条 | 诗词名句 |

---

## License

MIT
