"""
Tests for World Engine Phase 3:
================================
- Automated Obsidian Vault Generator (ObsidianVaultGenerator)
- Writer-Facing Web Dashboard Builder (build_dashboard_html)
- Lightweight Local Server (DashboardServer, HTTP API endpoints)
- CLI export-vault and serve subcommands
- Creative Non-Interference Charter Invariant Verification
"""

import json
import shutil
import tempfile
import urllib.request
from pathlib import Path

import pytest
import yaml

from world_engine.dashboard.builder import build_dashboard_html
from world_engine.serve import DashboardServer
from world_engine.vault_generator import ObsidianVaultGenerator, _sanitize_filename


@pytest.fixture
def temp_dir():
    d = tempfile.mkdtemp()
    yield Path(d)
    shutil.rmtree(d, ignore_errors=True)


class TestObsidianVaultGenerator:
    """Test suite for the automated Obsidian Vault generator."""

    def test_sanitize_filename(self):
        assert _sanitize_filename('خالد: حارس') == 'خالد_حارس'
        assert _sanitize_filename('العربة/01*') == 'العربة01'
        assert _sanitize_filename('') == 'ملاحظة'

    def test_vault_export_from_instance(self, temp_dir):
        instance_dir = Path(__file__).resolve().parent.parent / "instances" / "sand_train_auto"
        assert instance_dir.exists(), "sand_train_auto instance must exist"

        vault_out = temp_dir / "vault"
        gen = ObsidianVaultGenerator(instance_dir=instance_dir)
        stats = gen.export(vault_out)

        assert stats["characters"] >= 8
        assert stats["locations"] >= 4
        assert stats["laws"] >= 4
        assert stats["events"] >= 5
        assert stats["total_notes"] >= 25

        # Check .obsidian config
        app_json = vault_out / ".obsidian" / "app.json"
        graph_json = vault_out / ".obsidian" / "graph.json"
        assert app_json.exists()
        assert graph_json.exists()

        with open(graph_json, "r", encoding="utf-8") as f:
            graph_data = json.load(f)
            assert "colorGroups" in graph_data
            assert len(graph_data["colorGroups"]) >= 4

        # Check Master Dashboard
        dashboard = vault_out / "00_لوحة_تحكم_العالم.md"
        assert dashboard.exists()
        with open(dashboard, "r", encoding="utf-8") as f:
            dash_text = f.read()
            assert "لوحة تحكم العالم السردي" in dash_text
            assert "نحن نُحلل ونُقيّم.. ولا نُقوّم" in dash_text
            assert "dataview" in dash_text

        # Check character notes have YAML frontmatter and wikilinks
        char_files = list((vault_out / "Characters").glob("*.md"))
        assert len(char_files) >= 8
        with open(char_files[0], "r", encoding="utf-8") as f:
            char_text = f.read()
            assert char_text.startswith("---")
            assert "tags:" in char_text
            assert "[[" in char_text and "]]" in char_text

    def test_vault_export_custom_programmatic_data(self, temp_dir):
        custom_data = {
            "manifest": {
                "title": "محطة مدارية مهجورة",
                "genre": "sci_fi_survival",
                "chronotope": {"time_range": "2142 CE", "spatial_scope": "Station Alpha"},
            },
            "entities": {
                "characters": [
                    {"id": "pilot_01", "name": "القبطان ريان", "role": "ملاح", "location": "bridge"}
                ],
                "props": [
                    {"id": "oxygen_tank", "name": "خزان الأكسجين الاحتياطي", "owner": "القبطان ريان"}
                ]
            },
            "rules": {
                "rules": [
                    {"id": "LAW-VACUUM-01", "name": "ضغط الفراغ الصفري", "domain": "physics", "severity": "critical"}
                ]
            },
            "causality": {
                "events": [
                    {"id": "EVT-01", "description": "تسرب الضغط في الصالون الرئيس", "actor": "القبطان ريان"}
                ]
            }
        }
        vault_out = temp_dir / "custom_vault"
        gen = ObsidianVaultGenerator(world_data=custom_data)
        stats = gen.export(vault_out)

        assert stats["characters"] == 1
        assert stats["props"] == 1
        assert stats["laws"] == 1
        assert stats["events"] == 1

        pilot_note = vault_out / "Characters" / "القبطان_ريان.md"
        assert pilot_note.exists()


