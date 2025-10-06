import os
import math
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import norm
from torch.utils.data import Dataset, DataLoader
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

# 设置随机种子保证可重复性
torch.manual_seed(42)
np.random.seed(42)

# 设置设备
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"使用设备: {device}")


# 数据预处理与加载
class OptionDataset(Dataset):
    def __init__(self, X_seq, y, S, K, r, T, option_type):
        # 将形状从 [batch_size, seq_len, features/channels] 转换为 [batch_size, features/channels, seq_len]
        self.X_seq = torch.tensor(X_seq, dtype=torch.float32).to(device).transpose(1, 2)
        self.y = torch.tensor(y.values, dtype=torch.float32).to(device).unsqueeze(1)
        self.S = torch.tensor(S.values, dtype=torch.float32).to(device).unsqueeze(1)
        self.K = torch.tensor(K.values, dtype=torch.float32).to(device).unsqueeze(1)
        self.r = torch.tensor(r.values, dtype=torch.float32).to(device).unsqueeze(1)
        self.T = torch.tensor(T.values, dtype=torch.float32).to(device).unsqueeze(1)
        self.option_type = torch.tensor(option_type.values, dtype=torch.float32).to(device).unsqueeze(1)

    def __len__(self):
        return len(self.y)

    def __getitem__(self, idx):
        return (self.X_seq[idx], self.y[idx], self.S[idx], self.K[idx],
                self.r[idx], self.T[idx], self.option_type[idx])


def get_dataloaders(data_path, seq_len=20, batch_size=64, test_size=0.2):
    # 1. 读取并预处理原始数据
    data = pd.read_csv(data_path)  # 修复硬编码路径问题

    # 必要列检查
    required_cols = ["date", "S0", "K", "T", "r", "sigma", "V0", "option_type"]
    assert all(col in data.columns for col in required_cols), f"缺失必要列：{set(required_cols) - set(data.columns)}"

    # 处理缺失值/异常值
    data = data.ffill()  # 替换fillna(method="ffill")避免警告
    data = data[(data["V0"] > 0) & (data["sigma"] < 2) & (data["T"] > 0)]

    # 2. 标准化特征
    scaler = StandardScaler()
    scale_cols = ["S0", "K", "r", "sigma"]
    data[[col + "_std" for col in scale_cols]] = scaler.fit_transform(data[scale_cols])

    # 3. 构建时序样本
    X_seq = []
    y = []
    S_list, K_list, r_list, T_list, option_type_list = [], [], [], [], []

    # 处理日期并排序
    try:
        data["date"] = pd.to_datetime(data["date"])
    except Exception as e:
        raise ValueError(f"date列格式错误，无法转换为日期：{str(e)}")
    data = data.sort_values("date").reset_index(drop=True)

    # 滑动窗口构建时序样本
    for i in range(seq_len, len(data)):
        seq_features = data.iloc[i - seq_len:i][["S0_std", "K_std", "r_std", "sigma_std"]].values
        X_seq.append(seq_features)
        y.append(data.iloc[i]["V0"])
        S_list.append(data.iloc[i]["S0"])
        K_list.append(data.iloc[i]["K"])
        r_list.append(data.iloc[i]["r"])
        T_list.append(data.iloc[i]["T"])
        option_type_list.append(data.iloc[i]["option_type"])

    # 转换为合适的数据类型
    X_seq = np.array(X_seq)
    y = pd.Series(y)
    S = pd.Series(S_list)
    K = pd.Series(K_list)
    r = pd.Series(r_list)
    T = pd.Series(T_list)
    option_type = pd.Series(option_type_list)

    # 4. 划分训练/测试集
    test_split_idx = int(len(X_seq) * (1 - test_size))
    X_train_seq, y_train = X_seq[:test_split_idx], y[:test_split_idx]
    S_train, K_train, r_train, T_train, opt_type_train = S[:test_split_idx], K[:test_split_idx], r[:test_split_idx], T[
                                                                                                                     :test_split_idx], option_type[
                                                                                                                                       :test_split_idx]

    X_test_seq, y_test = X_seq[test_split_idx:], y[test_split_idx:]
    S_test, K_test, r_test, T_test, opt_type_test = S[test_split_idx:], K[test_split_idx:], r[test_split_idx:], T[
                                                                                                                test_split_idx:], option_type[
                                                                                                                                  test_split_idx:]

    # 5. 构建Dataset和DataLoader
    train_dataset = OptionDataset(
        X_seq=X_train_seq, y=y_train, S=S_train, K=K_train, r=r_train, T=T_train, option_type=opt_type_train
    )
    test_dataset = OptionDataset(
        X_seq=X_test_seq, y=y_test, S=S_test, K=K_test, r=r_test, T=T_test, option_type=opt_type_test
    )

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

    return (
        train_loader, test_loader,
        scaler,
        (X_train_seq, y_train, S_train, K_train, r_train, T_train, opt_type_train),
        (X_test_seq, y_test, S_test, K_test, r_test, T_test, opt_type_test)
    )


