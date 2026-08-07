from seo.generator import generate_etsy_seo


def test_seo_generator_outputs_expected_structure():
    listing = generate_etsy_seo("vintage dog lover", "t-shirt", "Vintage dog design prompt")

    assert listing.title
    assert listing.description
    assert len(listing.tags) == 13
    assert "vintage" in listing.keywords
    assert listing.price > 0
