from unittest.mock import MagicMock, patch

from app.site_settings import site_settings_to_public, update_site_settings


class TestSiteSettingsPublic:
    def test_empty_settings_return_blank_photo(self):
        public = site_settings_to_public(
            {
                "_id": "global",
                "team_photo_url": "",
                "team_photo_alt": "Team",
            }
        )
        assert public.teamPhotoUrl == ""
        assert public.teamPhotoAlt == "Team"

    def test_cloudinary_url_is_optimized(self):
        url = "https://res.cloudinary.com/demo/image/upload/v1/santana-aroma/team.jpg"
        public = site_settings_to_public(
            {
                "_id": "global",
                "team_photo_url": url,
                "team_photo_alt": "Our team",
            }
        )
        assert "w_1200" in public.teamPhotoUrl
        assert public.teamPhotoAlt == "Our team"


class TestPublicSiteSettingsEndpoint:
    def test_api_returns_team_photo(self, client):
        doc = {
            "_id": "global",
            "team_photo_url": "https://res.cloudinary.com/demo/image/upload/v1/team.jpg",
            "team_photo_alt": "Santana Aroma team",
        }

        with patch("app.routers.public.site_settings_to_public", return_value=site_settings_to_public(doc)):
            response = client.get("/api/site-settings")

        assert response.status_code == 200
        data = response.json()
        assert data["teamPhotoAlt"] == "Santana Aroma team"
        assert "team.jpg" in data["teamPhotoUrl"]


class TestUpdateSiteSettings:
    def test_update_persists_fields(self):
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = {
            "_id": "global",
            "team_photo_url": "https://example.com/team.jpg",
            "team_photo_alt": "Team photo",
            "team_photo_public_id": "team-photo",
            "updated_at": "2026-01-01T00:00:00Z",
        }

        with patch("app.site_settings.site_settings_collection", return_value=mock_collection):
            update_site_settings(
                team_photo_url="https://example.com/team.jpg",
                team_photo_alt="Team photo",
                team_photo_public_id="team-photo",
            )

        mock_collection.update_one.assert_called_once()
        args, kwargs = mock_collection.update_one.call_args
        assert args[0] == {"_id": "global"}
        assert kwargs["upsert"] is True
        assert args[1]["$set"]["team_photo_url"] == "https://example.com/team.jpg"