# 辅助函数
def calculate_metrics(y_true, y_pred):
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    return {
        "MSE": round(mse, 6),
        "RMSE": round(rmse, 6),
        "MAE": round(mae, 6),
        "R²": round(r2, 4)
    }


# 打印层（调试用）
class PrintLayer(nn.Module):
    def __init__(self, message):
        super(PrintLayer, self).__init__()
        self.message = message

    def forward(self, x):
        # 调试时取消注释
        # print(f"{self.message}: {x.shape[2]}")
        return x


# 残差块定义
class TemporalResidualBlock(nn.Module):
    def __init__(self, in_channels, out_channels, seq_len, kernel_sizes, dilations,
                 dropout_p=0.1, shifts=[1, 2]):
        super(TemporalResidualBlock, self).__init__()

        self.seq_len = seq_len
        self.conv_layers = nn.Sequential(
            nn.Conv1d(in_channels, out_channels, kernel_size=kernel_sizes[0], dilation=dilations[0],
                      padding=self._get_padding(kernel_sizes[0], dilations[0])),
            nn.BatchNorm1d(out_channels),
            nn.ReLU(),
            nn.Dropout(dropout_p),
            PrintLayer("第一层卷积后长度"),

            nn.Conv1d(out_channels, out_channels, kernel_size=kernel_sizes[1], dilation=dilations[1],
                      padding=self._get_padding(kernel_sizes[1], dilations[1])),
            nn.BatchNorm1d(out_channels),
            nn.ReLU(),
            nn.Dropout(dropout_p),
            PrintLayer("第二层卷积后长度"),

            nn.Conv1d(out_channels, out_channels, kernel_size=kernel_sizes[2], dilation=dilations[2],
                      padding=self._get_padding(kernel_sizes[2], dilations[2])),
            nn.BatchNorm1d(out_channels),
            PrintLayer("第三层卷积后长度"),
        )

        self.shifts = shifts
        self.shift_weights = nn.Parameter(
            torch.ones(len(shifts)) / len(shifts),
            requires_grad=True
        )

        self.shortcut = nn.Sequential()
        if in_channels != out_channels:
            self.shortcut = nn.Conv1d(in_channels, out_channels, kernel_size=1)

        self.relu = nn.ReLU()

    def _get_padding(self, kernel_size, dilation):
        effective_k = (kernel_size - 1) * dilation + 1
        return (effective_k - 1) // 2

    def temporal_shift(self, x, shift):
        if shift == 0:
            return x
        batch_size, channels, seq_len = x.shape

        if shift > 0:
            shifted = torch.cat([
                torch.zeros(batch_size, channels, shift, device=x.device),
                x[:, :, :-shift]
            ], dim=2)
        else:
            shift_abs = -shift
            shifted = torch.cat([
                x[:, :, shift_abs:],
                torch.zeros(batch_size, channels, shift_abs, device=x.device)
            ], dim=2)

        return shifted

    def forward(self, x):
        print(f"卷积前长度: {x.shape[2]}")
        out = self.conv_layers(x)
        # print(f"卷积后长度: {out.shape[2]}")

        assert out.shape[2] == self.seq_len, \
            f"卷积后长度不匹配: 预期{self.seq_len}, 实际{out.shape[2]}"

        residual = self.shortcut(x)

        shifted_residuals = []
        for shift in self.shifts:
            shifted = self.temporal_shift(residual, shift)
            shifted_residuals.append(shifted)

        weights = F.softmax(self.shift_weights, dim=0)
        weighted_residual = sum(w * s for w, s in zip(weights, shifted_residuals))

        out += weighted_residual
        out = self.relu(out)
        return out


# 期权定价模型 - 仅使用残差网络，移除未定义的LSTM和注意力机制
class OptionPricing(nn.Module):
    def __init__(self, in_channels=4,
                 seq_len=20,
                 num_blocks=3,
                 block_channels=[64, 128, 128],
                 kernel_sizes=[[3, 5, 7], [3, 5, 7], [3, 5, 7]],
                 dilations=[[1, 2, 3], [2, 3, 4], [3, 4, 5]],
                 dropout_p=0.1):
        super(OptionPricing, self).__init__()

        # 输入层
        self.input_layer = nn.Conv1d(in_channels, block_channels[0], kernel_size=1)

        # 残差块堆叠
        self.res_blocks = nn.ModuleList()
        for i in range(num_blocks):
            self.res_blocks.append(
                TemporalResidualBlock(
                    in_channels=block_channels[i - 1] if i > 0 else block_channels[0],
                    out_channels=block_channels[i],
                    seq_len=seq_len,
                    kernel_sizes=kernel_sizes[i],
                    dilations=dilations[i],
                    dropout_p=dropout_p,
                )
            )

        self.res_output_channels = block_channels[-1]

        # 全局平均池化
        self.global_avg_pool = nn.AdaptiveAvgPool1d(1)

        # 输出层
        self.output_layer = nn.Sequential(
            nn.Linear(self.res_output_channels, 64),
            nn.ELU(),
            nn.Dropout(dropout_p),
            nn.Linear(64, 1)
        )

    def forward(self, x, S, K, r, T, option_type):
        # 输入层特征映射
        x = self.input_layer(x)

        # 残差块特征提取
        for block in self.res_blocks:
            x = block(x)

        # 全局池化
        x = self.global_avg_pool(x).squeeze(-1)  # [batch, channels]

        # 输出价格
        raw_price = self.output_layer(x).unsqueeze(1)  # [batch, 1]

        # 应用金融约束
        constrained_price = self._apply_constraints(raw_price, S, K, r, T, option_type)

        return constrained_price

    def _apply_constraints(self, price, S, K, r, T, option_type):
        """应用期权定价的无套利约束"""
        # 看涨期权约束: price <= S 且 price >= max(S - K*e^(-rT), 0)
        call_mask = (option_type == 0).float()
        call_upper = S
        call_lower = torch.max(S - K * torch.exp(-r * T), torch.zeros_like(price))
        price = call_mask * torch.clamp(price, call_lower, call_upper) + (1 - call_mask) * price

        # 看跌期权约束: price <= K*e^(-rT) 且 price >= max(K*e^(-rT) - S, 0)
        put_mask = (option_type == 1).float()
        put_upper = K * torch.exp(-r * T)
        put_lower = torch.max(K * torch.exp(-r * T) - S, torch.zeros_like(price))
        price = put_mask * torch.clamp(price, put_lower, put_upper) + (1 - put_mask) * price

        return price


# 测试模型结构
def test_model_structure():
    in_channels = 4
    num_blocks = 3
    block_channels = [64, 128, 128]
    kernel_sizes = [[3, 5, 7], [3, 5, 7], [3, 5, 7]]
    # dilations = [[1, 2, 3], [2, 3, 4], [3, 4, 5]]
    dilations = [[2, 4, 6], [2, 4, 6], [4, 6, 8]]  # 确保dilation是偶数

    model = OptionPricing(
        in_channels=in_channels,
        seq_len=20,
        num_blocks=num_blocks,
        block_channels=block_channels,
        kernel_sizes=kernel_sizes,
        dilations=dilations,
        dropout_p=0.1
    ).to(device)

    # 模拟输入
    batch_size = 8
    seq_len = 20
    x = torch.randn(batch_size, in_channels, seq_len).to(device)
    S = torch.rand(batch_size, 1).to(device) * 100
    K = torch.rand(batch_size, 1).to(device) * 100
    r = torch.rand(batch_size, 1).to(device) * 0.05
    T = torch.rand(batch_size, 1).to(device) * 2
    option_type = torch.randint(0, 2, (batch_size, 1)).to(device)

    # 前向传播
    constrained_price = model(x, S, K, r, T, option_type)
    print("约束后价格形状:", constrained_price.shape)  # 应为 (8, 1)


