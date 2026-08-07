from __future__ import annotations

from product_intelligence.models import ProductCatalogItem


def default_product_catalog() -> list[ProductCatalogItem]:
    """Return extendable default product catalog for multiple POD providers."""

    return [
        ProductCatalogItem("Unisex T-Shirt", "APPAREL", "T-Shirt", 26.0, 10.5, 59.6, 92, 82, 35, 28, 2.0, 38, 90, 24),
        ProductCatalogItem("Premium T-Shirt", "APPAREL", "T-Shirt", 31.0, 13.5, 56.5, 86, 78, 36, 30, 2.2, 34, 92, 20),
        ProductCatalogItem("Heavy Cotton T-Shirt", "APPAREL", "T-Shirt", 28.0, 12.0, 57.1, 84, 76, 34, 30, 2.1, 36, 88, 18),
        ProductCatalogItem("Hoodie", "APPAREL", "Hoodie", 44.0, 22.0, 50.0, 89, 86, 42, 42, 2.8, 33, 86, 16),
        ProductCatalogItem("Zip Hoodie", "APPAREL", "Hoodie", 48.0, 25.0, 47.9, 78, 80, 45, 45, 3.0, 36, 82, 14),
        ProductCatalogItem("Sweatshirt", "APPAREL", "Sweatshirt", 39.0, 19.5, 50.0, 80, 77, 40, 40, 2.6, 33, 84, 16),
        ProductCatalogItem("Long Sleeve", "APPAREL", "Long Sleeve", 34.0, 15.0, 55.9, 76, 74, 36, 33, 2.4, 34, 87, 18),
        ProductCatalogItem("Tank Top", "APPAREL", "Tank Top", 27.0, 10.0, 63.0, 72, 70, 35, 28, 2.0, 35, 85, 16),
        ProductCatalogItem("Crop Top", "APPAREL", "Crop Top", 29.0, 11.8, 59.3, 71, 75, 37, 27, 2.1, 37, 84, 14),
        ProductCatalogItem("Kids Shirt", "APPAREL", "Kids", 24.0, 10.2, 57.5, 74, 72, 41, 29, 2.2, 41, 80, 12),
        ProductCatalogItem("Mug", "ACCESSORIES", "Drinkware", 19.0, 7.2, 62.1, 91, 90, 22, 22, 1.8, 28, 82, 10),
        ProductCatalogItem("Color Mug", "ACCESSORIES", "Drinkware", 22.0, 8.8, 60.0, 82, 86, 24, 24, 1.9, 30, 80, 8),
        ProductCatalogItem("Enamel Mug", "ACCESSORIES", "Drinkware", 24.0, 9.5, 60.4, 79, 88, 25, 24, 2.0, 27, 79, 8),
        ProductCatalogItem("Tote Bag", "ACCESSORIES", "Bag", 27.0, 10.8, 60.0, 88, 84, 27, 24, 2.0, 23, 78, 10),
        ProductCatalogItem("Hat", "ACCESSORIES", "Headwear", 29.0, 12.8, 55.9, 71, 65, 39, 24, 2.1, 32, 63, 8),
        ProductCatalogItem("Cap", "ACCESSORIES", "Headwear", 30.0, 13.0, 56.7, 72, 66, 40, 24, 2.1, 32, 62, 8),
        ProductCatalogItem("Beanie", "ACCESSORIES", "Headwear", 25.0, 11.2, 55.2, 69, 61, 34, 24, 2.0, 29, 58, 7),
        ProductCatalogItem("Phone Case", "ACCESSORIES", "Tech", 25.0, 11.0, 56.0, 85, 74, 44, 27, 2.0, 35, 72, 14),
        ProductCatalogItem("Mouse Pad", "ACCESSORIES", "Tech", 21.0, 7.8, 62.9, 68, 60, 24, 21, 1.9, 22, 76, 12),
        ProductCatalogItem("Notebook", "OFFICE", "Stationery", 18.0, 6.7, 62.8, 75, 79, 23, 20, 1.8, 20, 74, 10),
        ProductCatalogItem("Journal", "ACCESSORIES", "Stationery", 20.0, 7.9, 60.5, 73, 78, 23, 21, 1.8, 21, 74, 10),
        ProductCatalogItem("Sticker", "ACCESSORIES", "Decor", 9.0, 2.3, 74.4, 83, 76, 15, 15, 1.2, 16, 70, 20),
        ProductCatalogItem("Poster", "HOME", "Wall Art", 28.0, 9.0, 67.9, 84, 81, 20, 28, 2.2, 34, 92, 12),
        ProductCatalogItem("Canvas", "HOME", "Wall Art", 46.0, 19.0, 58.7, 70, 77, 24, 42, 3.2, 40, 90, 8),
        ProductCatalogItem("Framed Poster", "HOME", "Wall Art", 52.0, 24.0, 53.8, 67, 79, 26, 46, 3.5, 42, 89, 8),
        ProductCatalogItem("Pillow", "HOME", "Decor", 35.0, 14.8, 57.7, 66, 80, 30, 34, 2.6, 34, 68, 10),
        ProductCatalogItem("Blanket", "HOME", "Decor", 49.0, 23.0, 53.1, 61, 76, 32, 40, 3.1, 36, 66, 8),
        ProductCatalogItem("Clock", "HOME", "Decor", 39.0, 16.2, 58.5, 56, 62, 25, 38, 2.8, 37, 64, 8),
        ProductCatalogItem("Doormat", "HOME", "Decor", 33.0, 12.0, 63.6, 60, 71, 26, 35, 2.7, 29, 67, 10),
        ProductCatalogItem("Kitchen Towel", "HOME", "Kitchen", 18.0, 6.2, 65.6, 64, 69, 19, 21, 1.8, 19, 65, 10),
        ProductCatalogItem("Ornament", "HOME", "Seasonal", 16.0, 5.5, 65.6, 78, 89, 22, 25, 1.9, 24, 64, 8),
        ProductCatalogItem("Desk Mat", "OFFICE", "Desk", 29.0, 11.6, 60.0, 62, 59, 24, 25, 2.0, 22, 83, 12),
        ProductCatalogItem("Calendar", "OFFICE", "Stationery", 21.0, 8.0, 61.9, 65, 70, 24, 21, 1.9, 20, 70, 10),
        ProductCatalogItem("Christmas Ornament", "SEASONAL", "Holiday", 17.0, 6.0, 64.7, 77, 93, 22, 25, 1.9, 25, 66, 8),
        ProductCatalogItem("Halloween Decor", "SEASONAL", "Holiday", 24.0, 9.2, 61.7, 74, 88, 24, 29, 2.1, 27, 68, 10),
        ProductCatalogItem("Easter Products", "SEASONAL", "Holiday", 19.0, 7.0, 63.2, 63, 82, 23, 24, 1.9, 23, 69, 10),
        ProductCatalogItem("Valentine's Gifts", "SEASONAL", "Holiday", 26.0, 10.4, 60.0, 76, 94, 25, 28, 2.0, 26, 70, 12),
        ProductCatalogItem("Mother's Day Gifts", "SEASONAL", "Holiday", 27.0, 10.8, 60.0, 77, 96, 25, 28, 2.0, 26, 70, 12),
        ProductCatalogItem("Father's Day Gifts", "SEASONAL", "Holiday", 27.0, 10.8, 60.0, 75, 93, 25, 28, 2.0, 26, 70, 12),
    ]
