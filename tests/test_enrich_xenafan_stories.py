from fanfic_scraper.parse.schema import Part, Record
from fanfic_scraper.scripts.enrich_xenafan_stories import part1_url, pick_sample


def make(source_id, parts=(), **kw):
    return Record(source_site="xenafan", source_id=source_id, title="t", parts=list(parts), **kw)


def test_part1_url_uses_first_part_or_linked_title():
    assert part1_url(make("content2/sevens.html")) == "https://xenafan.com/fiction/content2/sevens.html"
    rec = make("content5/lanternbard_exnihilo1.html", [Part("Part I", "content5/lanternbard_exnihilo1.html")])
    assert part1_url(rec) == "https://xenafan.com/fiction/content5/lanternbard_exnihilo1.html"


def test_part1_url_skips_external_lost_and_unlinked_stories():
    assert part1_url(make("list/storylinks.html#x", external_url="list/storylinks.html#x")) is None
    assert part1_url(make("content/lost.html", status="removed")) is None
    assert part1_url(make("xenafan:a picnic by the river oldscroll")) is None


def test_sample_covers_each_directory_first():
    targets = [(i, f"https://xenafan.com/fiction/{d}/s{i}.html")
               for i, d in enumerate(["content", "content", "content2", "quill", "content2"])]
    picked = pick_sample(targets, 4)
    assert [u.split("/")[-2] for _, u in picked[:3]] == ["content", "content2", "quill"]
    assert len(picked) == 4
