"""Offline tests for layer 1: no network, no key. Run: .venv/bin/python -m unittest"""

import unittest

from cmv import youtube


class Layer1Offline(unittest.TestCase):
    def test_duration_parsing(self):
        self.assertEqual(youtube._seconds("PT1H2M30S"), 3750)
        self.assertEqual(youtube._seconds("PT45S"), 45)
        self.assertEqual(youtube._seconds("garbage"), 0)

    def test_video_from_api_cleans_stranger_text(self):
        item = {
            "id": "PFDu9oVAE-g",
            "snippet": {"title": "Eigen | ★ vectors‮", "channelTitle": "3B1B",
                        "channelId": "UC1", "publishedAt": "2016-09-15T00:00:00Z",
                        "description": "raw"},
            "contentDetails": {"duration": "PT17M16S", "caption": "true"},
            "statistics": {"viewCount": "1000", "likeCount": "50"},
        }
        v = youtube._video_from_api(item)
        self.assertEqual(v["title"], "Eigen vectors")
        self.assertEqual(v["seconds"], 1036)
        self.assertEqual(v["likes_per_1k_views"], 50.0)
        self.assertTrue(v["creator_captions"])

    def test_hidden_likes(self):
        item = {"id": "PFDu9oVAE-g", "snippet": {}, "contentDetails": {},
                "statistics": {"viewCount": "10"}}
        self.assertIsNone(youtube._video_from_api(item)["likes_per_1k_views"])

    def test_key_is_scrubbed_from_errors(self):
        youtube._key = "SECRETKEY123"
        try:
            self.assertNotIn("SECRETKEY123", youtube._scrub("url?key=SECRETKEY123"))
        finally:
            youtube._key = None


if __name__ == "__main__":
    unittest.main()
