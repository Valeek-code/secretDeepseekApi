from pathlib import Path

from domain.raw_parser import OpKind, RawOp, parse_raw


def build_preview(project_root: Path | None, raw_text: str) -> tuple[str, int]:
    if not raw_text.strip():
        return ("Вставь raw-код из промпта — здесь появится план изменений.", 0)
    if project_root is None:
        return ("Проект не открыт. Открой проект (Проект → Открыть проект…).", 0)

    result = parse_raw(raw_text)
    lines: list[str] = []
    actionable = 0

    creates: list[RawOp] = []
    updates: list[RawOp] = []
    deletes: list[RawOp] = []
    missing_deletes: list[RawOp] = []

    for op in result.ops:
        target = (project_root / op.path).resolve()
        if op.kind == OpKind.WRITE:
            if target.exists() and target.is_file():
                updates.append(op)
            else:
                creates.append(op)
        else:
            if target.exists() and target.is_file():
                deletes.append(op)
            else:
                missing_deletes.append(op)

    if creates:
        lines.append(f"Создастся ({len(creates)}):")
        for op in creates:
            lines.append(f"  + {op.path}")
        lines.append("")
    if updates:
        lines.append(f"Изменится ({len(updates)}):")
        for op in updates:
            lines.append(f"  ~ {op.path}")
        lines.append("")
    if deletes:
        lines.append(f"Удалится ({len(deletes)}):")
        for op in deletes:
            lines.append(f"  - {op.path}")
        lines.append("")
    if missing_deletes:
        lines.append(f"Не найдено для удаления ({len(missing_deletes)}):")
        for op in missing_deletes:
            lines.append(f"  ? {op.path}")
        lines.append("")

    if result.errors:
        lines.append("Ошибки парсинга:")
        for err in result.errors:
            lines.append(f"  ! {err}")
        lines.append("")

    actionable = len(creates) + len(updates) + len(deletes)
    if actionable == 0 and not result.errors:
        lines.append("Нет операций для применения.")

    return ("\n".join(lines).rstrip() + "\n", actionable)
