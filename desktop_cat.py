#!/usr/bin/env python3
"""
Desktop Cat Pet 🐱 — 桌面电子猫咪

一只可爱的桌面互动猫咪：睡觉 😴 → 散步 🚶 → 跟随鼠标 🦋 → 跳舞提醒 💃

特点:
  - 零外部依赖（纯 Python 标准库：tkinter + ctypes）
  - Windows 全屏透明窗口，点击穿透，不影响正常操作
  - 智能工作监控，适时提醒休息
  - 手绘 Canvas 猫咪动画，四种状态流畅切换

作者: Hermes Agent
版本: 1.0.0
GitHub: https://github.com/wupor/desktop-cat-pet
许可证: MIT
"""

import tkinter as tk
import random
import math
import time
import threading
import ctypes
import ctypes.wintypes
from datetime import datetime

# ===== Windows API 常量与函数 =====
GWL_EXSTYLE = -20
WS_EX_LAYERED = 0x80000
WS_EX_TRANSPARENT = 0x20
WS_EX_TOOLWINDOW = 0x80

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32


class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [("cbSize", ctypes.wintypes.UINT),
                ("dwTime", ctypes.wintypes.DWORD)]


def get_cursor_pos():
    """获取鼠标在屏幕上的坐标"""
    pt = ctypes.wintypes.POINT()
    user32.GetCursorPos(ctypes.byref(pt))
    return pt.x, pt.y


def get_idle_seconds():
    """获取用户无操作的时间（秒）"""
    struct = LASTINPUTINFO()
    struct.cbSize = ctypes.sizeof(LASTINPUTINFO)
    user32.GetLastInputInfo(ctypes.byref(struct))
    millis = kernel32.GetTickCount() - struct.dwTime
    return millis / 1000.0


def set_clickthrough(hwnd):
    """让窗口可穿透（鼠标点击穿过窗口到桌面/其他应用）"""
    ex_style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
    ex_style |= WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_TOOLWINDOW
    user32.SetWindowLongW(hwnd, GWL_EXSTYLE, ex_style)


def hide_cursor():
    """隐藏系统鼠标指针"""
    user32.ShowCursor(False)


def show_cursor():
    """显示系统鼠标指针（多次调用需对应）"""
    # ShowCursor(True) 需要和 HideCursor 调用次数对应
    # 强制显示: 调用多次直到计数 >= 0
    while user32.ShowCursor(True) < 0:
        pass


