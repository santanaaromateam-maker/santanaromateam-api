from unittest.mock import MagicMock, patch

from app.services_mapper import service_to_public


SAMPLE_DOC = {
    "_id": "abc123",
    "slug": "office-cleaning",
    "title": "Office Cleaning",
    "short_description": "Short",
    "chip_label": "Office Cleaning",
    "order": 1,
    "active": True,
    "image": "https://res.cloudinary.com/demo/image/upload/v1/santana-aroma/services/main.jpg",
    "image_alt": "Main office",
    "hero_title": "Office Cleaning",
    "hero_subtitle": "Short",
    "meta_description": "Meta",
    "intro": ["Intro"],
    "gallery": [
        {
            "src": "https://res.cloudinary.com/demo/image/upload/v1/santana-aroma/services/extra.jpg",
            "alt": "Extra",
        },
    ],
    "service_areas": ["Hollywood, FL"],
    "whatsapp_text": "Hi",
}


class TestServiceToPublicGallery:
    def test_public_gallery_includes_main_and_extra_images(self):
        public = service_to_public(SAMPLE_DOC)
        assert len(public.gallery) == 2
        assert "main.jpg" in public.gallery[0].src
        assert "extra.jpg" in public.gallery[1].src

    def test_public_gallery_deduplicates_main_when_repeated_in_gallery(self):
        doc = {
            **SAMPLE_DOC,
            "gallery": [{"src": SAMPLE_DOC["image"], "alt": "Dup"}],
        }
        public = service_to_public(doc)
        assert len(public.gallery) == 1


class TestPublicServicesEndpoint:
    def test_api_returns_merged_gallery(self, client):
        mock_cursor = MagicMock()
        mock_cursor.sort.return_value = [SAMPLE_DOC]

        mock_collection = MagicMock()
        mock_collection.find.return_value = mock_cursor

        with patch("app.routers.public.services_collection", return_value=mock_collection):
            response = client.get("/api/services")

        assert response.status_code == 200
        data = response.json()
        service = data["services"][0]
        assert service["slug"] == "office-cleaning"
        assert len(service["gallery"]) == 2
        assert service["gallery"][0]["alt"] == "Main office"
        assert service["gallery"][1]["alt"] == "Extra"

    def test_api_returns_empty_gallery_when_no_images(self, client):
        doc = {**SAMPLE_DOC, "image": "", "gallery": []}
        mock_cursor = MagicMock()
        mock_cursor.sort.return_value = [doc]
        mock_collection = MagicMock()
        mock_collection.find.return_value = mock_cursor

        with patch("app.routers.public.services_collection", return_value=mock_collection):
            response = client.get("/api/services")

        assert response.status_code == 200
        assert response.json()["services"][0]["gallery"] == []
