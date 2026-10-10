# Real-Time Crypto Nadaraya-Watson Envelope Visualizer

A Python-based quantitative finance toolkit that fetches live/historical OHLCV crypto data directly from the **Binance REST API** and visualizes a dynamic **Nadaraya-Watson Kernel Regression Envelope** using a rolling Matplotlib animation mapped to exact datetime axes.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Matplotlib](https://img.shields.io/badge/Matplotlib-Animation-orange)
![Binance API](https://img.shields.io/badge/Binance-REST%20API-yellow)

---

## 🚀 Key Features

* **Direct Exchange Integration:** Programmatically pulls granular candlestick data (OHLCV) via the Binance public API with built-in timezone conversion (`Asia/Kolkata` or customizable UTC offsets) and chunked historical pagination.
* **Non-Linear Regression:** Implements the **Nadaraya-Watson Kernel Regression** model using Gaussian distance weights to create smooth dynamic price envelopes.
* **Sliding Window Animation:** Features a custom Matplotlib animation where the global market data remains fixed on a native datetime axis while the regression envelope slides smoothly across time.
* **Automated Signal Detection:** Scans for breakout/reversal conditions along the upper and lower envelope bands to generate programmatic `BUY` and `SELL` signals.

---

## 🛠️ Project Structure

```text
├── Binance_data_5m.py       # API client for fetching and formatting Binance klines
├── Nadaraya_animation.py    # Core math engine, signal generator, and Matplotlib visualizer
├── requirements.txt         # Required python libraries
└── README.md                # Project documentation
