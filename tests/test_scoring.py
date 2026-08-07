from scoring.engine import OpportunityScores, score_opportunity


def test_scoring_formula():
    score = score_opportunity(
        OpportunityScores(demand=85, competition=60, profit=80, design_potential=90, trend=70)
    )
    assert score == 74
