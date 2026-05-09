#!/usr/bin/env python3
"""MVP结算动画 — 纯终端渲染，零外部依赖，直接在 VS Code 终端播放。"""
import sys, os, time, math, random, shutil

# ── ANSI 工具 ──────────────────────────────────────────────
CSI = '\033['

def hide_cursor(): sys.stdout.write(CSI + '?25l')
def show_cursor(): sys.stdout.write(CSI + '?25h')
def goto(x, y):   sys.stdout.write(f'{CSI}{y};{x}H')
def clear():      sys.stdout.write(CSI + '2J' + CSI + 'H')
def bg_rgb(r, g, b): return f'{CSI}48;2;{r};{g};{b}m'
def fg_rgb(r, g, b): return f'{CSI}38;2;{r};{g};{b}m'
def reset():      return CSI + '0m'
def flush():      sys.stdout.flush()

# ── 终端尺寸 ────────────────────────────────────────────────
def term_size():
    try:
        cols, rows = shutil.get_terminal_size()
        return max(cols, 40), max(rows, 20)
    except Exception:
        return 80, 24

# ── 像素字体 (5x7, S/A/B 评级) ─────────────────────────────
# 每字符 5 列 x 7 行, 1=亮, 0=暗
FONT_S = [
    [0,1,1,1,0],
    [1,1,0,0,0],
    [0,1,1,1,0],
    [0,0,0,1,1],
    [0,1,1,1,0],
    [0,0,0,0,0],
    [0,0,0,0,0],
]

FONT_A = [
    [0,1,1,1,0],
    [1,0,0,0,1],
    [1,1,1,1,1],
    [1,0,0,0,1],
    [1,0,0,0,1],
    [0,0,0,0,0],
    [0,0,0,0,0],
]

FONT_B = [
    [1,1,1,1,0],
    [1,0,0,0,1],
    [1,1,1,1,0],
    [1,0,0,0,1],
    [1,1,1,1,0],
    [0,0,0,0,0],
    [0,0,0,0,0],
]

FONTS = {'S': FONT_S, 'A': FONT_A, 'B': FONT_B}

# ── 粒子系统 ────────────────────────────────────────────────
class Particle:
    def __init__(self, cx, cy):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2.0, 8.0)
        self.x = cx
        self.y = cy
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = random.uniform(0.8, 1.5)
        self.age = 0
        hue = random.uniform(0, 1)
        self.r, self.g, self.b = hsv_to_rgb(hue, 0.9, 1.0)

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.age += dt
        return self.age < self.life

def hsv_to_rgb(h, s, v):
    """h:0-1, s:0-1, v:0-1 → (r,g,b) 0-255"""
    if s == 0:
        return (int(v*255),)*3
    h = h * 6
    i = int(h)
    f = h - i
    p, q, t = v*(1-s), v*(1-f*s), v*(1-(1-f)*s)
    rgb = [(v,q,p), (t,v,p), (p,v,t), (p,q,v), (t,p,v), (v,p,q)][i % 6]
    return tuple(int(c*255) for c in rgb)

