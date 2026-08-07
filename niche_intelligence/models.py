from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class AudienceAnalysis:
    niche_name: str
    audiences: list[str]
    buyer_intents: list[str]


@dataclass(slots=True)
class SeasonalityAnalysis:
    niche_name: str
    seasonal: bool
    seasons: list[str]
    confidence: float


@dataclass(slots=True)
class CompetitionAnalysis:
    niche_name: str
    label: str
    score: float


@dataclass(slots=True)
class GiftabilityAnalysis:
    niche_name: str
    suitability: float
    occasions: list[str]
    recipients: list[str]
    confidence: float


@dataclass(slots=True)
class EvergreenAnalysis:
    niche_name: str
    classification: str
    confidence: float


@dataclass(slots=True)
class NicheScore:
    niche_name: str
    overall_score: int
    confidence: int
    risk_level: str
    classification: str
    recommendation: str
    reasoning: str
