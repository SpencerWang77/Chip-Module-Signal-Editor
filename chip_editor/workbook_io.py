"""Excel validation, parsing, and export for register maps."""

from __future__ import annotations

import re
import shutil
from pathlib import Path
from typing import Optional

from openpyxl import load_workbook
from openpyxl.cell.cell import MergedCell

from .constants import BIT_COLUMN_COUNT, REGISTER_SHEET
from .models import RegisterByte, RegisterField, WorkbookData


FIELD_VALUE_RE = re.compile(r"^(.*?)(?:\[\s*(0x[0-9a-fA-F]+|\d+)\s*\])?\s*$")


class WorkbookFormatError(ValueError):
    """Raised when an uploaded workbook does not match the register format."""


def _cell_text(value: object) -> str:
    return "" if value is None else str(value).strip()


def _hex_address(value: object, decimal_fallback: object = None) -> str:
    candidate = value if value is not None else decimal_fallback
    if candidate is None:
        return "—"
    if isinstance(candidate, int):
        return f"0x{candidate:04X}"
    text = str(candidate).strip()
    try:
        return f"0x{int(text, 0):04X}"
    except (TypeError, ValueError):
        return text


def _parse_field_text(value: object) -> tuple[str, int]:
    text = _cell_text(value)
    if not text:
        return "", 0
    match = FIELD_VALUE_RE.match(text)
    if not match:
        return text, 0
    name = match.group(1).strip()
    raw_value = match.group(2)
    try:
        default = int(raw_value, 0) if raw_value else 0
    except ValueError:
        default = 0
    return name, default