# ── 主动画 ──────────────────────────────────────────────────
def animate(rating='S', project_name='未知任务', lines=173, bugs=0, files=1):
    cols, rows = term_size()
    cx, cy = cols // 2, rows // 2

    particles = []
    starfield = [(random.randint(0, cols-1), random.randint(0, rows-1),
                   random.uniform(0.3, 1.0)) for _ in range(60)]

    fps = 30
    frame_duration = 1.0 / fps
    total_time = 0
    max_time = 6.0

    # 配色
    GOLD = (255, 215, 0)
    WHITE = (255, 255, 255)
    DIM = (60, 60, 80)
    BG = (10, 10, 20)

    try:
        hide_cursor()
        clear()

        while total_time < max_time:
            frame_start = time.time()
            dt = min(frame_duration, 0.1)

            # ── 粒子更新 ──
            if total_time < 2.0 and random.random() < 0.6:
                for _ in range(random.randint(1, 4)):
                    particles.append(Particle(cx, cy))

            alive = []
            for p in particles:
                if p.update(dt):
                    alive.append(p)
            particles[:] = alive

            # ── 渲染 ──
            # 背景
            goto(1, 1)
            out_lines = []
            for py in range(1, rows + 1):
                line_chars = []
                for px in range(1, cols + 1):
                    line_chars.append(bg_rgb(*BG) + '  ')
                out_lines.append(''.join(line_chars))
            sys.stdout.write(''.join(out_lines))

            # 星空
            for sx, sy, bright in starfield:
                flicker = 0.4 + 0.6 * abs(math.sin(total_time * 2.0 + sx * 0.1))
                b = int(150 * bright * flicker)
                if 1 <= sx <= cols and 1 <= sy <= rows:
                    goto(sx, sy)
                    sys.stdout.write(bg_rgb(b, b, b + 30) + '  ')

            # 粒子
            for p in particles:
                px, py = int(p.x), int(p.y)
                if 1 <= px <= cols and 1 <= py <= rows:
                    alpha = max(0, 1 - p.age / p.life)
                    r, g, b = int(p.r*alpha), int(p.g*alpha), int(p.b*alpha)
                    goto(px, py)
                    sys.stdout.write(bg_rgb(r, g, b) + fg_rgb(r, g, b) + '▄' + reset())

            # ── 评级大字浮现 (1.5s - 5s) ──
            if 1.5 <= total_time < 5.0:
                font = FONTS.get(rating, FONT_S)
                font_w, font_h = 5, 7
                scale = 3
                char_x = cx - (font_w * scale) // 2
                char_y = cy - (font_h * scale) // 2

                fade = min(1.0, (total_time - 1.5) / 0.6)
                shake_x = int((random.random() - 0.5) * 3 * (1 - fade))
                shake_y = int((random.random() - 0.5) * 2 * (1 - fade))

                for fy in range(font_h):
                    for fx in range(font_w):
                        if font[fy][fx]:
                            for sy in range(scale):
                                for sx in range(scale):
                                    px = char_x + fx * scale + sx + shake_x
                                    py = char_y + fy * scale + sy + shake_y
                                    if 1 <= px <= cols and 1 <= py <= rows:
                                        r = int(GOLD[0] * fade)
                                        g = int(GOLD[1] * fade)
                                        b = int(GOLD[2] * fade)
                                        goto(px, py)
                                        sys.stdout.write(bg_rgb(r, g, b) + fg_rgb(r, g, b) + '█' + reset())

            # ── 金色边框 (2.5s - 5s) ──
            if 2.5 <= total_time < 5.0:
                border_fade = min(1.0, (total_time - 2.5) / 0.5)
                r, g, b = int(GOLD[0]*border_fade), int(GOLD[1]*border_fade), int(GOLD[2]*border_fade)
                color = bg_rgb(r, g, b) + fg_rgb(r, g, b)
                for x in range(1, cols + 1):
                    goto(x, 1); sys.stdout.write(color + '▄' + reset())
                    goto(x, rows); sys.stdout.write(color + '▀' + reset())
                for y in range(1, rows + 1):
                    goto(1, y); sys.stdout.write(color + '█' + reset())
                    goto(cols, y); sys.stdout.write(color + '█' + reset())

            # ── 底部字幕滚动 (3.5s - 6s) ──
            if 3.5 <= total_time < 6.0:
                sub_fade = min(1.0, (total_time - 3.5) / 0.4)
                text = f'  ★★★  {project_name}  CLEAR!  ★★★  '
                text_x = cols - int((total_time - 3.5) * 15) % (cols + len(text) + 20) + 5
                text_y = rows - 2
                r, g, b = int(255*sub_fade), int(255*sub_fade), int(255*sub_fade)

                for i, ch in enumerate(text):
                    px = text_x + i
                    if 1 <= px <= cols and 1 <= text_y <= rows:
                        goto(px, text_y)
                        sys.stdout.write(fg_rgb(r, g, b) + bg_rgb(*BG) + ch + reset())

            # ── 顶部标题 (3s - 6s) ──
            if 3.0 <= total_time < 6.0:
                title_fade = min(1.0, (total_time - 3.0) / 0.5)
                title = f'  GAME CLEAR  '
                title_x = cx - len(title) // 2
                r, g, b = int(GOLD[0]*title_fade), int(GOLD[1]*title_fade), int(GOLD[2]*title_fade)
                for i, ch in enumerate(title):
                    goto(title_x + i, 2)
                    sys.stdout.write(fg_rgb(r, g, b) + bg_rgb(*BG) + ch + reset())

            flush()
            elapsed = time.time() - frame_start
            time.sleep(max(0, frame_duration - elapsed))
            total_time += dt

        # ── 定格画面 ──
        clear()
        goto(1, 1)

        card = f"""{bg_rgb(*BG)}{fg_rgb(255,215,0)}
  ╔══════════════════════════════════════╗
  ║                                      ║
  ║   {fg_rgb(255,255,255)}🎮 恭喜！项目《{project_name}》已通关！{fg_rgb(255,215,0)}   ║
  ║                                      ║
  ║   {fg_rgb(255,255,255)}📊 代码行数     : {lines} 行{fg_rgb(255,215,0)}              ║
  ║   {fg_rgb(255,255,255)}🐛 Bug 击杀    : {bugs} 只{fg_rgb(255,215,0)}              ║
  ║   {fg_rgb(255,255,255)}📁 涉及文件     : {files} 个{fg_rgb(255,215,0)}              ║
  ║   {fg_rgb(255,255,255)}👥 通关角色     : 人类 × AI 联机小队{fg_rgb(255,215,0)}   ║
  ║   {fg_rgb(255,255,255)}⭐ 评价等级     : {rating}{fg_rgb(255,215,0)}                   ║
  ║                                      ║
  ╚══════════════════════════════════════╝
{reset()}"""
        sys.stdout.write(card)
        flush()

    finally:
        show_cursor()
        print()

# ── 入口 ─────────────────────────────────────────────────────
if __name__ == '__main__':
    rating = sys.argv[1] if len(sys.argv) > 1 else 'S'
    project = sys.argv[2] if len(sys.argv) > 2 else '未知任务'
    lines = int(sys.argv[3]) if len(sys.argv) > 3 else 173
    bugs = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    files = int(sys.argv[5]) if len(sys.argv) > 5 else 1
    animate(rating, project, lines, bugs, files)
