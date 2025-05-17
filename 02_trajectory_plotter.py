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

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ---- 设置中文字体，避免中文乱码 ----
plt.rcParams['font.sans-serif'] = ['SimHei']  # 指定中文字体为黑体
plt.rcParams['axes.unicode_minus'] = False    # 正常显示负号

# ---- 1. 读取数据 ----
df = pd.read_excel('predict_theta_g.xlsx', sheet_name='Sheet1')
df.columns = ['theta', 'g']  # 确保列名正确

# ---- 2. 初始速度 ----
# We used the empirically determined firing speed (100.37 m/s) from
# https://github.com/NYTN02/APEX_thetacalculation
v0 = 100.37  # m/s

# ---- 3. 配色方案：根据 theta 在 [theta_min, theta_max] 做渐变 ----
theta_min = df['theta'].min()
theta_max = df['theta'].max()
norm = (df['theta'] - theta_min) / (theta_max - theta_min)
cmap = plt.get_cmap('viridis')

# ---- 4. 创建画布和坐标轴 ----
fig, ax = plt.subplots(figsize=(10, 6))

# ---- 5. 逐条计算并绘制轨迹（延伸至高度 y = -100m） ----
for theta, g, n in zip(df['theta'], df['g'], norm):
    theta_rad = np.deg2rad(theta)  # 角度转弧度

    # 求解 y(t) = -100 时的 t：0.5*g*t^2 - v0*sin(theta)*t - 100 = 0
    a = 0.5 * g
    b = -v0 * np.sin(theta_rad)
    c = -100
    disc = b**2 - 4 * a * c
    t_end = (-b + np.sqrt(disc)) / (2 * a)  # 取正根

    # 时间采样
    t = np.linspace(0, t_end, 300)

    # 轨迹方程
    x = v0 * np.cos(theta_rad) * t
    y = v0 * np.sin(theta_rad) * t - 0.5 * g * t**2

    ax.plot(x, y, color=cmap(n), linewidth=1)

# ---- 6. 添加颜色条 ----
sm = plt.cm.ScalarMappable(norm=plt.Normalize(vmin=theta_min, vmax=theta_max), cmap=cmap)
sm.set_array([])  # 为 colorbar 提供数据
cbar = fig.colorbar(sm, ax=ax)
cbar.set_label('倾角 θ (度)')

# ---- 7. 设置标签与标题 ----
ax.set_xlabel('水平距离 x (m)')
ax.set_ylabel('高度 y (m)')
ax.set_title('不同倾角下的斜抛运动轨迹（延伸至 -100m 地面）')

# ---- 8. 网格与布局 ----
ax.grid(True)
plt.tight_layout()

# ---- 9. 显示图形 ----
plt.show()