class TestWriterDashboard:
    """Test suite for the Writer Dashboard builder and server."""

    def test_build_dashboard_html(self, temp_dir):
        out_html = temp_dir / "writer_dashboard.html"
        content = build_dashboard_html(output_path=out_html)

        assert out_html.exists()
        assert len(content) > 20000
        assert "<!DOCTYPE html>" in content
        assert "World Engine OS" in content
        assert "ميثاق الحياد الإبداعي" in content
        assert "نحن نُحلل ونُقيّم.. ولا نُقوّم" in content
        assert "ENGINE_DATA" in content

    def test_dashboard_server_api_and_static(self):
        port = 8094
        server = DashboardServer(port=port)
        server.start(background=True)

        try:
            # 1. API Status
            req = urllib.request.urlopen(f"http://127.0.0.1:{port}/api/status")
            assert req.status == 200
            data = json.loads(req.read().decode("utf-8"))
            assert data["engine_version"] == "2.5.0"
            assert data["subsystems_passed"] == 30

            # 2. API Health
            req_health = urllib.request.urlopen(f"http://127.0.0.1:{port}/api/health")
            assert req_health.status == 200

            # 3. API Recommend Rules
            post_req = urllib.request.Request(
                f"http://127.0.0.1:{port}/api/recommend-rules",
                data=json.dumps({"text": "محطة فضاء مدارية وانعدام الجاذبية والفراغ"}).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            res = urllib.request.urlopen(post_req)
            assert res.status == 200
            rec_data = json.loads(res.read().decode("utf-8"))
            assert rec_data["recommended_pack"] == "orbital_space_station"

            # 4. Static HTML serving
            dash_req = urllib.request.urlopen(f"http://127.0.0.1:{port}/")
            assert dash_req.status == 200
            html_text = dash_req.read().decode("utf-8")
            assert "World Engine" in html_text

        finally:
            server.stop()


class TestPhase3CLICommands:
    """Test CLI commands for export-vault."""

    def test_cli_export_vault_execution(self, temp_dir):
        from world_engine.cli import cmd_export_vault
        import argparse

        out_path = temp_dir / "cli_vault"
        args = argparse.Namespace(
            instance=None,  # default to auto instance
            output=out_path
        )
        ret = cmd_export_vault(args)
        assert ret == 0
        assert (out_path / "00_لوحة_تحكم_العالم.md").exists()
        assert (out_path / "Characters").exists()

    def test_cli_export_vault_missing_instance(self, temp_dir):
        from world_engine.cli import cmd_export_vault
        import argparse

        out_path = temp_dir / "cli_vault_fail"
        args = argparse.Namespace(
            instance=temp_dir / "non_existent_instance",
            output=out_path
        )
        ret = cmd_export_vault(args)
        assert ret == 1

    def test_dashboard_gauges_integrity(self, temp_dir):
        out_html = temp_dir / "dash.html"
        content = build_dashboard_html(output_path=out_html)
        assert "gauge-temp" in content
        assert "gauge-co2" in content
        assert "gauge-lux" in content
        assert "gauge-pneum" in content
        assert "gauge-batt" in content

    def test_zero_touch_baseline_preservation(self):
        """Ensure Phase 3 did not modify baseline novel text under any circumstances."""
        baseline_path = Path(__file__).resolve().parent.parent / "00_BASELINE" / "novel_baseline.md"
        assert baseline_path.exists()
        with open(baseline_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        assert len(lines) == 1429, "Baseline must remain exactly 1429 lines"

