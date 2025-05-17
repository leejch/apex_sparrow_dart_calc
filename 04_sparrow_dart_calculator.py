# -*- coding: utf-8 -*-
#
# apex_sparrow_dart_calc
#
# A Sparrow Tracker Dart trajectory calculator for Apex Legends
#
# Copyright (C) 2025 https://github.com/leejch
#
# This file is part of apex_sparrow_dart_calc.
#
# apex_sparrow_dart_calc is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# apex_sparrow_dart_calc is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with apex_sparrow_dart_calc. If not, see <https://www.gnu.org/licenses/>.
#
# Author: https://github.com/leejch
# GitHub: https://github.com/leejch/apex_sparrow_dart_calc

import math
import numpy as np
import matplotlib.pyplot as plt

# ---- 设置中文字体，避免中文乱码 ----
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# ---- 常量 ----
# We used the empirically determined firing speed (100.37 m/s) from
# https://github.com/NYTN02/APEX_thetacalculation
v0 = 100.37  # 初速度 (m/s)

# ---- 分段线性函数：根据 θ 返回重力加速度 g(θ) ----
def get_g(theta):
    if 25.00 <= theta <= 46.77:
        return 0.17889 * theta + 16.23330
    elif 46.77 < theta <= 53.58:
        return 0.46990 * theta + 2.62278
    elif 53.58 < theta <= 66.95:
        return 0.29918 * theta + 11.76994
    elif 66.95 < theta <= 81.89:
        return 0.23352 * theta + 16.16584
    elif 81.89 < theta < 89.00:
        return 0.27639 * theta + 12.65522
    else:
        return None

# ---- 方程 F(θ; d, h)=0: 在 x=d 时 y=h ----
def F(theta, d, h):
    gθ = get_g(theta)
    if gθ is None:
        return 1e6
    θ = math.radians(theta)
    return d * math.tan(θ) - gθ * d**2 / (2 * v0**2 * math.cos(θ)**2) - h

# ---- 判断在 x=d 时是否处于“下落”阶段（导数<0） ----
def is_descending(theta, d):
    gθ = get_g(theta)
    θ = math.radians(theta)
    return (math.tan(θ) - gθ * d / (v0**2 * math.cos(θ)**2)) < 0

# ---- 二分法求根，要求 func(a)*func(b)<0 ----
def bisect_root(func, a, b, tol=1e-6, max_iter=50):
    fa, fb = func(a), func(b)
    if fa * fb > 0:
        raise ValueError("端点没有异号")
    for _ in range(max_iter):
        m = 0.5 * (a + b)
        fm = func(m)
        if fa * fm <= 0:
            b, fb = m, fm
        else:
            a, fa = m, fm
        if abs(b - a) < tol:
            break
    return 0.5 * (a + b)

# ---- 在 [25.00, 89.00) 区间扫面并求出所有命中根 ----
def find_all_roots(d, h):
    roots = []
    step = 0.01
    thetas = np.arange(25.00, 89.00, step)
    Fs = [F(t, d, h) for t in thetas]
    for i in range(len(thetas) - 1):
        t1, t2 = thetas[i], thetas[i+1]
        f1, f2 = Fs[i], Fs[i+1]
        if f1 * f2 < 0:
            try:
                root = bisect_root(lambda th: F(th, d, h), t1, t2)
            except ValueError:
                continue
            roots.append(round(root, 5))
    return sorted(set(roots))

# ---- 按照要求分类低射和高射角度 ----
def classify(nominal_all, d):
    # 分离下落解和上升解
    desc = [r for r in nominal_all if is_descending(r, d)]
    asc  = [r for r in nominal_all if not is_descending(r, d)]
    desc.sort()
    asc.sort()

    θ_high = None
    θ_low  = None

    # 先处理下落解
    if len(desc) >= 2:
        θ_low  = desc[0]
        θ_high = desc[-1]
    elif len(desc) == 1:
        θ_high = desc[0]
        # 再看上升解能否做低射：需 < θ_high
        valid_asc = [r for r in asc if r < θ_high]
        if valid_asc:
            θ_low = max(valid_asc)
    else:
        # 下落解为空，则无高射；可用上升解做低射
        θ_high = None
        if asc:
            θ_low = max(asc)

    return θ_low, θ_high

# ---- 主程序 ----
def main():
    # 1. 输入
    d = float(input("请输入目标水平距离 d (m): "))
    θ_aim = float(input("请输入瞄准角度 θ_aim (度): "))

    # 2. 计算目标高度差并输出
    h = d * math.tan(math.radians(θ_aim))
    print(f"目标高度差 h = {h:.1f} m")

    # 3. 求 nominal、far、near 三种距离的所有根
    nominal_all = find_all_roots(d, h)
    far_all     = find_all_roots(d + 2, h) if d > 2 else []
    near_all    = find_all_roots(d - 2, h) if d > 2 else []

    # 4. 无解：没有任何命中根
    if not nominal_all:
        print("无解：无法命中目标。")
        return

    # 5. 分类 nominal 距离下的低射/高射
    θ_low, θ_high = classify(nominal_all, d)

    # 6. 输出单解/双解/无高射 情况
    if θ_high is None:
        print("高射无解。")
    elif θ_low is None:
        # 只有高射
        print(f"射击角度 θ = {θ_high:.2f}°")
    else:
        print(f"低射角 θ_low  = {θ_low:.2f}°")
        print(f"高射角 θ_high = {θ_high:.2f}°")

    # 7. 分别分类 near（近处）与 far（远处），输出极值
    θ_low_max,  θ_high_max  = classify(near_all, d - 2)
    θ_low_min,  θ_high_min  = classify(far_all, d + 2)

    if θ_low_min  is not None:
        print(f"低射最小角 θ_low_min   = {θ_low_min:.2f}°")
    if θ_low_max  is not None:
        print(f"低射最大角 θ_low_max   = {θ_low_max:.2f}°")
    if θ_high_min is not None:
        print(f"高射最小角 θ_high_min  = {θ_high_min:.2f}°")
    if θ_high_max is not None:
        print(f"高射最大角 θ_high_max  = {θ_high_max:.2f}°")

    # 8. 绘图：只绘制存在的轨迹
    fig, ax = plt.subplots(figsize=(8, 5))
    for θ, label in [(θ_low, '低射轨迹'), (θ_high, '高射轨迹')]:
        if θ is None:
            continue
        θrad = math.radians(θ)
        gθ = get_g(θ)
        # 绘制范围：h>=0 绘制到落地 y=0，否则绘制到 x=d
        if h >= 0:
            t_end = 2 * v0 * math.sin(θrad) / gθ
        else:
            t_end = d / (v0 * math.cos(θrad))
        t = np.linspace(0, t_end, 300)
        x = v0 * math.cos(θrad) * t
        y = v0 * math.sin(θrad) * t - 0.5 * gθ * t**2
        ax.plot(x, y, label=f"{label} ({θ:.2f}°)")

    # 标记目标点
    ax.scatter([d], [h], color='k', zorder=5)
    ax.text(d, h, '  目标', va='bottom')

    ax.set_xlabel('水平距离 x (m)')
    ax.set_ylabel('高度 y (m)')
    ax.set_title('射击弹道轨迹')
    ax.legend()
    ax.grid(True)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
