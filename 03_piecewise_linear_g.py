# -*- coding: utf-8 -*-
#
# apex_sparrow_dart_calc
#
# A Sparrow Tracker Dart trajectory calculator for Apex Legends
#
# Copyright (C) 2025 https://github.com/leejch
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Author: https://github.com/leejch
# GitHub: https://github.com/leejch/apex_sparrow_dart_calc

import numpy as np
import matplotlib.pyplot as plt

# ---- 设置中文字体，避免中文乱码 ----
plt.rcParams['font.sans-serif'] = ['SimHei']  # 指定中文字体为黑体
plt.rcParams['axes.unicode_minus'] = False    # 正常显示负号

# ---- 绘制分段线性 g(θ) 函数 ----
points = [
    (30.00, 21.6),
    (46.77, 24.6),
    (53.58, 27.8),
    (66.95, 31.8),
    (81.89, 35.2888),
    (89.00, 37.2539)
]

# 遍历每一段相邻点，计算一次函数表达式
print("共 {} 段函数：\n".format(len(points) - 1))
for i in range(len(points) - 1):
    x1, y1 = points[i]
    x2, y2 = points[i + 1]

    # 计算斜率 a 和截距 b：g(θ) = a*θ + b
    a = round((y2 - y1) / (x2 - x1), 5)
    b = round(y1 - a * x1, 5)

    print(f"第 {i+1} 段函数区间：[{x1:.2f}, {x2:.2f}]")
    print(f"g(θ) ={a:.5f}*A1+{b:.5f}\n")

fig2, ax2 = plt.subplots(figsize=(8, 5))
for (x1, y1), (x2, y2) in zip(points[:-1], points[1:]):
    # 计算当前段的 a, b
    a = (y2 - y1) / (x2 - x1)
    b = y1 - a * x1
    # 在当前段上取 100 个点
    thetas = np.linspace(x1, x2, 100)
    gs = a * thetas + b
    ax2.plot(thetas, gs, linewidth=2)

# 标出所有节点
tp, gp = zip(*points)
ax2.scatter(tp, gp, color='red', zorder=5)
for θ, g_val in points:
    ax2.text(θ, g_val, f'({θ:.2f},{g_val:.2f})', fontsize=8, va='bottom')

ax2.set_xlabel('倾角 θ (度)')
ax2.set_ylabel('重力加速度 g (m/s^2)')
ax2.set_title('分段线性关系 g(θ)')
ax2.grid(True)
plt.tight_layout()
plt.show()
