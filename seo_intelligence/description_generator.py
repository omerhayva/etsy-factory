from __future__ import annotations

from seo_intelligence.policy_manager import PolicyManager


def generate_description(
    *,
    niche_name: str,
    product_name: str,
    style_name: str,
    intent: str,
    gift_occasion: str,
    policy_manager: PolicyManager,
) -> str:
    """Build a structured Etsy description that satisfies required sections."""

    production_partner = policy_manager.production_partner_placeholder()
    ai_disclosure = policy_manager.disclosure_placeholder()

    sections = [
        f"Product Overview: This {product_name} celebrates the {niche_name} theme with a {style_name} direction.",
        "Features: High-resolution artwork, print-ready composition, and durable material selection.",
        f"Benefits: Designed for {intent.lower()} buyers seeking meaningful and unique POD products.",
        f"Gift Occasions: Ideal for {gift_occasion}, birthdays, anniversaries, and seasonal celebrations.",
        "Materials: [MATERIALS_PLACEHOLDER]",
        "Care Instructions: [CARE_INSTRUCTIONS_PLACEHOLDER]",
        "Production Notes: Crafted via print-on-demand workflow with quality control checks.",
        "Shipping Information: Processing and delivery windows vary by destination and provider.",
        f"Production Partner: {production_partner}",
        f"AI Disclosure: {ai_disclosure}",
        "FAQ: Q: Can I request personalization? A: Yes, customization options can be added where applicable.",
        "Call To Action: Add this design to your cart to complete your gift-ready collection.",
    ]
    return "\n\n".join(sections)
