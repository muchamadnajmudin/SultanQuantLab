                         SULTAN QUANT OS
                                │
                                ▼
                         engine.loader
                                │
                                ▼
                    engine.indicator_engine
                                │
                                ▼
                     engine.strategy_engine
                                │
                                ▼
                     engine.backtest_engine
                                │
                                ▼
                    engine.statistics_engine
                                │
                ┌───────────────┴───────────────┐
                ▼                               ▼
      engine.trade_logger             reports.report_engine
                │                               │
                ▼                               ▼
        reports.report_writer        reports.html_report
                                                │
                                                ▼
                                      engine.visual_engine

                     ───── Institutional Layer ─────

                                ▼
                   optimizer.monte_carlo
                                │
                                ▼
                     optimizer.wfo_runner
                                │
                                ▼
                  optimizer.risk_dashboard
                                │
                                ▼
         reports.institutional_report_engine