# 完整训练函数
def train_model(model, train_loader, test_loader, epochs=100, lr=0.001, patience=5):
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)
    model.to(device)

    best_test_loss = float('inf')
    early_stop_count = 0

    for epoch in range(epochs):
        # 训练阶段
        model.train()
        train_loss = 0.0
        for X_batch, y_batch, S_batch, K_batch, r_batch, T_batch, opt_type_batch in train_loader:
            optimizer.zero_grad()
            constrained_price = model(
                x=X_batch,
                S=S_batch,
                K=K_batch,
                r=r_batch,
                T=T_batch,
                option_type=opt_type_batch
            )

            loss = criterion(constrained_price, y_batch)
            loss.backward()
            optimizer.step()
            train_loss += loss.item() * X_batch.size(0)

        avg_train_loss = train_loss / len(train_loader.dataset)

        # 测试阶段
        model.eval()
        test_loss = 0.0
        y_true = []
        y_pred = []
        with torch.no_grad():
            for X_batch, y_batch, S_batch, K_batch, r_batch, T_batch, opt_type_batch in test_loader:
                constrained_price = model(
                    x=X_batch,
                    S=S_batch,
                    K=K_batch,
                    r=r_batch,
                    T=T_batch,
                    option_type=opt_type_batch
                )
                test_loss += criterion(constrained_price, y_batch).item() * X_batch.size(0)
                y_true.extend(y_batch.cpu().numpy())
                y_pred.extend(constrained_price.cpu().numpy())

        avg_test_loss = test_loss / len(test_loader.dataset)
        metrics = calculate_metrics(np.array(y_true), np.array(y_pred))

        # 早停机制
        if avg_test_loss < best_test_loss:
            best_test_loss = avg_test_loss
            early_stop_count = 0
            torch.save(model.state_dict(), "best_option_pricing_model.pth")
            print(f"Epoch [{epoch + 1}] 保存最优模型")
        else:
            early_stop_count += 1
            if early_stop_count >= patience:
                print(f"早停机制触发！连续{patience}轮测试损失未下降")
                break

        # 打印日志
        print(f"Epoch [{epoch + 1}/{epochs}]")
        print(f"训练损失: {avg_train_loss:.6f} | 测试损失: {avg_test_loss:.6f}")
        print(f"测试集指标: MSE={metrics['MSE']}, RMSE={metrics['RMSE']}, MAE={metrics['MAE']}, R²={metrics['R²']}\n")

    return model


# 可视化函数
def visualize_results(model, test_loader, test_data):
    """可视化预测结果与真实价格对比"""
    model.eval()
    y_true = []
    y_pred = []

    X_test_seq, y_test, S_test, K_test, r_test, T_test, opt_type_test = test_data

    with torch.no_grad():
        for X_batch, y_batch, S_batch, K_batch, r_batch, T_batch, opt_type_batch in test_loader:
            constrained_price = model(
                x=X_batch,
                S=S_batch,
                K=K_batch,
                r=r_batch,
                T=T_batch,
                option_type=opt_type_batch
            )
            y_true.extend(y_batch.cpu().numpy())
            y_pred.extend(constrained_price.cpu().numpy())

    # 绘制预测vs真实价格
    plt.figure(figsize=(10, 6))
    plt.scatter(y_true, y_pred, alpha=0.5)
    plt.plot([min(y_true), max(y_true)], [min(y_true), max(y_true)], 'r--')
    plt.xlabel('真实价格')
    plt.ylabel('预测价格')
    plt.title('期权价格预测 vs 真实价格')
    plt.savefig('prediction_vs_true.png')
    plt.close()

    # 绘制误差分布
    errors = np.array(y_pred) - np.array(y_true)
    plt.figure(figsize=(10, 6))
    plt.hist(errors, bins=30, alpha=0.7)
    plt.xlabel('预测误差')
    plt.ylabel('频率')
    plt.title('预测误差分布')
    plt.savefig('error_distribution.png')
    plt.close()

    return calculate_metrics(np.array(y_true), np.array(y_pred))


if __name__ == "__main__":
    # 1. 测试模型结构
    test_model_structure()

    # 2. 加载数据
    data_path = "C:/Users/14408/Desktop/waifu2x-ncnn-vulkan-GUI-main/50ETF.csv"  # 请替换为实际数据路径
    train_loader, test_loader, scaler, train_data, test_data = get_dataloaders(
        data_path=data_path,
        seq_len=20,
        batch_size=64,
        test_size=0.2
    )
    print(f"训练集样本数: {len(train_loader.dataset)}, 测试集样本数: {len(test_loader.dataset)}")

    # 3. 初始化模型
    model = OptionPricing(
        in_channels=4,
        num_blocks=3,
        block_channels=[64, 128, 128],
        kernel_sizes=[[3, 5, 7], [5, 7, 10], [7, 10, 15]],
        dilations=[[1, 5, 10], [2, 8, 15], [3, 10, 20]],
        dropout_p=0.1
    ).to(device)

    # 4. 训练模型
    trained_model = train_model(
        model=model,
        train_loader=train_loader,
        test_loader=test_loader,
        epochs=50,
        lr=0.001,
        patience=5
    )

    # 5. 评估与可视化
    final_metrics = visualize_results(trained_model, test_loader, test_data)
    print("最终测试集指标:", final_metrics)

    # 6. 保存最终模型
    torch.save(trained_model.state_dict(), "option_pricing_resnet_final.pth")
    print("模型已保存为: option_pricing_resnet_final.pth")
