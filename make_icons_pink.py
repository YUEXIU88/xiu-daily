# -*- coding: utf-8 -*-
"""V68: 重新生成统一粉色版 PWA 图标
设计：粉红渐变背景 + 白色地球线框 + 玫瑰金双向贸易箭头 + 顶部柔光
替换原来青蓝色版的 icon-192/icon-512/icon-maskable-512
"""
import math
from PIL import Image, ImageDraw, ImageFilter

S = 1024

# 粉色系（用户截图里那个粉色图标大致是 #ff5d8f ~ #ffa6c5 范围）
PINK_DARK  = (255, 102, 152)   # #ff6698 主色
PINK_LIGHT = (255, 196, 215)   # #ffc4d7 顶部高光
PINK_DEEP  = (220, 80, 130)    # #dc5082 底部加深、箭头深色
GOLD       = (255, 220, 165)   # #ffdca5 偏暖玫瑰金（搭配粉底）
WHITE      = (255, 255, 255)
W_SOFT     = (255, 255, 255, 130)


def gradient_bg(size):
    """粉红渐变：左上浅粉 → 右下深粉"""
    grad = Image.new('RGBA', (size, size))
    gd = ImageDraw.Draw(grad)
    for y in range(size):
        t = y / (size - 1)
        r = int(PINK_LIGHT[0] + (PINK_DARK[0] - PINK_LIGHT[0]) * t)
        g = int(PINK_LIGHT[1] + (PINK_DARK[1] - PINK_LIGHT[1]) * t)
        b = int(PINK_LIGHT[2] + (PINK_DARK[2] - PINK_LIGHT[2]) * t)
        gd.line([(0, y), (size, y)], fill=(r, g, b, 255))
    # 加一个左上柔光叠加层
    glow = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    gg = ImageDraw.Draw(glow)
    gg.ellipse([-size * 0.3, -size * 0.3, size * 0.6, size * 0.6], fill=(255, 255, 255, 60))
    glow = glow.filter(ImageFilter.GaussianBlur(size * 0.18))
    grad = Image.alpha_composite(grad, glow)
    return grad


def draw_globe(d, cx, cy, r):
    """白色线框地球（同原设计）"""
    lw_main = max(6, int(r * 0.055))
    lw_sub = max(4, int(r * 0.035))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=WHITE, width=lw_main)
    for k in (0.94, 0.56):
        rx = int(r * k)
        d.ellipse([cx - rx, cy - r, cx + rx, cy + r], outline=W_SOFT, width=lw_sub)
    for frac in (0.0, 0.52, -0.52):
        yy = cy + int(r * frac)
        half = int(r * math.sqrt(max(0, 1 - frac * frac)))
        col = WHITE if frac == 0.0 else W_SOFT
        d.line([cx - half, yy, cx + half, yy], fill=col, width=lw_sub)


def arc_point(cx, cy, r, ang_deg):
    a = math.radians(ang_deg)
    return cx + r * math.cos(a), cy + r * math.sin(a)


def draw_arrow_head(d, tip, ang_deg, size, color):
    tx, ty = tip
    dir_ang = math.radians(ang_deg + 90)
    dx, dy = math.cos(dir_ang), math.sin(dir_ang)
    px, py = -dy, dx
    p1 = (tx + dx * size * 0.9, ty + dy * size * 0.9)
    p2 = (tx - dx * size * 0.35 + px * size * 0.62, ty - dy * size * 0.35 + py * size * 0.62)
    p3 = (tx - dx * size * 0.35 - px * size * 0.62, ty - dy * size * 0.35 - py * size * 0.62)
    d.polygon([p1, p2, p3], fill=color)


def draw_trade_arrows(d, cx, cy, r):
    """玫瑰金双向弧线箭头"""
    ra = int(r * 1.34)
    lw = max(8, int(r * 0.075))
    head = max(16, int(r * 0.24))
    d.arc([cx - ra, cy - ra, cx + ra, cy + ra], start=196, end=322, fill=GOLD, width=lw)
    draw_arrow_head(d, arc_point(cx, cy, ra, 322), 322, head, GOLD)
    d.arc([cx - ra, cy - ra, cx + ra, cy + ra], start=16, end=142, fill=GOLD, width=lw)
    draw_arrow_head(d, arc_point(cx, cy, ra, 142), 142, head, GOLD)
    for ang in (196, 16):
        ex, ey = arc_point(cx, cy, ra, ang)
        er = max(5, int(r * 0.055))
        d.ellipse([ex - er, ey - er, ex + er, ey + er], fill=GOLD)


def make_art(scale=1.0):
    img = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    img.paste(gradient_bg(S), (0, 0))
    d = ImageDraw.Draw(img)
    cx = cy = S // 2
    r = int(S * 0.215 * scale)
    draw_globe(d, cx, cy, r)
    draw_trade_arrows(d, cx, cy, r)
    return img


def rounded(img, radius_ratio=0.225):
    mask = Image.new('L', (S, S), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle([0, 0, S, S], radius=int(S * radius_ratio), fill=255)
    out = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    out.paste(img, (0, 0), mask)
    return out


def save(img, path, size):
    img.resize((size, size), Image.LANCZOS).save(path, 'PNG')
    print('saved', path, '->', size, 'x', size)


if __name__ == '__main__':
    # 标准图标（圆角、含透明边角）
    art = make_art(1.0)
    save(rounded(art), 'icon-192.png', 192)
    save(rounded(art), 'icon-512.png', 512)
    # maskable：全出血背景、内容缩到安全区（72%）
    full = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    full.paste(gradient_bg(S), (0, 0))
    art_small = make_art(0.72)
    full = Image.alpha_composite(full, art_small)
    save(full, 'icon-maskable-512.png', 512)
    print('=== PINK ICONS DONE ===')
