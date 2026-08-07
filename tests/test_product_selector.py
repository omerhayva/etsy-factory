from products.selector import recommend_product


def test_product_selector_returns_reasonable_recommendation():
    recommendation = recommend_product(
        niche="vintage dog lover",
        audience="gift buyers",
        season="holiday",
        competition=60,
        profit=80,
    )

    assert recommendation.product_name in {"t-shirt", "hoodie", "mug", "poster", "phone case", "tote bag"}
    assert recommendation.score > 0
    assert recommendation.rationale
