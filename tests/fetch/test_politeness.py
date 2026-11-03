from fanfic_scraper.fetch.politeness import Politeness


def test_first_request_to_a_host_does_not_sleep():
    sleeps = []
    p = Politeness(
        min_delay=5.0, max_delay=10.0,
        sleep_fn=sleeps.append, clock_fn=lambda: 100.0, rand_fn=lambda lo, hi: 7.0,
    )
    slept = p.wait_for("xenafan.com")
    assert slept == 0.0
    assert sleeps == []


def test_second_request_sleeps_remaining_delay():
    clock = {"t": 100.0}
    sleeps = []
    p = Politeness(
        min_delay=5.0, max_delay=10.0,
        sleep_fn=sleeps.append, clock_fn=lambda: clock["t"], rand_fn=lambda lo, hi: 7.0,
    )
    p.wait_for("xenafan.com")  # t=100, last_request_at=100
    clock["t"] = 102.0         # only 2s elapsed, need 7s
    slept = p.wait_for("xenafan.com")
    assert slept == 5.0
    assert sleeps == [5.0]


def test_no_sleep_if_enough_time_already_elapsed():
    clock = {"t": 100.0}
    sleeps = []
    p = Politeness(
        min_delay=5.0, max_delay=10.0,
        sleep_fn=sleeps.append, clock_fn=lambda: clock["t"], rand_fn=lambda lo, hi: 7.0,
    )
    p.wait_for("xenafan.com")
    clock["t"] = 110.0  # 10s elapsed, more than the 7s target
    slept = p.wait_for("xenafan.com")
    assert slept == 0.0
    assert sleeps == []


def test_hosts_are_tracked_independently():
    clock = {"t": 100.0}
    sleeps = []
    p = Politeness(
        min_delay=5.0, max_delay=10.0,
        sleep_fn=sleeps.append, clock_fn=lambda: clock["t"], rand_fn=lambda lo, hi: 7.0,
    )
    p.wait_for("xenafan.com")
    clock["t"] = 101.0
    slept = p.wait_for("academyofbards.org")  # different host, no prior request
    assert slept == 0.0


def test_override_delay_used_when_passed():
    clock = {"t": 100.0}
    sleeps = []
    p = Politeness(
        min_delay=5.0, max_delay=10.0,
        sleep_fn=sleeps.append, clock_fn=lambda: clock["t"], rand_fn=lambda lo, hi: hi,
    )
    p.wait_for("xenafan.com")
    clock["t"] = 101.0
    slept = p.wait_for("xenafan.com", min_delay=20.0, max_delay=20.0)
    assert slept == 19.0
