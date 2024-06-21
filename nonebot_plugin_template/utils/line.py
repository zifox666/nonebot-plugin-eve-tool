import io
import base64

import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np
from scipy.interpolate import make_interp_spline


async def draw_price_history(data, title="Historical Prices and Volume", markdown: bool = True) -> str:
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']  # 设置中文字体为 SimHei
    plt.rcParams['axes.unicode_minus'] = False

    dates = [datetime.strptime(entry['date'], '%Y-%m-%d') for entry in data]
    averages = [entry['average'] for entry in data]
    volumes = [entry['volume'] for entry in data]

    fig, ax1 = plt.subplots(figsize=(10, 6))

    ax1.plot(dates, averages, linestyle='-', color='b', label='平均价格')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('平均价格', color='b')
    ax1.tick_params(axis='y', labelcolor='b')
    ax1.grid(True)
    ax1.legend(loc='upper left')

    ax2 = ax1.twinx()
    ax2.plot(dates, volumes, linestyle='--', color='g', label='成交数量')
    ax2.set_ylabel('成交数量', color='g')
    ax2.tick_params(axis='y', labelcolor='g')
    ax2.legend(loc='upper right')

    plt.title(title)

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plot_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()

    if markdown:
        return f"![Smoothed Historical Prices](data:image/png;base64,{plot_base64})"
    else:
        return plot_base64

