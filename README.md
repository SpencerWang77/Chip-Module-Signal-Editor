# Chip Module Editor for ESWIN

A polished PyQt5 desktop application for importing, viewing, and editing ESWIN chip-module register maps from Excel workbooks.

The import finds the first readable worksheet whose name contains `register` (case-insensitive). That worksheet must provide `HEX_BYTE_ADDR`, `REG_NAME`, and an eight-column `REG_FIELD` area ordered from bit 7 to bit 0. Merged cells in `REG_FIELD` become visible multi-bit fields in the editor.

A description worksheet is optional. When a worksheet name contains `AD_AA`, it must provide `SIGNAL_NAME` and `DESCRIPTION`; `HEX_BYTE_ADDR` is used when available to improve suffix matching. Export begins with a copy of the uploaded workbook, updates the detected register sheet, and carries all other worksheets and content into the exported `.xlsx` file.

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
3. Toggle bit circles, then click a colored register-field label to select it and inspect its optional `AD_AA` description.
4. Rename the field only in the selected-field panel. Labels beneath the circles are selection controls, not text inputs.
5. Edit a matched description in the same panel and apply it back to its source `AD_AA` row.
6. Review every bit, field-name, and description change in the session log on the right.
7. Search modules, optionally show edited modules only, and export a workbook copy. The copy includes an `EDITED_HEX_VALUE` column and updates edited field names, defaults, and matched descriptions.

## Architecture

The frontend uses **PyQt5 Qt Widgets**. It is a native desktop UI rather than a browser-based frontend.

- `main.py` — lightweight application entry point
- `chip_editor/models.py` — register and workbook data models
- `chip_editor/workbook_io.py` — Excel parsing, validation, and export
- `chip_editor/theme.py` — central Qt stylesheet
- `chip_editor/window.py` — main window and page navigation
- `chip_editor/ui/common.py` — reusable bit, field, drag/drop, and register widgets
- `chip_editor/ui/upload_page.py` — workbook import screen
- `chip_editor/ui/import_rules.py` — hover-expandable workbook contract
- `chip_editor/ui/editor_page.py` — interactive register editor
- `chip_editor/ui/field_details.py` — selected-field description and rename panel
- `chip_editor/ui/module_gallery.py` — responsive square module cards
- `chip_editor/ui/change_log.py` — session edit history panel

`openpyxl` handles the Excel workbook data layer.
