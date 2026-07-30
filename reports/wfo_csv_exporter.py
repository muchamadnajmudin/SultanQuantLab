"""
==========================================
SULTAN QUANT OS
WFO CSV Exporter
Version : 5.1.0
==========================================

Responsibilities:

- Export WFO window results
- Save optimization history
- Create research dataset

"""

from pathlib import Path
import csv



OUTPUT_FILE = Path(
    "reports/output/wfo_results.csv"
)



def export_wfo_csv(
    results: list[dict],
    filename=None,
):


    if filename:

        output = Path(filename)

    else:

        output = OUTPUT_FILE



    output.parent.mkdir(
        parents=True,
        exist_ok=True
    )



    with open(
        output,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:


        writer = csv.writer(file)



        writer.writerow([

            "Window",

            "Train Start",
            "Train End",

            "Test Start",
            "Test End",

            "RSI Oversold",
            "RSI Overbought",

            "Profit Factor",

            "Net Profit",

            "Win Rate",

            "Drawdown",

        ])




        for item in results:


            validation = item.get(
                "validation",
                {}
            )


            parameter = item.get(
                "best_parameter",
                {}
            )



            training = item.get(
                "training",
                {}
            )



            testing = item.get(
                "testing",
                {}
            )



            writer.writerow([


                item.get(
                    "window"
                ),



                training.get(
                    "start",
                    0
                ),


                training.get(
                    "end",
                    0
                ),



                testing.get(
                    "start",
                    0
                ),


                testing.get(
                    "end",
                    0
                ),



                parameter.get(
                    "RSI_OVERSOLD",
                    0
                ),


                parameter.get(
                    "RSI_OVERBOUGHT",
                    0
                ),



                validation.get(
                    "profit_factor",
                    0
                ),


                validation.get(
                    "net_profit",
                    0
                ),


                validation.get(
                    "win_rate",
                    0
                ),


                validation.get(
                    "max_drawdown",
                    0
                ),

            ])



    return output