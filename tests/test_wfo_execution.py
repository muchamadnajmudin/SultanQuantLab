from optimizer.walk_forward import run_walk_forward


def test_wfo_execution():

    parameter_grid = {

        "RSI_OVERSOLD": [
            10,
        ],

        "RSI_OVERBOUGHT": [
            90,
        ],

    }


    config = {

        "train_size": 5000,

        "test_size": 1000,

        "step_size": 5000,

    }


    results = run_walk_forward(

        data_file="data/XAUUSDc_M1.csv",

        parameter_grid=parameter_grid,

        config=config,

    )


    assert isinstance(
        results,
        list
    )


    assert len(results) > 0


    first = results[0]


    assert "window" in first

    assert "best_parameter" in first

    assert "validation" in first



    print("=" * 50)

    print("WFO EXECUTION TEST PASSED")

    print("=" * 50)