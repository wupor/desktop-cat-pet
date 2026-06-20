<div align="center">

# 🐱 Desktop Cat Pet — 桌面电子猫咪

<img src="https://img.shields.io/badge/Python-3.8%2B-blue?logo=python" alt="Python">
<img src="https://img.shields.io/badge/Platform-Windows%2010%2F11-lightgrey?logo=windows" alt="Platform">
<img src="https://img.shields.io/badge/License-MIT-green" alt="License">
<img src="https://img.shields.io/badge/dependencies-zero-brightgreen" alt="Zero Dependencies">
<img src="https://img.shields.io/badge/built%20with-Hermes%20Agent-8B5CF6?logo=robot" alt="Hermes Agent">

**一只会睡觉、散步、跟随鼠标、跳舞提醒你休息的桌面猫咪 🐱**

*An interactive desktop pet cat that sleeps, walks, follows your mouse, and dances to remind you to take breaks.*

> 🚀 **本项目由 [Hermes Agent](https://hermes-agent.nousresearch.com) 在 10 分钟内开发完成**
>
> *This project was built with [Hermes Agent](https://hermes-agent.nousresearch.com) in under 10 minutes*

[✨ 功能](#-功能-features) | [📸 截图](#-截图-screenshots) | [🚀 快速开始](#-快速开始-quick-start) | [🎮 交互方式](#-交互方式-interaction) | [⚙️ 自定义配置](#️-自定义配置-configuration) | [🧠 技术原理](#-技术原理-how-it-works) | [📦 项目结构](#-项目结构-project-structure)

</div>

---

## ✨ 功能 Features

| 状态 | 行为 | 触发条件 |
|------|------|---------|
| 😴 **睡觉 Sleep** | 蜷缩成一团，头顶飘出 Zzz 💤 | 空闲默认状态，猫咪会打盹 |
| 🚶 **散步 Walk** | 在桌面上随机走动，左顾右盼 | 每隔 8~20 秒自动触发一次 |
| 🦋 **跟随鼠标 Follow** | 鼠标靠近时 → 光标变成蝴蝶 → 猫咪跟着鼠标走 | 距离猫咪 160px 以内 |
| 💃 **跳舞提醒 Dance** | 猫咪蹦迪 🎵 + 音符飘动 ❤️ + 文字提醒 | **连续工作 30 分钟后**自动触发 |
| ⏸ **空闲 Idle** | 安静坐着，偶尔眨眼、摇尾巴 | 散步/跟随之间的过渡状态 |

### 核心亮点

- 🎯 **零依赖** — 只用 Python 标准库（tkinter + ctypes），装好 Python 就能跑
- 🪟 **完全穿透** — 全屏透明窗口，鼠标点击直接穿透到桌面，不影响正常操作
- 🧠 **智能检测** — 通过 Windows API 实时监控用户工作状态，适时提醒休息
- 🎨 **手绘橘猫** — 用 Canvas 图形组合绘制，每个状态都有专属动画帧
- 🦋 **蝴蝶光标** — 鼠标靠近时系统光标自动隐藏，替换为 🦋 蝴蝶

---

## 📸 截图 Screenshots

> *截图待补充 — 运行后按 `Win+PrintScreen` 截图并放入 `assets/` 目录*
>
> *Screenshots coming soon — take your own with `Win+PrintScreen` and add to `assets/`*

```
[😴 睡觉]          [🚶 散步]          [🦋 跟随]          [💃 跳舞提醒]
   ╱▔▔╲   z          /\_/\              /\_/\              ♪┏(･o･)┛♪
  ╱    ╲            ( o.o )     🦋←    (⊙_⊙)              ✧ ٩(◕‿◕｡)۶ ✧
 │ ● ● │            >  ^  <            >  ^  <  →🦋       ♫ ♪ ♫ ♪ ♫
  ﹀     ﹀
```

---

## 🚀 快速开始 Quick Start

### 系统要求 Requirements

- **Windows 10 / 11**（使用 Windows API 实现透明窗口和光标控制）
- **Python 3.8+**（自带 tkinter 即可，无需额外安装）

### 安装与运行 Install & Run

```bash
# 1. 克隆仓库（或直接下载 desktop_cat.py）
git clone https://github.com/YOUR_USERNAME/desktop-cat-pet.git
cd desktop-cat-pet

# 2. 直接运行！
python desktop_cat.py
```

> 💡 **无任何依赖需要安装** — tkinter 和 ctypes 都是 Python 标准库。
>
> 如果双击运行，确保 `.py` 文件关联到 Python，或在文件上右键 → 打开方式 → Python。

---

## 🎮 交互方式 Interaction

| 操作 | 效果 |
|------|------|
| 🖱️ **鼠标靠近猫咪** | 系统光标 → 🦋 蝴蝶，猫咪转身跟着你走 |
| 🖱️ **鼠标移开** | 猫咪切回空闲状态 → 自动睡觉/散步 |
| 🖱️ **右键点击猫咪** | 弹出菜单：**退出程序** / **立即跳舞** |
| ⌨️ **`Esc` 键** | 退出程序 |
| ⌨️ **`Ctrl+Q` / `Ctrl+C`** | 退出程序 |

### 行为逻辑

```
   ┌──────────┐     8~20秒无交互     ┌──────────┐
   │  睡觉 😴 │ ◄────────────────── │  空闲 😺 │
   └─────┬────┘                     └─────┬────┘
         │ 随机醒来                         │ 随机触发
         ▼                                  ▼
   ┌──────────┐                     ┌──────────┐
   │  散步 🚶 │                     │  跟随 🦋 │
   └──────────┘                     └──────────┘
         │ 到达目的地                        │ 鼠标移开
         └──────────────────►───────────────┘

   工作 30 分钟后 ⬇️
   ┌──────────┐
   │ 跳舞 💃  │  🎵 起来活动一下吧！
   └──────────┘  12秒后自动回到空闲
```

---

## ⚙️ 自定义配置 Configuration

打开 `desktop_cat.py`，在 `DesktopCat` 类的开头的参数区域可以调整：

```python
class DesktopCat:
    MOVE_SPEED = 4              # 跟随鼠标速度（像素/帧）🐢 → 🐇
    WALK_SPEED = 2              # 散步速度
    PROXIMITY_DIST = 160        # 触发跟随的距离（像素）
    STOP_DIST = 30              # 跟到离鼠标多远停下
    DANCE_DURATION = 12         # 跳舞提醒持续时间（秒）
    WORK_REMINDER_MINUTES = 30  # 工作多久后提醒（分钟）
    CAT_SIZE = 80               # 猫咪大小（缩放基数）
```

### 调参建议

- 🐢 想让猫咪走路更慢？ `WALK_SPEED = 1`
- 🐇 想让猫咪飞快跟着鼠标？ `MOVE_SPEED = 8`
- 😴 想让猫咪反应更灵敏？ `PROXIMITY_DIST = 250`
- 💃 工作1小时再提醒？ `WORK_REMINDER_MINUTES = 60`
- 🐱 想让猫咪变大/变小？ `CAT_SIZE = 120`（变大）或 `CAT_SIZE = 50`（变小）

### 多显示器

程序默认覆盖主屏幕。在多显示器环境下，可以修改窗口几何参数：

```python
# 在第 126 行附近修改窗口尺寸
screen_w = 1920   # 你的主屏宽度
screen_h = 1080   # 你的主屏高度
```

---

## 🧠 技术原理 How It Works

### 架构 Architecture

```
┌─────────────────────────────────────────────────┐
│                   主线程 tkinter                  │
│  ┌─────────────┐  ┌─────────────────────────┐    │
│  │ 全屏透明画布  │  │    状态机 (30 FPS 循环)   │    │
│  │ Canvas       │  │  sleep → idle → walk    │    │
│  │ bg=black     │  │  → follow → dance       │    │
│  │ transparent  │  │                         │    │
│  └─────────────┘  └─────────────────────────┘    │
│         ↓                                         │
│  ┌─────────────┐                                 │
│  │ 猫 CatRenderer │  ← 根据 state + frame 绘图     │
│  └─────────────┘                                 │
├─────────────────────────────────────────────────┤
│           ctypes (Windows API 调用)              │
│  ┌───────────┐ ┌──────────┐ ┌──────────────┐    │
│  │GetCursorPos│ │ShowCursor│ │GetLastInputInfo│   │
│  │鼠标位置轮询 │ │光标隐藏/ │ │ 用户空闲时间   │    │
│  │           │ │显示      │ │ 检测          │    │
│  └───────────┘ └──────────┘ └──────────────┘    │
├─────────────────────────────────────────────────┤
│         独立蝴蝶窗口 (Toplevel)                   │
│  ┌─────────────────────────────────────────┐    │
│  │ 🦋 Label, 透明, 置顶, 跟随鼠标位置        │    │
│  └─────────────────────────────────────────┘    │
└─────────────────────────────────────────────────┘
```

### 关键技术细节

| 技术 | 说明 |
|------|------|
| **透明窗口** | `tkinter` + `wm_attributes('-transparentcolor', 'black')` 让黑色像素透明 |
| **点击穿透** | `SetWindowLongW(hwnd, GWL_EXSTYLE, WS_EX_TRANSPARENT)` 让鼠标事件穿透窗口 |
| **光标替换** | 鼠标进入 160px 范围 → `ShowCursor(False)` 隐藏系统光标 + 弹出 🦋 窗口跟随鼠标 |
| **工作监控** | `GetLastInputInfo()` 获取系统级用户空闲时间，累计工作 30 分钟触发跳舞 |
| **动画系统** | 基于帧的状态机，30 FPS，每个状态有独立的绘图函数和帧计数 |
| **猫咪外观** | 纯 `Canvas` 图形组合（椭圆、多边形、弧线、线条），约 30 个图形元素构成猫咪 |

### 为什么用 tkinter 而不用游戏引擎？

| | tkinter ✅ | Pygame / Unity ❌ |
|--|-----------|------------------|
| **依赖** | Python 自带，零安装 | 需要安装额外库 |
| **透明窗口** | 原生支持 `transparentcolor` | 需要额外配置 |
| **系统集成** | 直接调用 Win32 API | 需要绕一层 |
| **文件大小** | 单文件 ~30KB | 至少数 MB |

---

## 📦 项目结构 Project Structure

```
desktop-cat-pet/
├── desktop_cat.py         # 🐱 主程序（单文件，所有逻辑都在这里）
├── README.md              # 📖 本说明文档
├── LICENSE                # 📄 MIT 开源许可证
├── .gitignore             # 🙈 Git 忽略规则
└── assets/                # 🖼️ 截图等资源
    └── .gitkeep
```

> 整个程序只有 **1 个 Python 文件**，约 900 行代码。麻雀虽小，五脏俱全！

---

## 🧪 已知限制 Known Limitations

- 🪟 **仅限 Windows** — 使用了 Win32 API（`ctypes.windll`），不支持 macOS/Linux
- 🖥️ **单显示器优化** — 默认覆盖主屏，多显示器需要手动调整尺寸
- 🎨 **临时文件** — 当前无配置文件，设置需修改源码（见 ⚙️ 配置部分）
- 🖱️ **蝴蝶窗口** — 使用独立 Toplevel 窗口实现蝴蝶，偶尔在高 DPI 缩放下有微小偏移

### 后续可能的功能 Ideas

- [ ] 📝 独立的 `config.yaml` 配置文件
- [ ] 🐧 macOS / Linux 支持（可改用 pyobjc / X11）
- [ ] 🎨 更多猫咪皮肤（黑猫、三花、布偶）
- [ ] 🍔 喂食功能（点击给猫咪加食物碗）
- [ ] 🗣️ 与猫咪对话（简单语音/文字交互）
- [ ] 🌙 夜间模式（猫咪自动进入深度睡眠）
- [ ] 📊 工作统计面板（显示今日工作时长、休息次数）

---

## 📄 许可证 License

本项目采用 **MIT License** — 完全开源，可自由使用、修改、分发。

---

<div align="center">

**🐱 喜欢这个项目吗？给它一个 ⭐ Star！**

---

*本项目由 [Hermes Agent](https://hermes-agent.nousresearch.com) 在 **不到 10 分钟** 内开发完成。*

*从需求描述 → 代码生成 → 调试优化 → GitHub 发布，全程 AI 驱动。*

*Hermes Agent 是一个开源的个人 AI 代理框架，由 [Nous Research](https://nousresearch.com) 开发。*

*Built with [Hermes Agent](https://hermes-agent.nousresearch.com) in under 10 minutes.*

*Made with ❤️ and 🐍 Python*

</div>
