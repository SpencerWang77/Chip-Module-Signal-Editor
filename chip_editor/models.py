"""Domain models for register workbooks."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


@dataclass
class RegisterField:
    """A named field occupying one or more of the eight register bits."""

    name: str
    original_name: str
    original_text: str
    start_column: int
    end_column: int
    start_bit: int
    end_bit: int
    default_value: int = 0
    description: str = ""
    description_source_name: str = ""
    description_source_row: int = 0

    @property
    def width(self) -> int:
        return self.start_bit - self.end_bit + 1

    @property
    def range_label(self) -> str:
        if self.start_bit == self.end_bit:
            return f"b{self.start_bit}"
        return f"b{self.start_bit}:{self.end_bit}"

    @property
    def is_modified(self) -> bool:
        return self.name != self.original_name

    @property
    def has_description(self) -> bool:
        return bool(self.description)


@dataclass
class RegisterByte:
    """One workbook row and its editable eight-bit value."""

    worksheet_row: int
    dec_addr: str
    hex_addr: str
    reg32_name: str
    reg_name: str
    fields: list[RegisterField]
    original_bits: tuple[int, ...]
    bits: list[int] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.bits:
            self.bits = list(self.original_bits)

    @staticmethod
    def value_from_bits(bits: Iterable[int]) -> int:
        value = 0
        for bit in bits:
            value = (value << 1) | int(bool(bit))
        return value

    @property
    def value(self) -> int:
        return self.value_from_bits(self.bits)

    @property
    def default_value(self) -> int:
        return self.value_from_bits(self.original_bits)

    @property
    def is_modified(self) -> bool:
        return tuple(self.bits) != self.original_bits or any(
            register_field.is_modified for register_field in self.fields
        )


@dataclass
class RegisterModule:
    """A named four-byte module beginning at a REG32_NAME row."""

    name: str
    registers: list[RegisterByte]

    @property
    def start_address(self) -> str:
        return self.registers[0].hex_addr

    @property
    def end_address(self) -> str:
        return self.registers[-1].hex_addr

    @property
    def modified_count(self) -> int:
        return sum(register.is_modified for register in self.registers)

    @property
    def is_modified(self) -> bool:
        return bool(self.modified_count)


def build_register_modules(registers: list[RegisterByte]) -> list[RegisterModule]:
    """Build exact four-byte modules from rows that declare REG32_NAME."""

    modules: list[RegisterModule] = []
    for index, register in enumerate(registers):
        if not register.reg32_name:
            continue
        module_registers = registers[index : index + 4]
        if module_registers:
            modules.append(RegisterModule(register.reg32_name, module_registers))
    return modules


@dataclass
class WorkbookData:
    """Parsed workbook metadata and editable register rows."""

    source_path: Path
    sheet_name: str
    header_row: int
    bit_start_column: int
    registers: list[RegisterByte]
    description_sheet_name: str = ""

    @property
    def described_field_count(self) -> int:
        return sum(
            register_field.has_description
            for register in self.registers
            for register_field in register.fields
        )
