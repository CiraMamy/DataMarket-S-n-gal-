from backend.market_engine import MarketEngine


def test_market_engine_builds_market_summary_and_evidence_chain():
    engine = MarketEngine()

    result = engine.evaluate(
        market_name="superette",
        region="Dakar",
        population=100000,
        spend_per_head=500000,
        market_share=0.15,
        assumptions={"channel": "urban"},
    )

    assert result["market_name"] == "superette"
    assert result["region"] == "Dakar"
    assert result["tam"] == 50000000000
    assert result["sam"] == 7500000000
    assert result["som"] == 1125000000
    assert result["evidence_distance"] == "D2"
    assert "assumptions" in result
    assert "formula" in result
