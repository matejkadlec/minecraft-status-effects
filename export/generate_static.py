"""
Pre-generate static export files for instant download.
Run this script to create CSV, XLSX, and JSON files with all effects.
"""

import json
import os
from datetime import datetime
from export.export_handler import ExportHandler


def main():
    """Generate pre-built export files."""
    print("Generating pre-built export files...")

    # Ensure export directories exist
    os.makedirs("export/files", exist_ok=True)

    handler = ExportHandler()

    # Generate files for both themes
    themes = ["light", "dark"]
    formats = ["json", "csv", "xlsx"]

    for theme in themes:
        print(f"\nGenerating {theme} theme files...")

        for format_type in formats:
            try:
                # Generate with no filters (all effects)
                content, _ = handler.export_data(
                    format_type, theme, ignore_filters=True
                )

                # Save with theme-specific name (JSON is theme-agnostic)
                if format_type == "json":
                    filename = f"status-effects.{format_type}"
                else:
                    filename = f"status-effects-{theme}.{format_type}"

                filepath = os.path.join("export/files", filename)

                # Write file
                mode = "wb" if format_type == "xlsx" else "wb"
                with open(filepath, mode) as f:
                    f.write(content)

                print(f"  ✓ Generated {filename}")

            except Exception as e:
                print(f"  ✗ Failed to generate {theme} {format_type}: {e}")

    # Update timestamp file
    timestamp_file = "export/files/.generated"
    with open(timestamp_file, "w") as f:
        f.write(datetime.now().isoformat())

    print(f"\n✓ All files generated successfully!")
    print("Files are ready for instant download in export/files/")


if __name__ == "__main__":
    main()
