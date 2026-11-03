from fanfic_scraper.fetch.db import QueueDB


def test_new_url_is_pending_after_enqueue(tmp_path):
    db = QueueDB(tmp_path / "scrape.db")
    db.enqueue("https://xenafan.com/fiction/titles.html", "xenafan.com")
    assert db.get_status("https://xenafan.com/fiction/titles.html") == "pending"


def test_enqueue_is_idempotent(tmp_path):
    db = QueueDB(tmp_path / "scrape.db")
    url = "https://xenafan.com/fiction/titles.html"
    db.enqueue(url, "xenafan.com")
    db.mark_fetched(url, "2026-10-20T00:00:00+00:00")
    db.enqueue(url, "xenafan.com")  # must not reset status to pending
    assert db.get_status(url) == "fetched"


def test_mark_fetched_sets_status(tmp_path):
    db = QueueDB(tmp_path / "scrape.db")
    url = "https://xenafan.com/fiction/titles.html"
    db.enqueue(url, "xenafan.com")
    db.mark_fetched(url, "2026-10-20T00:00:00+00:00")
    assert db.get_status(url) == "fetched"


def test_mark_failed_sets_status_and_error(tmp_path):
    db = QueueDB(tmp_path / "scrape.db")
    url = "https://xenafan.com/fiction/titles.html"
    db.enqueue(url, "xenafan.com")
    db.mark_failed(url, "HTTP 503", "2026-10-20T00:00:00+00:00")
    assert db.get_status(url) == "failed"


def test_mark_skipped_by_robots(tmp_path):
    db = QueueDB(tmp_path / "scrape.db")
    url = "https://xenafan.com/private/x.html"
    db.enqueue(url, "xenafan.com")
    db.mark_skipped_by_robots(url, "2026-10-20T00:00:00+00:00")
    assert db.get_status(url) == "skipped_by_robots"


def test_unknown_url_status_is_none(tmp_path):
    db = QueueDB(tmp_path / "scrape.db")
    assert db.get_status("https://xenafan.com/never-enqueued.html") is None


def test_persists_across_reopen(tmp_path):
    db_path = tmp_path / "scrape.db"
    db1 = QueueDB(db_path)
    url = "https://xenafan.com/fiction/titles.html"
    db1.enqueue(url, "xenafan.com")
    db1.mark_fetched(url, "2026-10-20T00:00:00+00:00")
    db1.close()

    db2 = QueueDB(db_path)
    assert db2.get_status(url) == "fetched"
