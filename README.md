# 毛选壁纸 · Mao Quote Wallpaper — AI Skill

每天一句毛泽东语录，生成书法艺术桌面壁纸。**兼容所有 AI 编程助手**（Claude Code / Copilot / Cursor / Windsurf / 开源 LLM 工具）。

> **100 条精选语录**，涵盖《毛泽东选集》全四卷 +《毛泽东文集》+《毛泽东诗词集》。

![Preview](preview.png)

---

## 快速开始（人类用）

```bash
pip install Pillow
python run.py --set-wallpaper   # 随机语录 + 设为桌面壁纸
python run.py --list            # 列出全部 100 条
python run.py 52                # 指定第 52 条
```

---

## 在 AI 工具中使用

### Claude Code

进入项目目录后，直接使用 slash command：

```
/mao-wallpaper              # 随机语录壁纸
/mao-wallpaper 52           # 指定第 52 条
/mao-wallpaper --set-wallpaper  # 随机 + 设为桌面壁纸
```

### GitHub Copilot / Codex

```copilot
@terminal python run.py --set-wallpaper
```

### Cursor / Windsurf

```
Run `python run.py --set-wallpaper` to generate a daily Mao quote wallpaper.
```

### 任意 AI 助手（通用提示词模板）

复制以下内容到任何 AI 对话中：

```
You are a helpful assistant. I need a Mao Zedong quote desktop wallpaper.

Steps:
1. Read the file `quotes.json` in this project
2. Pick one quote randomly (avoid repeating the same quote as last time)
3. Run this command (replace the placeholder values with the actual quote):
   python gen_wallpaper.py \
     --quote "THE_QUOTE_TEXT" \
     --volume "THE_VOLUME" \
     --article "THE_ARTICLE" \
     --date "THE_DATE" \
     --vertical-year "THE_YEAR" \
     --note "THE_ANNOTATION" \
     --output "mao_quote_wallpaper.png" \
     --set-wallpaper
4. Tell me which quote was selected
```

---

## 精确控制

```bash
python gen_wallpaper.py \
  --quote "星星之火，可以燎原" \
  --volume "《毛泽东选集》第一卷" \
  --article "《星星之火，可以燎原》" \
  --date "一九三〇年一月五日" \
  --vertical-year "一九三〇" \
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
| `--vertical-year` / `--year` | ✅ | 左下角竖排年份（两个参数名都支持） |
| `--note` | ✅ | 段落注释 |
| `--output` | | 输出路径（默认 `mao_quote_wallpaper.png`） |
| `--font` | | 主字体路径（自动检测） |
| `--font-size` | | 字号（自动适配语录长度） |
| `--width` | | 宽度（默认 1920） |
| `--height` | | 高度（默认 1080） |
| `--set-wallpaper` | | 生成后自动设为桌面壁纸 |

---

## 设计规范

| 元素 | 说明 |
|------|------|
| 分辨率 | 1920×1080 |
| 背景 | 羊皮纸暖色径向渐变 + 纸质纹理 |
| 主语录 | 朱砂红渐变（上→下：亮红→暗红），暖金色光晕 |
| 主字体 | 汉仪黄科行书简（自动检测，回退华文行楷 / 楷体） |
| 光晕 | 中心暖金色辉光，半径 550px |
| 印章 | 右上角红色「毛选」圆角方框 |
| 装饰 | 左上「毛主席语录」标签，左下竖排年份 |
| 出处 | 右下角：卷次、篇名、日期、段落注释 |
| 暗角 | 温暖色调边缘加深 |

---

## 项目结构

```
maoxuan-wallpaper.skill/
├── .claude/
│   └── settings.json    ← Claude Code slash command 定义
├── gen_wallpaper.py     ← 核心生成器（跨平台，支持 --set-wallpaper）
├── run.py               ← 一键随机入口
├── quotes.json          ← 100 条语录库（JSON，方便 AI 解析）
├── hanyihuangkexingshujian.ttf ← 汉仪黄科行书简字体
├── AGENT.md             ← AI 智能体接手指南
├── README.md            ← 本文件
└── requirements.txt     ← Pillow>=9.0.0
```

---

## 每日自动化

### Linux / macOS（crontab）

```bash
# 每天早上 8:00 更换壁纸
0 8 * * * cd /path/to/maoxuan-wallpaper.skill && python run.py --set-wallpaper
```

### Windows（任务计划程序）

```powershell
schtasks /create /tn "MaoWallpaper" /tr "python C:\path\to\maoxuan-wallpaper.skill\run.py --set-wallpaper" /sc daily /st 08:00
```

### GitHub Actions

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

## 自定义视觉

编辑 `gen_wallpaper.py` 中的颜色变量：

```python
BG_CENTER = (250, 245, 232)  # 中心底色（羊皮纸暖色）
INK_TOP   = (200, 35, 35)    # 字色上（朱砂红）
INK_BOT   = (110, 16, 16)    # 字色下（深红）
SEAL_RED  = (200, 30, 30)    # 印章红
```

## 添加语录

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
