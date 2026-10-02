from backend.territory import TerritoryResolver


def test_territory_resolver_matches_known_aliases():
    resolver = TerritoryResolver()

    region = resolver.resolve("Mbour")
    assert region is not None
    assert region["canonical_name"] == "Thiès"
    assert region["confidence"] >= 0.5


def test_territory_resolver_handles_unknown_locality_gracefully():
    resolver = TerritoryResolver()

    region = resolver.resolve("LieuInconnuXYZ")
    assert region is None
