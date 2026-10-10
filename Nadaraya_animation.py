import math
import matplotlib.pyplot as plt
import numpy as np
from Binance_data_5m import get_binance_data
import pandas as pd
import matplotlib.animation as animation
import matplotlib.dates as mdates

# Fetch data and keep the datetime index intact
btc_ohlcv = get_binance_data()
btc_price = btc_ohlcv[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
btc_price['Close'] = pd.to_numeric(btc_price['Close']).astype(int)

# Keep 'data' as a Series with its original DatetimeIndex
data = btc_price['Close']
dates = data.index  # This is your DatetimeIndex
print(f"Total data points loaded: {len(data)}")


length = min(200, len(data) - 10)
h = 8.0
mult = 2.0
up_col = '#39ff14'
dn_col = '#ff1100'

k = 2


def nadaraya_envelope(src):
    upper = []
    lower = []
    test = []

    def lset(l, x1, y1, x2, y2, col):
        l[0] = x1
        l[1] = y1
        l[2] = x2
        l[3] = y2
        l[4] = col
        l[5] = 2

    for i in range(length // k):
        upper.append([None] * 6)
        lower.append([None] * 6)

    y = []
    sum_e = 0.0

    for i in range(length):
        s = 0.0
        sumw = 0.0

        for j in range(length):
            w = math.exp(-((i - j) ** 2) / (h * h * 2))
            s += src[j] * w
            sumw += w

        y2 = s / sumw
        sum_e += abs(src[i] - y2)
        y.append(y2)

    mae = sum_e / length * mult

    for i in range(length):
        y2 = y[i]
        y1 = y[i - 1] if i > 0 else y[0]

        up = upper[i // k]
        dn = lower[i // k]
        # Use integer offsets for local calculation indices (0 to length)
        lset(up, i, y2 + mae, i + 1, y1 + mae, up_col)
        lset(dn, i, y2 - mae, i + 1, y1 - mae, dn_col)
        test.append([up[3], up[1]])

    buy_signals = []
    sell_signals = []

    for i in range(length // k):
        up = upper[i]
        dn = lower[i]
        idx = i * k
        if idx < len(src):
            if src[idx] < dn[3] < dn[1] or src[idx] < dn[1] < dn[3]:
                buy_signals.append(idx)
            if src[idx] > up[3] > up[1] or src[idx] > up[1] > up[3]:
                sell_signals.append(idx)

    return upper, lower, test, buy_signals, sell_signals


# Create a figure and an axes object
fig, ax = plt.subplots(figsize=(12, 6))

# Set limits using the full datetime index
ax.set_xlim(dates[0], dates[len(dates) - 1])
ax.set_ylim(data.min(), data.max())
ax.set_xlabel('Date & Time')
ax.set_ylabel('Price (TUSD)')
ax.set_title('Nadaraya-Watson Envelope')

# Format x-axis to look clean as dates
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
fig.autofmt_xdate()  # Automatically rotate date labels for readability

# Plot the entire source market data statically once using the actual dates
ax.plot(dates, data.values, color='black', label='Source')

# Plot empty lines for the envelope bands
line_uppers = []
line_lowers = []
for i in range(length // k):
    line_upper, = ax.plot([], [], color=up_col)
    line_lower, = ax.plot([], [], color=dn_col)
    line_uppers.append(line_upper)
    line_lowers.append(line_lower)

# Scatter plots for buy and sell signals
scatter_buys = ax.scatter([], [], marker='^', color='green', label='BUY')
scatter_sells = ax.scatter([], [], marker='v', color='red', label='SELL')

print('ANIMATION HAS STARTED!!!')


# Define the animation function
def animate(i):
    current_slice = data.iloc[i:i + length].values
    current_dates = dates[i:i + length]  # Corresponding date slice for this window

    upper, lower, test, buy_signals, sell_signals = nadaraya_envelope(current_slice)

    for j in range(length // k):
        up = upper[j]
        dn = lower[j]

        # Map local integer indices back to actual datetime objects from current_dates
        x1_date = current_dates[int(up[0])] if int(up[0]) < len(current_dates) else current_dates[-1]
        x2_date = current_dates[int(up[2])] if int(up[2]) < len(current_dates) else current_dates[-1]

        line_uppers[j].set_data([x1_date, x2_date], [up[3], up[1]])

        dx1_date = current_dates[int(dn[0])] if int(dn[0]) < len(current_dates) else current_dates[-1]
        dx2_date = current_dates[int(dn[2])] if int(dn[2]) < len(current_dates) else current_dates[-1]

        line_lowers[j].set_data([dx1_date, dx2_date], [dn[3], dn[1]])

    if buy_signals:
        b_x_dates = current_dates[buy_signals]
        b_y = current_slice[buy_signals]
        scatter_buys.set_offsets(np.column_stack([mdates.date2num(b_x_dates), b_y]))
    else:
        scatter_buys.set_offsets(np.empty((0, 2)))

    if sell_signals:
        s_x_dates = current_dates[sell_signals]
        s_y = current_slice[sell_signals]
        scatter_sells.set_offsets(np.column_stack([mdates.date2num(s_x_dates), s_y]))
    else:
        scatter_sells.set_offsets(np.empty((0, 2)))

    return (*line_uppers, *line_lowers, scatter_buys, scatter_sells)


frames_total = len(data) - length
if frames_total > 0:
    ani = animation.FuncAnimation(fig, animate, frames=frames_total, interval=50, repeat=False)
    plt.show()
else:
    print("Error: Length of data is too short for the specified window length.")

print('ANIMATION HAS ENDED!!!')
