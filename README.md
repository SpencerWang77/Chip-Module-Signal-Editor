# Chip Module Editor for ESWIN

A polished PyQt5 desktop application for importing, viewing, and editing ESWIN chip-module register maps from Excel workbooks.

The import expects a `3.register` worksheet with `HEX_BYTE_ADDR`, `REG_NAME`, and an eight-column `REG_FIELD` area ordered from bit 7 to bit 0. Merged cells in `REG_FIELD` become visible multi-bit fields in the editor. When `2.AD_AA` is present, `SIGNAL_NAME` suffixes and byte addresses are used to attach its `DESCRIPTION` text to matching register fields.

## Requirements

- Python 3.10+
- PyQt5
- openpyxl

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

## Workflow

1. Drop an `.xlsx` workbook onto the upload screen or select `top_signal.xlsx` as the included sample.
2. Choose a square module card to open its four-byte register editor.
3. Toggle bit circles, then click a colored register-field label to inspect its `2.AD_AA` description.
4. Rename the selected field either inline or in the description panel.
5. Review every bit and field-name change in the session log on the right.
6. Search modules, optionally show edited modules only, and export a workbook copy. The copy includes an `EDITED_HEX_VALUE` column and updates edited field names and defaults.

## Architecture

The frontend uses **PyQt5 Qt Widgets**. It is a native desktop UI rather than a browser-based frontend.

- `main.py` — lightweight application entry point
- `chip_editor/models.py` — register and workbook data models
- `chip_editor/workbook_io.py` — Excel parsing, validation, and export
- `chip_editor/theme.py` — central Qt stylesheet
- `chip_editor/window.py` — main window and page navigation
- `chip_editor/ui/common.py` — reusable bit, field, drag/drop, and register widgets
- `chip_editor/ui/upload_page.py` — workbook import screen
- `chip_editor/ui/editor_page.py` — interactive register editor
- `chip_editor/ui/field_details.py` — selected-field description and rename panel
- `chip_editor/ui/module_gallery.py` — responsive square module cards
- `chip_editor/ui/change_log.py` — session edit history panel

`openpyxl` handles the Excel workbook data layer.
