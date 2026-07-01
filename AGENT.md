# 毛选壁纸项目 — AI 智能体接手指南

## 项目概述

每天随机选取一句毛泽东语录，生成书法艺术风格桌面壁纸（1920×1080 PNG）。
语录库 100 条，覆盖《毛选》四卷 + 文集 + 诗词。

## 文件结构

```
E:\20260701毛选语录壁纸\
├── AGENT.md             ← 本文件（AI 接手说明）
├── gen_wallpaper.py     ← 核心生成器（跨平台）
├── run.py               ← 一键随机入口
├── quotes.json          ← 100 条语录库（JSON）
├── requirements.txt     ← Pillow>=9.0.0
├── hanyihuangkexingshujian.ttf ← 汉仪黄科行书简字体
├── README.md            ← 跨平台使用说明
├── .claude\
│   └── settings.json    ← Skill 定义（/mao-wallpaper 命令）
└── .gitignore
```

## 快速开始（AI 智能体用）

### 1. 安装依赖

```bash
pip install Pillow
```

### 2. 随机生成一张壁纸

```bash
python run.py --output mao_wallpaper.png
```

### 3. 随机生成 + 设为桌面壁纸

```bash
python run.py --set-wallpaper
```

### 4. 指定某条语录

```bash
python run.py 52 --output wallpaper.png
```

### 5. 列出全部 100 条

```bash
python run.py --list
```

## 精确控制（传入任意语录参数）

```bash
python gen_wallpaper.py \
  --quote "星星之火，可以燎原" \
  --volume "《毛泽东选集》第一卷" \
  --article "《星星之火，可以燎原》" \
  --date "一九三〇年一月五日" \
  --vertical-year "一九三〇" \
  --note "毛泽东致林彪的复信..." \
  --output wallpaper.png \
  --set-wallpaper
```

## 语录库格式（quotes.json）

每条语录结构如下：

```json
{
  "quote": "星星之火，可以燎原",
  "volume": "《毛泽东选集》第一卷",
  "article": "《星星之火，可以燎原》",
  "date": "一九三〇年一月五日",
  "year": "一九三〇",
  "note": "毛泽东致林彪的复信。指出革命力量虽处微弱..."
}
```

添加新语录：在 JSON 数组末尾按同样格式追加即可。

## 字体说明

- **主书法字体**：项目目录下的 `hanyihuangkexingshujian.ttf`（汉仪黄科行书简）
  - `detect_calligraphy_font()` 优先检测同目录下的该字体文件，存在即直接使用
  - 如文件缺失，则回退到系统目录搜索：汉仪黄科行书简 → 华文行楷 → 系统楷体
- Windows：通常自带华文行楷，无需额外安装
- macOS：需要安装任意楷体/行书字体
- Linux：`sudo apt install fonts-noto-cjk`

可以通过 `--font` 参数手动指定其他字体路径覆盖。

## 壁纸设置（跨平台）

- **Windows**：通过 Win32 API `SystemParametersInfoW` 直接设置
- **macOS**：通过 AppleScript 设置
- **Linux**：依次尝试 GNOME / KDE / XFCE / feh

`gen_wallpaper.py` 和 `run.py` 都支持 `--set-wallpaper` 参数。

## 跨平台 AI 支持

本工具可在以下 AI 平台使用：

| 平台 | 方式 |
|------|------|
| **Claude Code** | 进入项目目录，输入 `/mao-wallpaper` |
| **GitHub Copilot / Codex** | `@terminal python run.py --set-wallpaper` |
| **Cursor / Windsurf** | 让 AI 执行 `python run.py --set-wallpaper` |
| **任意 AI 助手** | 使用 README.md 中的通用提示词模板 |

## 每日自动化

### Windows 任务计划程序

```powershell
schtasks /create /tn "MaoWallpaper" /tr "python E:\20260701毛选语录壁纸\run.py --set-wallpaper" /sc daily /st 08:00
```

### crontab (Linux/macOS)

```bash
0 8 * * * cd /path/to/20260701毛选语录壁纸 && python run.py --set-wallpaper
```

### GitHub Actions

参考 README.md 中的配置，每日 UTC 00:00 自动生成并推送。

## 代码说明

| 文件 | 用途 | 关键函数/逻辑 |
|------|------|-------------|
| `gen_wallpaper.py` | 核心生成 | `generate()` — 6 步渲染：背景渐变、纹理、辉光、颗粒、书法文字、出处注释 |
| `run.py` | 随机入口 | 读 `quotes.json` → 随机/指定 pick → 调用 `gen_wallpaper.py` |
| `quotes.json` | 语录库 | 100 条，来源标注卷次和篇名 |

### gen_wallpaper.py 关键区域

- **颜色变量**（第 258-268 行附近）：`BG_CENTER`、`INK_TOP`、`SEAL_RED` 等，改视觉风格从这里入手
- **字号自适应**（`calc_font_size` 函数）：根据语录字数自动计算，6 字=220px，30+ 字=60px
- **竖向年份**（左下角）：竖排中文年份，楷体 15px
- **印章**：右上角「毛选」二字红色圆角方框

## 已知限制

1. 字体检测依赖系统字体目录遍历，每次运行都会遍历，速度较慢
2. 中文竖排仅支持左下角年份，大规模竖排语录暂未实现
3. 壁纸设置后需手动刷新桌面才能立即看到（部分系统）

## 自定义视觉

编辑 `gen_wallpaper.py` 中的颜色常量组即可改变整体色调：

```python
BG_CENTER = (250, 245, 232)  # 中心底色（羊皮纸暖色）
INK_TOP   = (200, 35, 35)    # 字色上（朱砂红）
INK_BOT   = (110, 16, 16)    # 字色下（深红）
SEAL_RED  = (200, 30, 30)    # 印章红
```

## GitHub

- 仓库：https://github.com/penapinner/maoxuan-wallpaper.skill
- 本地 Git remote：已配置（origin → penapinner/maoxuan-wallpaper.skill）
- 如无法推送：用 GitHub 网页端 "Upload files" 上传

## 常见任务（AI 接手后可能被要求做的）

1. **"换一张壁纸"** → `python run.py --set-wallpaper`
2. **"加一条语录"** → 编辑 `quotes.json` 追加
3. **"改颜色风格"** → 编辑 `gen_wallpaper.py` 顶部颜色变量
4. **"设每日自动换"** → 创建系统定时任务（见上方自动化部分）
5. **"推送 GitHub"** → 先 commit 再 push，或网页上传