# ===== 桌面猫咪主程序 =====
class DesktopCat:
    """桌面猫咪——主控类"""

    # ----- 颜色方案（橘猫） -----
    COLORS = {
        "body": "#F4A460",      # 身体 - 沙棕色
        "body_dark": "#D2691E", # 深色条纹
        "belly": "#FFDEAD",     # 肚子 - 浅米色
        "head": "#F4A460",      # 头部
        "ear_outer": "#F4A460", # 耳朵外面
        "ear_inner": "#FFB6C1", # 耳朵内部 - 粉色
        "eye": "#2E8B57",       # 眼睛 - 绿色
        "eye_white": "#FFFFFF", # 眼白
        "pupil": "#1A1A1A",     # 瞳孔
        "nose": "#FFB6C1",      # 鼻子 - 粉色
        "mouth": "#8B4513",     # 嘴巴
        "whisker": "#8B7355",   # 胡须
        "outline": "#8B4513",   # 轮廓线
        "bg": "#000000",        # 背景（透明色）
        "heart": "#FF4757",     # 爱心
        "note": "#FFD700",      # 音符 - 金色
        "z_color": "#87CEEB",   # Zzz - 天蓝色
        "paw_pad": "#FFB6C1",   # 肉垫
    }

    # ----- 行为参数 -----
    MOVE_SPEED = 4              # 跟随鼠标速度
    WALK_SPEED = 2              # 散步速度
    PROXIMITY_DIST = 160        # 触发跟随的距离（像素）
    STOP_DIST = 30              # 跟到鼠标附近停止的距离
    DANCE_DURATION = 12         # 跳舞提醒持续时间（秒）
    WORK_REMINDER_MINUTES = 30  # 工作多久后提醒（分钟）
    CAT_SIZE = 80               # 猫咪大小（缩放基数）

    def __init__(self):
        # ----- 窗口设置 -----
        self.root = tk.Tk()
        self.root.title("Desktop Cat 🐱")
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        self.SW = screen_w
        self.SH = screen_h

        # 全屏窗口，无边框，置顶
        self.root.geometry(f"{screen_w}x{screen_h}+0+0")
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)
        self.root.wm_attributes("-transparentcolor", "black")
        self.root.configure(bg="black")

        # ----- 画布 -----
        self.canvas = tk.Canvas(
            self.root,
            width=screen_w,
            height=screen_h,
            bg="black",
            highlightthickness=0
        )
        self.canvas.pack()

        # ----- 猫咪状态 -----
        self.x = screen_w // 2          # 猫咪位置
        self.y = screen_h // 2
        self.state = "sleep"            # sleep | idle | walk | follow | dance
        self.face_dir = 1               # 1=右, -1=左
        self.anim_frame = 0
        self.walk_target = None         # 散步目标 (x, y)
        self.sleep_timer = 0            # 入睡倒计时
        self.is_near_cat = False        # 鼠标是否在附近

        # ----- 动画控制 -----
        self.butterfly_id = None        # Canvas 上蝴蝶的 ID
        self.dance_end_time = 0         # 跳舞结束时间
        self.zzz_ids = []               # Zzz 文字ID列表
        self.music_ids = []             # 音符ID列表

        # ----- 工作监控 -----
        self.work_accumulated = 0.0     # 累计工作时间（秒）
        self.last_active_check = time.time()
        self.in_dance_reminder = False
        self.dance_reminder_shown = False  # 本次工作周期是否已提醒

        # ----- 蝴蝶悬浮层（独立窗口） -----
        self.butterfly_window = None
        self.butterfly_label = None
        self._setup_butterfly_window()

        # ----- 启动 -----
        self.root.after(500, self._apply_window_styles)
        self.root.after(1000, self._animate)
        self.root.after(2000, self._work_monitor)

        # 鼠标经过时也能检测
        self.cursor_was_hidden = False

        # ----- 退出热键 -----
        self.root.bind("<Escape>", lambda e: self._quit())
        self.root.bind("<Control-c>", lambda e: self._quit())
        self.root.bind("<Control-q>", lambda e: self._quit())

        # 右键菜单退出
        self.canvas.bind("<Button-3>", self._show_context_menu)
        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="退出程序 🐱", command=self._quit)
        self.menu.add_command(label="立即跳舞 💃", command=self.trigger_dance)

        # 窗口关闭时恢复光标
        self.root.protocol("WM_DELETE_WINDOW", self._quit)

    def _apply_window_styles(self):
        """应用窗口样式（延迟执行确保窗口已创建）"""
        hwnd = ctypes.windll.user32.GetParent(
            ctypes.windll.user32.GetParent(
                ctypes.c_int(self.canvas.winfo_id())
            )
        )
        if hwnd:
            set_clickthrough(hwnd)

    # ==================== 蝴蝶窗口 ====================
    def _setup_butterfly_window(self):
        """创建蝴蝶光标专用小窗口"""
        self.butterfly_window = tk.Toplevel(self.root)
        self.butterfly_window.overrideredirect(True)
        self.butterfly_window.wm_attributes("-topmost", True)
        self.butterfly_window.wm_attributes("-transparentcolor", "black")
        self.butterfly_window.configure(bg="black")
        self.butterfly_window.geometry("40x40+0+0")

        self.butterfly_label = tk.Label(
            self.butterfly_window,
            text="🦋",
            font=("Segoe UI Emoji", 28),
            bg="black",
            fg="#FF6B9D",
        )
        self.butterfly_label.pack()

        # 默认隐藏
        self.butterfly_window.withdraw()

        # 也让蝴蝶窗口点击穿透
        self.butterfly_window.after(500, self._make_butterfly_clickthrough)

    def _make_butterfly_clickthrough(self):
        hwnd = ctypes.windll.user32.GetParent(
            ctypes.c_int(self.butterfly_window.winfo_id())
        )
        if hwnd:
            set_clickthrough(hwnd)

    def _show_butterfly(self, mx, my):
        """在鼠标位置显示蝴蝶"""
        if self.butterfly_window:
            self.butterfly_window.geometry(f"40x40+{mx-20}+{my-20}")
            self.butterfly_window.deiconify()
            self.butterfly_window.lift()

    def _hide_butterfly(self):
        """隐藏蝴蝶"""
        if self.butterfly_window:
            self.butterfly_window.withdraw()

    # ==================== 猫咪绘制 ====================
    def _draw_cat(self, canvas, cx, cy, state, frame, face_dir):
        """
        在画布 (cx, cy) 位置绘制猫咪。
        state: sleep / idle / walk / follow / dance
        frame: 动画帧编号
        face_dir: 1=朝右, -1=朝左
        """
        s = self.CAT_SIZE / 80.0  # 缩放因子
        C = self.COLORS
        fd = face_dir

        # 清除旧绘制（只清除猫咪区域，不碰蝴蝶）
        canvas.delete("cat")

        def _oval(x1, y1, x2, y2, fill=None, outline=None, width=1, tags="cat"):
            return canvas.create_oval(
                cx + x1*s, cy + y1*s, cx + x2*s, cy + y2*s,
                fill=fill or C["body"], outline=outline or C["outline"],
                width=width, tags="cat"
            )

        def _poly(points, fill=None, outline=None, width=1, tags="cat"):
            pts = []
            for px, py in points:
                pts.append(cx + px * s)
                pts.append(cy + py * s)
            return canvas.create_polygon(
                *pts, fill=fill or C["body"],
                outline=outline or C["outline"],
                width=width, smooth=True, tags="cat"
            )

        def _line(x1, y1, x2, y2, color=None, width=1, tags="cat"):
            return canvas.create_line(
                cx + x1*s, cy + y1*s, cx + x2*s, cy + y2*s,
                fill=color or C["outline"], width=width, tags="cat"
            )

        def _arc(x1, y1, x2, y2, start, extent, fill=None, outline=None, width=1, style="arc", tags="cat"):
            return canvas.create_arc(
                cx + x1*s, cy + y1*s, cx + x2*s, cy + y2*s,
                start=start, extent=extent,
                fill=fill, outline=outline or C["outline"],
                width=width, style=style, tags="cat"
            )

        def _text(x, y, text, color, font_size=14, tags="cat"):
            return canvas.create_text(
                cx + x*s, cy + y*s, text=text,
                fill=color, font=("Segoe UI Emoji", font_size),
                tags="cat"
            )

        # 方向偏移：朝右为1，朝左为-1，对称绘制
        def px(x):
            """根据朝向翻转 X 坐标"""
            return x * fd

        # ===== 根据状态绘制 =====
        if state == "sleep":
            # --- 睡觉：蜷缩成一团 ---
            # 身体（大椭圆）
            _oval(-35, -20, 35, 30, fill=C["body"])

            # 肚子浅色区域
            _oval(-20, -10, 20, 20, fill=C["belly"])

            # 头（稍微露出）
            _oval(-25, -30, 25, 5, fill=C["head"])

            # 耳朵
            ear_lx = -16 + (1 if frame % 2 == 0 else 2)
            _poly([(ear_lx, -35), (ear_lx-10, -55), (ear_lx+8, -40)],
                  fill=C["ear_outer"])
            _poly([(ear_lx-3, -38), (ear_lx-6, -50), (ear_lx+4, -42)],
                  fill=C["ear_inner"], outline="")
            ear_rx = 16 - (1 if frame % 2 == 0 else 2)
            _poly([(ear_rx, -35), (ear_rx+10, -55), (ear_rx-8, -40)],
                  fill=C["ear_outer"])
            _poly([(ear_rx+3, -38), (ear_rx+6, -50), (ear_rx-4, -42)],
                  fill=C["ear_inner"], outline="")

            # 闭着的眼睛（弧形）
            _arc(-13, -22, -3, -12, 0, 180, width=2, style="arc")
            _arc(3, -22, 13, -12, 0, 180, width=2, style="arc")
            canvas.itemconfig(canvas.find_withtag("cat")[-1], fill=C["outline"])
            canvas.itemconfig(canvas.find_withtag("cat")[-2], fill=C["outline"])

            # 小鼻子
            _poly([(0, -12), (-3, -7), (3, -7)], fill=C["nose"], outline="")

            # 尾巴蜷在身上
            _arc(-30, 5, -5, 25, 180, 120, width=3, style="arc")

            # Zzz 浮动（根据帧变化）
            z_alpha = (frame % 30) / 15.0  # 0~2 周期
            if z_alpha <= 1:
                offset_y = -40 - z_alpha * 30
                size = 12 + z_alpha * 4
            else:
                offset_y = -40 - (2 - z_alpha) * 30
                size = 16 - (z_alpha - 1) * 4
            _text(20 + (frame % 15) * 0.5, offset_y, "💤", C["z_color"], 14)
            if frame % 30 < 20:
                _text(35, offset_y - 15, "z", C["z_color"], int(size))
            if frame % 30 < 12:
                _text(48, offset_y - 35, "Z", C["z_color"], int(size) + 4)
            if frame % 30 < 6:
                _text(62, offset_y - 55, "Z", C["z_color"], int(size) + 8)

        elif state in ("idle", "walk", "follow"):
            # --- 坐着/走路/跟随 ---
            walk_bob = 0
            if state in ("walk", "follow"):
                # 走路时身体上下微微弹动
                walk_bob = math.sin(frame * 0.4) * 3

            # 尾巴
            tail_wag = math.sin(frame * 0.1) * 8 if state == "idle" else math.sin(frame * 0.3) * 5
            _arc(-30, 15, -15, 35 + walk_bob, 160 + tail_wag, 80,
                 width=3, style="arc")

            # 身体
            body_top = -15 + walk_bob
            body_bot = 35 + walk_bob
            _oval(-30, body_top, 30, body_bot)

            # 肚子
            _oval(-18, body_top + 20, 18, body_bot - 2, fill=C["belly"])

            # 后腿
            leg_offset = math.sin(frame * 0.4) * 5 if state in ("walk", "follow") else 0
            _oval(-28, 25 + walk_bob, -18, 38 + walk_bob, fill=C["body"])
            _oval(18 + leg_offset, 25 + walk_bob, 28 + leg_offset * 2, 38 + walk_bob, fill=C["body"])

            # 前腿（走路时交替）
            leg_swing = 0
            if state in ("walk", "follow"):
                leg_swing = math.sin(frame * 0.3) * 6
            _oval(-22 + leg_swing, body_bot - 8, -12 + leg_swing, body_bot + 5,
                  fill=C["body"])
            _oval(12 - leg_swing, body_bot - 8, 22 - leg_swing, body_bot + 5,
                  fill=C["body"])

            # 头部
            head_y = -18 + walk_bob
            _oval(-22, head_y - 22, 22, head_y + 10)

            # 耳朵
            _poly([(-14, head_y-22), (-22, head_y-45), (-6, head_y-28)],
                  fill=C["ear_outer"])
            _poly([(-12, head_y-26), (-18, head_y-40), (-8, head_y-30)],
                  fill=C["ear_inner"], outline="")
            _poly([(14, head_y-22), (22, head_y-45), (6, head_y-28)],
                  fill=C["ear_outer"])
            _poly([(12, head_y-26), (18, head_y-40), (8, head_y-30)],
                  fill=C["ear_inner"], outline="")

            # 眼睛
            if state == "idle" and frame % 120 > 115:
                # 眨眼
                _line(px(-10), head_y-8, px(-4), head_y-8, width=2)
                _line(px(4), head_y-8, px(10), head_y-8, width=2)
            else:
                # 眼睛方向（跟随鼠标时看屏幕中心方向，平时随便看）
                if state == "follow":
                    eye_x_off = px(2)
                else:
                    eye_x_off = px(1 if frame % 40 < 20 else -1)

                # 眼白
                _oval(px(-12) + eye_x_off, head_y-14, px(-4) + eye_x_off, head_y-4,
                      fill=C["eye_white"], outline="")
                _oval(px(4) + eye_x_off, head_y-14, px(12) + eye_x_off, head_y-4,
                      fill=C["eye_white"], outline="")
                # 瞳孔
                pupil_off = px(3) if state == "follow" else px(1)
                _oval(px(-10) + pupil_off, head_y-12, px(-6) + pupil_off, head_y-7,
                      fill=C["pupil"], outline="")
                _oval(px(6) + pupil_off, head_y-12, px(10) + pupil_off, head_y-7,
                      fill=C["pupil"], outline="")
                # 高光
                _oval(px(-10) + pupil_off + 1, head_y-11, px(-8) + pupil_off + 1, head_y-9,
                      fill="white", outline="")
                _oval(px(6) + pupil_off + 1, head_y-11, px(8) + pupil_off + 1, head_y-9,
                      fill="white", outline="")

            # 鼻子
            _poly([(0, head_y-4), (-4, head_y+1), (4, head_y+1)],
                  fill=C["nose"], outline="")

            # 嘴巴
            _arc(px(-6), head_y, px(-1), head_y+5, 0, 180, width=1.5, style="arc")
            _arc(px(1), head_y, px(6), head_y+5, 0, 180, width=1.5, style="arc")

            # 胡须
            for i in range(3):
                y_off = i * 3
                _line(px(-22), head_y-1+y_off, px(-35), head_y-6+y_off*1.5,
                      color=C["whisker"], width=1)
                _line(px(22), head_y-1+y_off, px(35), head_y-6+y_off*1.5,
                      color=C["whisker"], width=1)

        elif state == "dance":
            # --- 跳舞 ---
            bounce = math.sin(frame * 0.5) * 10
            arm_swing = math.sin(frame * 0.7) * 20

            # 尾巴（兴奋摇动）
            _arc(-30, 10, -15, 35, 150 + math.sin(frame * 0.8) * 30, 80,
                 width=3, style="arc")

            # 身体（伴随弹跳上下动）
            body_top = -15 - bounce
            body_bot = 30 - bounce
            _oval(-28, body_top, 28, body_bot)

            # 肚子
            _oval(-16, body_top + 18, 16, body_bot - 2, fill=C["belly"])

            # 腿（跳起来时缩起）
            _oval(-25, 25 - bounce, -15, 38 - bounce, fill=C["body"])
            _oval(15, 25 - bounce, 25, 38 - bounce, fill=C["body"])

            # 前爪（举起来挥舞！）
            _oval(-25 + arm_swing, body_top - 15, -15 + arm_swing, body_top,
                  fill=C["body"])
            _oval(15 - arm_swing, body_top - 15, 25 - arm_swing, body_top,
                  fill=C["body"])
            # 肉垫
            _oval(-20 + arm_swing, body_top - 8, -17 + arm_swing, body_top - 4,
                  fill=C["paw_pad"], outline="")
            _oval(17 - arm_swing, body_top - 8, 20 - arm_swing, body_top - 4,
                  fill=C["paw_pad"], outline="")

            # 头部
            head_y = -18 - bounce
            _oval(-22, head_y - 22, 22, head_y + 8)

            # 耳朵（兴奋竖起）
            _poly([(-14, head_y-22), (-24, head_y-48), (-6, head_y-30)],
                  fill=C["ear_outer"])
            _poly([(-12, head_y-26), (-20, head_y-43), (-8, head_y-32)],
                  fill=C["ear_inner"], outline="")
            _poly([(14, head_y-22), (24, head_y-48), (6, head_y-30)],
                  fill=C["ear_outer"])
            _poly([(12, head_y-26), (20, head_y-43), (8, head_y-32)],
                  fill=C["ear_inner"], outline="")

            # 眼睛（兴奋发亮）
            _oval(px(-12), head_y-15, px(-4), head_y-5,
                  fill=C["eye_white"], outline="")
            _oval(px(4), head_y-15, px(12), head_y-5,
                  fill=C["eye_white"], outline="")
            _oval(px(-9), head_y-12, px(-7), head_y-8,
                  fill=C["pupil"], outline="")
            _oval(px(7), head_y-12, px(9), head_y-8,
                  fill=C["pupil"], outline="")
            _oval(px(-8), head_y-11, px(-7), head_y-9,
                  fill="white", outline="")
            _oval(px(8), head_y-11, px(9), head_y-9,
                  fill="white", outline="")

            # 开心的嘴巴
            _arc(px(-8), head_y-1, px(8), head_y+10, 180, 180,
                 fill=C["belly"], style="chord")

            # 鼻子
            _poly([(0, head_y-4), (-3, head_y), (3, head_y)],
                  fill=C["nose"], outline="")

            # 胡须（跳舞时兴奋翘起）
            for i in range(3):
                y_off = i * 3
                _line(px(-22), head_y-1+y_off, px(-38), head_y-12+y_off*1.5,
                      color=C["whisker"], width=1.5)
                _line(px(22), head_y-1+y_off, px(38), head_y-12+y_off*1.5,
                      color=C["whisker"], width=1.5)

            # 音符和星星（跳舞时出现）
            note_positions = [
                (-45, -50), (40, -55), (-50, -30), (50, -35),
                (-35, -60), (35, -65),
            ]
            note_idx = frame % len(note_positions)
            for i in range(min(4, len(note_positions))):
                idx = (note_idx + i) % len(note_positions)
                nx, ny = note_positions[idx]
                # 音符闪烁
                if (frame + i * 5) % 15 < 10:
                    note_char = random.choice(["♪", "♫", "♩", "🎵", "✨"])
                    _text(nx, ny + math.sin(frame*0.1 + i) * 3,
                          note_char, C["note"], 16)

            # 爱心（偶尔飘出）
            if frame % 20 < 5:
                _text(random.randint(-30, 30), -55 - random.randint(0, 20),
                      "❤️", C["heart"], 14)

    # ==================== 动画主循环 ====================
    def _animate(self):
        """每帧更新——约 30 FPS"""
        fps = 30
        delay = 1000 // fps

        # 获取鼠标位置
        mx, my = get_cursor_pos()

        # 计算猫咪到鼠标的距离
        dx = mx - self.x
        dy = my - self.y
        dist = math.sqrt(dx * dx + dy * dy)

        # ---- 状态机 ----
        is_near = dist < self.PROXIMITY_DIST

        if is_near:
            # === 鼠标在附近：跟随模式 ===
            if not self.is_near_cat:
                self.is_near_cat = True
                # 切换到跟随状态
                if self.state != "dance":
                    self.state = "follow"
                hide_cursor()
                self.cursor_was_hidden = True

            # 显示蝴蝶
            self._show_butterfly(mx, my)

            # 如果不在跳舞，就跟随鼠标
            if self.state != "dance":
                self.state = "follow"
                if dist > self.STOP_DIST:
                    move = self.MOVE_SPEED * min(dist / 100, 1.2)
                    self.x += (dx / max(dist, 1)) * move
                    self.y += (dy / max(dist, 1)) * move
                    # 面向鼠标方向
                    self.face_dir = 1 if dx > 0 else -1
                self.anim_frame += 1
            else:
                self.anim_frame += 2  # 跳舞时动画加快

            # 边界限制
            self.x = max(self.CAT_SIZE, min(self.SW - self.CAT_SIZE, self.x))
            self.y = max(self.CAT_SIZE, min(self.SH - self.CAT_SIZE, self.y))

        else:
            # === 鼠标不在附近：正常行为 ===
            if self.is_near_cat:
                self.is_near_cat = False
                self._hide_butterfly()
                if self.cursor_was_hidden:
                    show_cursor()
                    self.cursor_was_hidden = False
                # 切回空闲
                if self.state != "dance":
                    self.state = "idle"
                    self._schedule_walk()

            if self.state == "follow":
                self.state = "idle"
                self._schedule_walk()

            self._hide_butterfly()

            if self.state == "sleep":
                # 睡觉——动画继续
                self.anim_frame += 1

            elif self.state == "idle":
                # 空闲——执行定时行为
                self.anim_frame += 1

            elif self.state == "walk":
                # 散步——向目标移动
                if self.walk_target:
                    tx, ty = self.walk_target
                    wx = tx - self.x
                    wy = ty - self.y
                    wd = math.sqrt(wx*wx + wy*wy)
                    if wd > 5:
                        move = self.WALK_SPEED * min(wd / 50, 1.5)
                        self.x += (wx / max(wd, 1)) * move
                        self.y += (wy / max(wd, 1)) * move
                        self.face_dir = 1 if wx > 0 else -1
                        self.anim_frame += 1
                    else:
                        # 到达目标，切回空闲
                        self.state = "idle"
                        self.walk_target = None
                        self._schedule_walk()

            elif self.state == "dance":
                # 跳舞
                self.anim_frame += 2
                if time.time() >= self.dance_end_time:
                    self.state = "idle"
                    self.in_dance_reminder = False
                    self._schedule_walk()
                    # 恢复光标（如果之前隐藏了）
                    if self.cursor_was_hidden:
                        show_cursor()
                        self.cursor_was_hidden = False
                        self.is_near_cat = False
                        self._hide_butterfly()

        # 绘制猫咪
        self.canvas.delete("cat")
        self._draw_cat(
            self.canvas,
            int(self.x), int(self.y),
            self.state, self.anim_frame, self.face_dir
        )

        # 继续动画循环
        self.root.after(delay, self._animate)

    def _schedule_walk(self):
        """安排一次随机散步"""
        if self.state not in ("idle",):
            return
        delay_ms = random.randint(8000, 20000)  # 8~20秒后散步
        self.root.after(delay_ms, self._start_walk)

    def _start_walk(self):
        """开始随机散步"""
        if self.state in ("idle",) and not self.is_near_cat and not self.in_dance_reminder:
            self.state = "walk"
            margin = 100
            self.walk_target = (
                random.randint(margin, self.SW - margin),
                random.randint(margin, self.SH - margin)
            )
            # 如果一切顺利，散步后自动回到 idle

    def trigger_dance(self):
        """触发跳舞提醒"""
        if self.in_dance_reminder:
            return
        self.in_dance_reminder = True
        self.state = "dance"
        self.anim_frame = 0
        self.dance_end_time = time.time() + self.DANCE_DURATION

        # 如果鼠标正在附近，先恢复光标
        if self.cursor_was_hidden:
            show_cursor()
            self.cursor_was_hidden = False
            self._hide_butterfly()

        # 显示提醒文字
        msg_id = self.canvas.create_text(
            self.SW // 2, 100,
            text="😺 工作好久了，起来休息一下吧！🚶‍♂️💪",
            fill="#FFD700",
            font=("Microsoft YaHei", 28, "bold"),
            tags="reminder"
        )
        sub_id = self.canvas.create_text(
            self.SW // 2, 140,
            text="站起来走一走，喝杯水，看看窗外 🌿",
            fill="#FFA500",
            font=("Microsoft YaHei", 18),
            tags="reminder"
        )
        # 闪烁效果：3秒后开始淡出
        self.root.after(3000, lambda: self._fade_reminder(5))

    def _fade_reminder(self, steps):
        """淡出提醒文字"""
        items = self.canvas.find_withtag("reminder")
        if not items:
            return
        # 每隔 0.3 秒降低一次透明度（实际上是通过颜色变暗模拟）
        if steps > 0:
            try:
                for item in items:
                    current = self.canvas.itemcget(item, "fill")
                    # 变暗：简单地改为更暗的颜色
                    if "FFD700" in current:
                        self.canvas.itemconfig(item, fill="#B8860B")
                    elif "B8860B" in current:
                        self.canvas.itemconfig(item, fill="#8B6914")
                    elif "FFA500" in current:
                        self.canvas.itemconfig(item, fill="#CC8400")
                    elif "CC8400" in current:
                        self.canvas.itemconfig(item, fill="#996300")
                self.root.after(300, lambda: self._fade_reminder(steps - 1))
            except tk.TclError:
                pass
        else:
            self.canvas.delete("reminder")

    # ==================== 工作监控 ====================
    def _work_monitor(self):
        """监控工作时间，每 10 秒检查一次"""
        idle_sec = get_idle_seconds()

        if idle_sec < 300:  # 5分钟内无操作算作"工作中"
            self.work_accumulated += 10  # 每10秒累加
        else:
            # 长时间没操作，重置计时（人离开了）
            if self.work_accumulated > 60:
                pass  # 保留已累计的时间

        # 检查是否达到提醒阈值
        if (self.work_accumulated >= self.WORK_REMINDER_MINUTES * 60
                and not self.dance_reminder_shown
                and not self.in_dance_reminder):
            self.dance_reminder_shown = True
            self.trigger_dance()
            # 提醒后将累计时间重置
            self.root.after(int(self.DANCE_DURATION * 1000) + 2000,
                            self._reset_work_timer)

        # 每10秒检查一次
        self.root.after(10000, self._work_monitor)

    def _reset_work_timer(self):
        """重置工作计时（跳舞结束后调用）"""
        self.work_accumulated = 0
        self.dance_reminder_shown = False

    # ==================== 退出与菜单 ====================
    def _quit(self):
        """安全退出程序"""
        self.in_dance_reminder = False  # 防止跳舞线程继续
        # 恢复光标
        show_cursor()
        self._hide_butterfly()
        try:
            self.root.destroy()
        except tk.TclError:
            pass

    def _show_context_menu(self, event):
        """显示右键菜单"""
        try:
            self.menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu.grab_release()

    # ==================== 启动 ====================
    def run(self):
        """启动程序"""
        self.root.mainloop()


# ===== 程序入口 =====
if __name__ == "__main__":
    print("🐱 桌面电子猫咪启动啦！")
    print("  • 平时会睡觉和散步")
    print("  • 鼠标靠近 → 变成蝴蝶 → 猫咪跟着你走 🦋")
    print(f"  • 工作 {DesktopCat.WORK_REMINDER_MINUTES} 分钟后会跳舞提醒休息 💃")
    print("  • 按 Ctrl+C 在终端退出程序")
    print()
    cat = DesktopCat()
    cat.run()
