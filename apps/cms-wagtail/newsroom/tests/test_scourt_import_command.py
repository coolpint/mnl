from __future__ import annotations

import sqlite3
from pathlib import Path
from tempfile import TemporaryDirectory

from django.core.management.base import CommandError
from django.test import TestCase

from newsroom.management.commands.import_scourt_reports import (
    Command,
    _decode_json_or_raise,
    _extract_output_text,
    _strip_fence,
)


class ScourtImportCommandUnitTests(TestCase):
    def test_strip_fence(self):
        raw = "```json\n{\"headline\":\"h\",\"body\":\"b\",\"summary\":\"s\"}\n```"
        self.assertEqual(_strip_fence(raw), '{"headline":"h","body":"b","summary":"s"}')

    def test_extract_output_text_from_output_text_field(self):
        payload = {"output_text": '{"headline":"h","body":"b","summary":"s"}'}
        self.assertEqual(_extract_output_text(payload), payload["output_text"])

    def test_extract_output_text_from_output_blocks(self):
        payload = {
            "output": [
                {
                    "content": [
                        {"type": "output_text", "text": {"value": '{"headline":"h","body":"b","summary":"s"}'}}
                    ]
                }
            ]
        }
        self.assertIn('"headline":"h"', _extract_output_text(payload))

    def test_decode_json_or_raise(self):
        decoded = _decode_json_or_raise('{"headline":"h","body":"b","summary":"s"}')
        self.assertEqual(decoded["headline"], "h")

        with self.assertRaises(CommandError):
            _decode_json_or_raise("not-json")

    def test_load_notices_from_scourt_db(self):
        with TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "scourt.db"
            with sqlite3.connect(str(db_path)) as conn:
                conn.execute(
                    """
                    CREATE TABLE notices (
                        notice_id TEXT PRIMARY KEY,
                        title TEXT NOT NULL,
                        posted_date TEXT NOT NULL,
                        detail_url TEXT NOT NULL,
                        pdf_url TEXT,
                        content_hash TEXT NOT NULL,
                        article_text TEXT NOT NULL
                    )
                    """
                )
                conn.execute(
                    """
                    INSERT INTO notices (notice_id, title, posted_date, detail_url, pdf_url, content_hash, article_text)
                    VALUES ('101', 't1', '2026-03-01', 'https://example.com/1', NULL, 'abc123', 'article1')
                    """
                )
                conn.execute(
                    """
                    INSERT INTO notices (notice_id, title, posted_date, detail_url, pdf_url, content_hash, article_text)
                    VALUES ('102', 't2', '2026-03-02', 'https://example.com/2', 'https://example.com/2.pdf', 'def456', 'article2')
                    """
                )
                conn.commit()

            cmd = Command()
            notices = cmd._load_notices(db_path=db_path, notice_ids=[], limit=1)
            self.assertEqual(len(notices), 1)
            self.assertEqual(notices[0].notice_id, "102")

            notices = cmd._load_notices(db_path=db_path, notice_ids=["101"], limit=5)
            self.assertEqual(len(notices), 1)
            self.assertEqual(notices[0].notice_id, "101")
