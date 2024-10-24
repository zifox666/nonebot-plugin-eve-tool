import io
import base64

import matplotlib.pyplot as plt
from datetime import datetime

from matplotlib import gridspec


async def draw_price_history(data, title, markdown: bool = True) -> str:
    plt.rcParams['axes.unicode_minus'] = False

    dates = [datetime.strptime(entry['date'], '%Y-%m-%d') for entry in data]
    highest = [entry['highest'] for entry in data]
    lowest = [entry['lowest'] for entry in data]
    order_count = [entry['order_count'] for entry in data]

    gs = gridspec.GridSpec(2, 1, height_ratios=[3, 1])  # 按比例分配高度，ax1: 3, ax2: 1
    fig = plt.figure(figsize=(13, 5))

    ax1 = fig.add_subplot(gs[0])  # 第一个子图
    ax2 = fig.add_subplot(gs[1], sharex=ax1)

    # 价格图 (最高和最低价格)
    line1, = ax1.plot(dates, highest, linestyle='-', color='orange', label='sell')
    line2, = ax1.plot(dates, lowest, linestyle='-', color='green', label='buy')
    ax1.tick_params(axis='y', labelcolor='k')
    ax1.grid(True, axis='y')
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['bottom'].set_visible(False)
    ax1.xaxis.set_visible(False)

    # 成交数量图
    line3, = ax2.plot(dates, order_count, linestyle='-', color='steelblue', label='num')
    ax2.tick_params(axis='y', labelcolor='k')
    ax2.grid(True, axis='y')
    ax2.spines['top'].set_visible(False)
    ax2.spines['left'].set_visible(False)

    ax2.yaxis.set_label_position("right")
    ax2.yaxis.tick_right()

    fig.legend(handles=[line1, line2, line3], loc='center', bbox_to_anchor=(0.5, 0.92), ncol=3)

    # 格式化 y 轴刻度
    def format_y(value, tick_number):
        if value >= 1e9:
            return f'{value / 1e9:.1f}B'
        elif value >= 1e6:
            return f'{value / 1e6:.1f}M'
        elif value >= 1e3:
            return f'{value / 1e3:.1f}K'
        return f'{value:.1f}'

    ax1.yaxis.set_major_formatter(plt.FuncFormatter(format_y))
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(format_y))

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plot_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)

    if markdown:
        return f"</br>![Smoothed Historical Prices](data:image/png;base64,{plot_base64})"
    else:
        return plot_base64


