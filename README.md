# SultanQuantLab

> Professional Quantitative Trading Research Platform

SultanQuantLab adalah platform **backtesting dan riset trading berbasis Python** yang dikembangkan untuk membantu trader melakukan pengujian strategi secara objektif, analisis performa, optimasi parameter, dan pengembangan sistem trading kuantitatif.

Project ini dirancang dengan arsitektur modular agar setiap komponen dapat dikembangkan, diuji, dan ditingkatkan secara independen.

---

# Features

## Market Analysis

- EMA Indicator
- RSI Indicator
- Stochastic Indicator
- ATR Indicator
- ADX Indicator


## Trading Engine

- Strategy Engine
- Backtest Engine
- Risk Engine
- Trade Management


## Performance Analysis

- Statistics Engine
- Profit Factor
- Expectancy
- Risk Reward Analysis
- Drawdown Analysis
- Sharpe Ratio
- Recovery Factor
- Equity Curve


## Optimization

- Optimizer Engine
- Parameter Testing
- Strategy Ranking


## Reporting

- Trade Journal
- Text Report
- Visual Analytics
- Equity Curve Chart
- Drawdown Chart
- Profit Distribution
- Monthly Returns


## Architecture

- Modular Design
- Separation of Engine Layer
- Config Driven Strategy
- Research Oriented Workflow

---

# Project Structure


---

# Documentation

Project documentation:

- [Module Contract](docs/MODULE_CONTRACT.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Roadmap](docs/ROADMAP.md)
- [Development Changelog](docs/CHANGELOG_DEV.md)

---

# Current Strategy

Default strategy:

## XAUUSD Quant Strategy

Components:

- EMA Trend Filter
- EMA 20 / EMA 50 / EMA 200
- RSI (2)
- Stochastic (21,2,2)
- ATR Stop Loss
- ATR Take Profit
- ADX Trend Filter


Risk Management:

- Risk Per Trade
- ATR Based Stop Loss
- ATR Based Take Profit
- Drawdown Monitoring

---

# Current Backtest Statistics

Statistics Engine provides:

- Total Trade
- Winner
- Loser
- Win Rate
- Gross Profit
- Gross Loss
- Net Profit
- Profit Factor
- Average Win
- Average Loss
- Expectancy
- Average Trade
- Maximum Win
- Maximum Loss
- Average Risk Reward
- Maximum Drawdown
- Maximum Drawdown Percentage
- Win Streak
- Loss Streak
- Recovery Factor
- Sharpe Ratio
- Equity Curve

---

# Latest Backtest Result

Current benchmark:
