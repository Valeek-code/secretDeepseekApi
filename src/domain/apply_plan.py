from dataclasses import dataclass, field
from pathlib import Path

from domain.raw_parser import OpKind, RawOp, parse_raw


@dataclass
class ApplyReport:
    created: list[str] = field(default_factory=list)
    updated: list[str] = field(default_factory=list)
    deleted: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def _safe_target(project_root: Path, rel_path: str) -> Path | None:
    root = project_root.resolve()
    target = (root / rel_path).resolve()
    try:
        target.relative_to(root)
    except ValueError:
        return None
    return target


def apply_plan(project_root: Path, raw_text: str) -> ApplyReport:
    report = ApplyReport()
    result = parse_raw(raw_text)
    report.errors.extend(result.errors)

    for op in result.ops:
        target = _safe_target(project_root, op.path)
        if target is None:
            report.errors.append(f"Путь вне проекта: {op.path}")
            continue

        if op.kind == OpKind.WRITE:
            try:
                existed = target.exists() and target.is_file()
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(op.content, encoding="utf-8")
                if existed:
                    report.updated.append(op.path)
                else:
                    report.created.append(op.path)
            except OSError as exc:
                report.errors.append(f"Не удалось записать {op.path}: {exc}")
        else:
            if target.exists() and target.is_file():
                try:
                    target.unlink()
                    report.deleted.append(op.path)
                except OSError as exc:
                    report.errors.append(f"Не удалось удалить {op.path}: {exc}")
            else:
                report.missing.append(op.path)

    return report


def format_report(report: ApplyReport) -> str:
    lines: list[str] = []
    if report.created:
        lines.append(f"Создано ({len(report.created)}):")
        for path in report.created:
            lines.append(f"  + {path}")
    if report.updated:
        lines.append(f"Изменено ({len(report.updated)}):")
        for path in report.updated:
            lines.append(f"  ~ {path}")
    if report.deleted:
        lines.append(f"Удалено ({len(report.deleted)}):")
        for path in report.deleted:
            lines.append(f"  - {path}")
    if report.missing:
        lines.append(f"Пропущено (нет файла, {len(report.missing)}):")
        for path in report.missing:
            lines.append(f"  ? {path}")
    if report.errors:
        lines.append(f"Ошибки ({len(report.errors)}):")
        for err in report.errors:
            lines.append(f"  ! {err}")
    if not lines:
        lines.append("Изменений не было.")
    return "\n".join(lines) + "\n"
