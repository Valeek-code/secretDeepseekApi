from dataclasses import dataclass
from enum import Enum


class OpKind(str, Enum):
    WRITE = "write"
    DELETE = "delete"


@dataclass
class RawOp:
    kind: OpKind
    path: str
    content: str = ""


@dataclass
class ParseResult:
    ops: list[RawOp]
    errors: list[str]


FILE_PREFIX = "=== FILE:"
DELETE_PREFIX = "=== DELETE:"
END_MARKER = "=== END ==="


def parse_raw(text: str) -> ParseResult:
    ops: list[RawOp] = []
    errors: list[str] = []

    current_kind: OpKind | None = None
    current_path: str | None = None
    content_lines: list[str] = []

    for raw_line in text.splitlines():
        stripped = raw_line.strip()

        if current_kind is None:
            if stripped.startswith(FILE_PREFIX) and stripped.endswith("==="):
                path = stripped[len(FILE_PREFIX):-3].strip()
                if not path:
                    errors.append("Пустой путь в === FILE: ... ===")
                    continue
                current_kind = OpKind.WRITE
                current_path = path
                content_lines = []
            elif stripped.startswith(DELETE_PREFIX) and stripped.endswith("==="):
                path = stripped[len(DELETE_PREFIX):-3].strip()
                if not path:
                    errors.append("Пустой путь в === DELETE: ... ===")
                    continue
                current_kind = OpKind.DELETE
                current_path = path
                content_lines = []
            continue

        if stripped == END_MARKER:
            if current_kind == OpKind.WRITE:
                ops.append(RawOp(OpKind.WRITE, current_path or "", "\n".join(content_lines)))
            else:
                ops.append(RawOp(OpKind.DELETE, current_path or ""))
            current_kind = None
            current_path = None
            content_lines = []
            continue

        content_lines.append(raw_line)

    if current_kind is not None:
        errors.append(f"Незакрытый блок для: {current_path}")

    return ParseResult(ops=ops, errors=errors)
