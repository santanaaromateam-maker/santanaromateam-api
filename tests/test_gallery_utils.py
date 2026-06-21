from app.gallery_utils import merge_service_gallery_items, normalize_image_url


CLOUD_A = "https://res.cloudinary.com/demo/image/upload/v1/santana-aroma/services/a.jpg"
CLOUD_A_OPTIMIZED = (
    "https://res.cloudinary.com/demo/image/upload/f_auto,q_auto:good,w_900,c_limit/v1/santana-aroma/services/a.jpg"
)
CLOUD_B = "https://res.cloudinary.com/demo/image/upload/v2/santana-aroma/services/b.png"


class TestNormalizeImageUrl:
    def test_same_asset_with_different_transforms(self):
        assert normalize_image_url(CLOUD_A) == normalize_image_url(CLOUD_A_OPTIMIZED)

    def test_different_assets_stay_different(self):
        assert normalize_image_url(CLOUD_A) != normalize_image_url(CLOUD_B)

    def test_empty_url(self):
        assert normalize_image_url("") == ""


class TestMergeServiceGalleryItems:
    def test_includes_main_image_first(self):
        result = merge_service_gallery_items(
            image=CLOUD_A,
            image_alt="Main photo",
            gallery=[],
        )
        assert len(result) == 1
        assert result[0]["src"] == CLOUD_A
        assert result[0]["alt"] == "Main photo"

    def test_includes_main_and_gallery_images(self):
        result = merge_service_gallery_items(
            image=CLOUD_A,
            image_alt="Main",
            gallery=[{"src": CLOUD_B, "alt": "Gallery two"}],
        )
        assert len(result) == 2
        assert result[0]["src"] == CLOUD_A
        assert result[1]["src"] == CLOUD_B
        assert result[1]["alt"] == "Gallery two"

    def test_deduplicates_main_image_also_in_gallery(self):
        result = merge_service_gallery_items(
            image=CLOUD_A,
            image_alt="Main",
            gallery=[{"src": CLOUD_A, "alt": "Duplicate"}],
        )
        assert len(result) == 1
        assert result[0]["src"] == CLOUD_A

    def test_multiple_gallery_only_when_no_main(self):
        result = merge_service_gallery_items(
            image="",
            image_alt="",
            gallery=[
                {"src": CLOUD_A, "alt": "One"},
                {"src": CLOUD_B, "alt": "Two"},
            ],
        )
        assert len(result) == 2
        assert [item["src"] for item in result] == [CLOUD_A, CLOUD_B]

    def test_preserves_order_main_then_gallery(self):
        result = merge_service_gallery_items(
            image=CLOUD_A,
            image_alt="Main",
            gallery=[
                {"src": CLOUD_B, "alt": "B"},
                {"src": "https://example.com/c.jpg", "alt": "C"},
            ],
        )
        assert [item["src"] for item in result] == [
            CLOUD_A,
            CLOUD_B,
            "https://example.com/c.jpg",
        ]