def parse_register_workbook(path: Path) -> WorkbookData:
    """Validate and parse a workbook without changing the source file."""

    try:
        # Cached values resolve formula-based addresses in the supplied sample.
        # Export reopens with data_only=False so source formulas remain intact.
        workbook = load_workbook(path, data_only=True, read_only=False)
    except Exception as exc:
        raise WorkbookFormatError(f"This file could not be opened as an Excel workbook: {exc}") from exc

    if REGISTER_SHEET not in workbook.sheetnames:
        raise WorkbookFormatError(
            f"Missing the required ‘{REGISTER_SHEET}’ sheet. Found: {', '.join(workbook.sheetnames)}"
        )

    worksheet = workbook[REGISTER_SHEET]
    required_headers = {"HEX_BYTE_ADDR", "REG_NAME", "REG_FIELD"}
    header_row: Optional[int] = None
    header_columns: dict[str, int] = {}

    for row_index in range(1, min(worksheet.max_row, 40) + 1):
        found = {
            _cell_text(worksheet.cell(row_index, column).value): column
            for column in range(1, worksheet.max_column + 1)
        }
        if required_headers.issubset(found):
            header_row = row_index
            header_columns = found
            break

    if header_row is None:
        raise WorkbookFormatError(
            "The register table needs HEX_BYTE_ADDR, REG_NAME, and REG_FIELD headers."
        )

    bit_start = header_columns["REG_FIELD"]
    bit_end = bit_start + BIT_COLUMN_COUNT - 1
    for merged_range in worksheet.merged_cells.ranges:
        if (
            merged_range.min_row <= header_row <= merged_range.max_row
            and merged_range.min_col <= bit_start <= merged_range.max_col
        ):
            if merged_range.max_col - merged_range.min_col + 1 == BIT_COLUMN_COUNT:
                bit_start = merged_range.min_col
                bit_end = merged_range.max_col
            break

    if bit_end > worksheet.max_column:
        raise WorkbookFormatError("REG_FIELD must span eight columns, ordered from bit 7 to bit 0.")

    merged_by_row: dict[int, list[tuple[int, int]]] = {}
    for merged_range in worksheet.merged_cells.ranges:
        if merged_range.max_col < bit_start or merged_range.min_col > bit_end:
            continue
        for row_index in range(merged_range.min_row, merged_range.max_row + 1):
            if row_index > header_row:
                merged_by_row.setdefault(row_index, []).append(
                    (max(bit_start, merged_range.min_col), min(bit_end, merged_range.max_col))
                )

    dec_col = header_columns.get("DEC_BYTE_ADDR")
    reg32_col = header_columns.get("REG32_NAME")
    hex_col = header_columns["HEX_BYTE_ADDR"]
    name_col = header_columns["REG_NAME"]
    registers: list[RegisterByte] = []

    for row_index in range(header_row + 1, worksheet.max_row + 1):
        address = worksheet.cell(row_index, hex_col).value
        register_name = worksheet.cell(row_index, name_col).value
        decimal_address = worksheet.cell(row_index, dec_col).value if dec_col else None
        if address is None and decimal_address is None and register_name is None:
            continue

        fields: list[RegisterField] = []
        visited: set[int] = set()
        merged_spans = merged_by_row.get(row_index, [])

        for column in range(bit_start, bit_end + 1):
            if column in visited:
                continue
            span_start = column
            span_end = column
            for merged_start, merged_end in merged_spans:
                if merged_start <= column <= merged_end:
                    span_start, span_end = merged_start, merged_end
                    break
            visited.update(range(span_start, span_end + 1))

            cell = worksheet.cell(row_index, span_start)
            if isinstance(cell, MergedCell) or cell.value is None:
                continue
            original_text = _cell_text(cell.value)
            field_name, default_value = _parse_field_text(original_text)
            if not field_name:
                continue
            start_bit = 7 - (span_start - bit_start)
            end_bit = 7 - (span_end - bit_start)
            width = start_bit - end_bit + 1
            fields.append(
                RegisterField(
                    name=field_name,
                    original_text=original_text,
                    start_column=span_start,
                    end_column=span_end,
                    start_bit=start_bit,
                    end_bit=end_bit,
                    default_value=default_value & ((1 << width) - 1),
                )
            )

        bits = [0] * BIT_COLUMN_COUNT
        for register_field in fields:
            for bit_number in range(register_field.end_bit, register_field.start_bit + 1):
                display_index = 7 - bit_number
                bits[display_index] = (
                    register_field.default_value >> (bit_number - register_field.end_bit)
                ) & 1

        registers.append(
            RegisterByte(
                worksheet_row=row_index,
                dec_addr=_cell_text(decimal_address),
                hex_addr=_hex_address(address, decimal_address),
                reg32_name=_cell_text(worksheet.cell(row_index, reg32_col).value) if reg32_col else "",
                reg_name=_cell_text(register_name) or "Unnamed register",
                fields=fields,
                original_bits=tuple(bits),
            )
        )

    if not registers:
        raise WorkbookFormatError("No register rows were found below the header.")

    return WorkbookData(
        source_path=path,
        sheet_name=REGISTER_SHEET,
        header_row=header_row,
        bit_start_column=bit_start,
        registers=registers,
    )


def export_workbook(data: WorkbookData, destination: Path) -> None:
    """Export a copy with edited field defaults and a byte-value column."""

    if data.source_path.resolve() == destination.resolve():
        raise ValueError("Choose a new file name so the source workbook remains unchanged.")

    shutil.copy2(data.source_path, destination)
    workbook = load_workbook(destination, data_only=False, read_only=False)
    worksheet = workbook[data.sheet_name]
    output_column = max(worksheet.max_column + 1, data.bit_start_column + BIT_COLUMN_COUNT)
    worksheet.cell(data.header_row, output_column, "EDITED_HEX_VALUE")

    for register in data.registers:
        worksheet.cell(register.worksheet_row, output_column, f"0x{register.value:02X}")
        if not register.is_modified:
            continue
        for register_field in register.fields:
            display_start = 7 - register_field.start_bit
            display_end = 7 - register_field.end_bit
            segment = register.bits[display_start : display_end + 1]
            original_segment = register.original_bits[display_start : display_end + 1]
            if tuple(segment) == tuple(original_segment):
                continue
            new_value = RegisterByte.value_from_bits(segment)
            worksheet.cell(
                register.worksheet_row,
                register_field.start_column,
                f"{register_field.name}[0x{new_value:X}]",
            )

    workbook.save(destination)
