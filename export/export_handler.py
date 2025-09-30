"""
Export handler for status effects data.
Handles filtering and theme-aware export generation.
"""

import json
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from export.export_formatter import ExportFormatter


class ExportHandler:
    def __init__(self, effects_data_path: str = "data/effects.json"):
        """Initialize with effects data."""
        with open(effects_data_path, "r", encoding="utf-8") as f:
            self.data = json.load(f)
        self.effects = self.data["effects"]

    def filter_effects(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply filters to effects data."""
        filtered = self.effects.copy()

        # Search filter
        if search := filters.get("search", "").strip():
            search_lower = search.lower()
            filtered = [
                effect
                for effect in filtered
                if (
                    search_lower in effect["effect"].lower()
                    or search_lower in effect["mod"].lower()
                    or search_lower in self._strip_html(effect["description"]).lower()
                )
            ]

        # Type filters
        type_filters = filters.get("type_filters", {})
        if type_filters.get("positive") is False:
            filtered = [e for e in filtered if "positive" not in e["tags"]]
        if type_filters.get("negative") is False:
            filtered = [e for e in filtered if "negative" not in e["tags"]]
        if type_filters.get("scaling") is False:
            filtered = [e for e in filtered if "scaling" not in e["tags"]]

        # Vanilla filter
        vanilla_filter = filters.get("vanilla_filter", True)
        if vanilla_filter is False:
            filtered = [e for e in filtered if e["mod"] != "Minecraft"]

        return filtered

    def _strip_html(self, text: str) -> str:
        """Remove HTML tags from text."""
        return re.sub(r"<[^>]+>", "", text)

    def export_data(
        self,
        format_type: str,
        theme: str,
        filters: Optional[Dict[str, Any]] = None,
        ignore_filters: bool = False,
    ) -> tuple[bytes, str]:
        """
        Export data in specified format with theme styling.

        Returns:
            tuple: (file_content as bytes, filename)
        """
        if ignore_filters or not filters:
            effects = self.effects
        else:
            effects = self.filter_effects(filters)

        formatter = ExportFormatter(theme)
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

        if format_type.lower() == "json":
            content = formatter.format_json(effects)
            filename = f"status-effects-{timestamp}.json"
            return content.encode("utf-8"), filename

        elif format_type.lower() == "csv":
            content = formatter.format_csv(effects)
            filename = f"status-effects-{timestamp}.csv"
            return content.encode("utf-8-sig"), filename  # BOM for Excel compatibility

        elif format_type.lower() == "xlsx":
            content = formatter.format_xlsx(effects)
            filename = f"status-effects-{timestamp}.xlsx"
            return content, filename

        else:
            raise ValueError(f"Unsupported format: {format_type}")
