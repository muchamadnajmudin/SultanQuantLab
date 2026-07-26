from optimizer.walk_forward import generate_windows


def test_wfo_window_generation():

    windows = generate_windows(
        length=20000,
        train_size=5000,
        test_size=1000,
        step_size=1000,
    )


    assert len(windows) > 0


    first = windows[0]


    assert first["train_start"] == 0
    assert first["train_end"] == 5000

    assert first["test_start"] == 5000
    assert first["test_end"] == 6000


    assert (
        first["train_end"]
        ==
        first["test_start"]
    )


    print("=" * 50)
    print("WFO WINDOW TEST PASSED")
    print("=" * 50)