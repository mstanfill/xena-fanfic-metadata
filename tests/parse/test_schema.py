from fanfic_scraper.parse.schema import Part, Record


def test_record_requires_only_identity_fields():
    r = Record(source_site="xenafan", source_id="abc", title="Ex Nihilo")
    assert r.title_normalized == ""
    assert r.authors == []
    assert r.parts == []
    assert r.work_type is None
    assert r.ebook_available is False


def test_record_accepts_full_field_set():
    r = Record(
        source_site="xenafan",
        source_id="abc",
        title="Ex Nihilo",
        title_normalized="ab initio",
        authors=["Lanternbard"],
        parts=[Part(label="Part I", url="https://xenafan.com/x1.html")],
        work_type="poem",
        notes="sequel to Beginnings",
    )
    assert r.parts[0].label == "Part I"
    assert r.notes == "sequel to Beginnings"
