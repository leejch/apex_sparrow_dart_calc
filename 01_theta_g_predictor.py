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

import os
import datetime
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader

# ----------------- 数据集定义 -----------------
class ThetaGDataset(Dataset):
    """自定义数据集：θ → g"""
    def __init__(self, theta_list, g_list):
        self.theta = torch.tensor(theta_list, dtype=torch.float32).unsqueeze(1)
        self.g = torch.tensor(g_list, dtype=torch.float32).unsqueeze(1)

    def __len__(self):
        return len(self.theta)

    def __getitem__(self, idx):
        return self.theta[idx], self.g[idx]

# ----------------- 模型定义 -----------------
class FeedForwardNN(nn.Module):
    """全连接网络：1→128→128→64→1，LeakyReLU 激活"""
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(1, 128),
            nn.LeakyReLU(inplace=True),
            nn.Linear(128, 128),
            nn.LeakyReLU(inplace=True),
            nn.Linear(128, 64),
            nn.LeakyReLU(inplace=True),
            nn.Linear(64, 1)
        )

    def forward(self, x):
        return self.net(x)

def main():
    # 设备选择
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"使用设备：{device}")

    # 1. 加载原始数据
    df = pd.read_excel("train_theta_g.xlsx", sheet_name="Sheet1", header=None)
    theta = df[0].values.astype(np.float32)
    g = df[1].values.astype(np.float32)

    # 2. 数据归一化（零均值、单位方差）
    theta_mean, theta_std = theta.mean(), theta.std()
    g_mean, g_std = g.mean(), g.std()
    theta_norm = (theta - theta_mean) / theta_std
    g_norm = (g - g_mean) / g_std

    # 3. 训练/验证集划分
    idx = np.arange(len(theta_norm))
    np.random.shuffle(idx)
    split = int(0.8 * len(idx))
    train_idx, val_idx = idx[:split], idx[split:]
    train_dataset = ThetaGDataset(theta_norm[train_idx], g_norm[train_idx])
    val_dataset   = ThetaGDataset(theta_norm[val_idx],   g_norm[val_idx])
    train_loader  = DataLoader(train_dataset, batch_size=32, shuffle=True)
    val_loader    = DataLoader(val_dataset,   batch_size=32, shuffle=False)

    # 4. 模型/损失/优化器/调度器
    model     = FeedForwardNN().to(device)
    criterion = nn.SmoothL1Loss()   # Huber 损失
    optimizer = optim.Adam(model.parameters(), lr=1e-3)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode='min', factor=0.5, patience=20
    )

    # 5. 训练循环（含早停）
    best_val_loss = float('inf')
    patience, counter = 50, 0
    max_epochs = 1000
    print("开始训练……")
    for epoch in range(1, max_epochs + 1):
        # --- 训练 ---
        model.train()
        train_loss = 0.0
        for x_batch, y_batch in train_loader:
            x_batch, y_batch = x_batch.to(device), y_batch.to(device)
            optimizer.zero_grad()
            y_pred = model(x_batch)
            loss = criterion(y_pred, y_batch)
            loss.backward()
            optimizer.step()
            train_loss += loss.item() * x_batch.size(0)
        train_loss /= len(train_loader.dataset)

        # --- 验证 ---
        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for x_batch, y_batch in val_loader:
                x_batch, y_batch = x_batch.to(device), y_batch.to(device)
                y_pred = model(x_batch)
                val_loss += criterion(y_pred, y_batch).item() * x_batch.size(0)
        val_loss /= len(val_loader.dataset)

        # 调整学习率
        scheduler.step(val_loss)

        if epoch % 100 == 0 or epoch == 1:
            print(f"Epoch {epoch}/{max_epochs} 训练损失: {train_loss:.6f}  验证损失: {val_loss:.6f}")

        # 早停判断
        if val_loss < best_val_loss - 1e-8:
            best_val_loss = val_loss
            counter = 0
            torch.save(model.state_dict(), "best_model.pt")
        else:
            counter += 1
            if counter >= patience:
                print(f"验证损失在 {patience} 个 epoch 内无改善，触发早停 (epoch={epoch})")
                break

    # 加载最佳模型
    model.load_state_dict(torch.load("best_model.pt", map_location=device))

    # 6. 生成预测并反归一化
    thetas = np.arange(89.0, 29.999, -0.01).round(2).astype(np.float32)
    theta_input = torch.tensor((thetas - theta_mean) / theta_std, dtype=torch.float32).unsqueeze(1).to(device)
    model.eval()
    with torch.no_grad():
        g_pred_norm = model(theta_input).cpu().numpy().flatten()
    g_pred = g_pred_norm * g_std + g_mean

    # 7. 保存到 Excel
    result_df = pd.DataFrame({"theta": thetas, "g_pred": g_pred})
    ts = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
    out_name = f"predict_{ts}.xlsx"
    result_df.to_excel(out_name, index=False)
    print(f"已生成预测结果文件：{out_name}")

if __name__ == "__main__":
    main()
