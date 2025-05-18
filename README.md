# apex_sparrow_dart_calc

<br>简体中文 / [English](README_EN.md)<br><br>

## 网页版

直接使用网页版，请访问: [琉雀追踪器飞镖射击角度计算器](https://leejch.github.io/apex_sparrow_dart_calc/)

## 项目简介

Apex Legends新传奇琉雀的追踪器飞镖技能的射击角度计算器，集数据拟合、轨迹绘制和分段线性模型于一体。

首先基于实测数据，使用 PyTorch 对倾角 θ 与对应重力加速度 g 构建非线性回归模型，生成全角度范围内的预测结果。

随后根据人工提取的转折点，构建分段一次函数近似 g(θ)，并在最终的命中计算器中实现高射角与低射角的判定与分类。

用户仅需输入目标与自身的水平距离 d 及瞄准倾角 θ_aim，即可获得精准的射击角度，并可视化对应弹道轨迹。

## 文件说明

- `theta_g_predictor.py` 负责加载原始实验数据、训练并验证神经网络模型，最终输出 θ→g 预测结果；
- `trajectory_plotter.py` 读取预测结果并绘制延伸至指定落地高度的斜抛轨迹图；
- `piecewise_linear_g.py` 根据人工选定的转折点生成并展示分段线性 g(θ) 函数；
- `sparrow_dart_calculator.py` 将前述模块整合为命令行交互工具，实现目标命中角度的计算及轨迹可视化。

## 快速开始

1. 克隆本仓库至本地后，确保已安装 Python 及依赖库：`pandas`、`numpy`、`torch`、`matplotlib`；
2. 运行 `sparrow_dart_calculator.py`，根据提示输入水平距离和瞄准角度，即可得到射击角度并生成轨迹图。


## 特别鸣谢

本项目参考并使用了以下开源成果：

- [NYTN02/APEX_thetacalculation](https://github.com/NYTN02/APEX_thetacalculation)
  使用了其计算得出的初速度参数（100.37 m/s）
  作者B站昵称："猫盒喵"，UID：379405259

## 版权与许可证

Copyright (C) 2025 [leejch](https://github.com/leejch)

本项目采用 [GPLv3 许可证](https://www.gnu.org/licenses/gpl-3.0.html) 开源发布。
你可以自由使用、修改和分发本软件，但必须保留原始版权信息，并在再发布时也使用 GPLv3 或兼容许可。

本程序按“原样”提供，不附带任何担保，包括适销性或适用于特定目的的适用性。
