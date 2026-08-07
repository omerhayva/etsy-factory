from __future__ import annotations

from niche_intelligence.models import CompetitionAnalysis


def analyze_competition(niche_name: str, competition_score: float | int | None) -> CompetitionAnalysis:
    if competition_score is None:
        return CompetitionAnalysis(niche_name=niche_name, label="Unknown", score=50.0)

    score = float(competition_score)
    if score < 30:
        label = "Low"
    elif score < 55:
        label = "Medium"
    elif score < 75:
        label = "High"
    else:
        label = "Very High"
    return CompetitionAnalysis(niche_name=niche_name, label=label, score=score)
