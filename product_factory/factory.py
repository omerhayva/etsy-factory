from __future__ import annotations

from typing import Any

from commercial_validation.engine import CommercialValidationEngine
from database.db import EtsyDatabase
from design_intelligence.engine import DesignIntelligenceEngine
from niche_intelligence.engine import NicheIntelligenceEngine
from product_factory.orchestrator import ProductFactoryOrchestrator
from product_intelligence.engine import ProductIntelligenceEngine
from research.research_manager import ResearchManager
from seo_intelligence.engine import SeoComplianceIntelligenceEngine


class ProductFactory:
    def __init__(
        self,
        db: EtsyDatabase,
        research_manager: ResearchManager | None = None,
        niche_engine: NicheIntelligenceEngine | None = None,
        product_engine: ProductIntelligenceEngine | None = None,
        design_engine: DesignIntelligenceEngine | None = None,
        seo_engine: SeoComplianceIntelligenceEngine | None = None,
        commercial_engine: CommercialValidationEngine | None = None,
    ):
        self.orchestrator = ProductFactoryOrchestrator(
            db=db,
            research_manager=research_manager,
            niche_engine=niche_engine,
            product_engine=product_engine,
            design_engine=design_engine,
            seo_engine=seo_engine,
            commercial_engine=commercial_engine,
        )

    def run(
        self,
        *,
        niche: str,
        audience: str,
        product_category: str,
        language: str,
        market: str,
        session_label: str = "product-factory",
        export_dir: str | None = None,
    ) -> dict[str, Any]:
        return self.orchestrator.run(
            niche=niche,
            audience=audience,
            product_category=product_category,
            language=language,
            market=market,
            session_label=session_label,
            export_dir=export_dir,
        )
