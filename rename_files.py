from pathlib import Path
import re
import uuid

SCRIPT_NAME = Path(__file__).name
TEMPLATE_FILE = "rename_template.txt"

# Поддерживаемый шаблон:
# name_[001].jpg
# Diablo_[001].jpg
# page_[0001].png
PLACEHOLDER_RE = re.compile(r"\[(\d+)\]")


def natural_key(text: str):
    """Естественная сортировка: 2 раньше 11, 11 раньше 101."""
    return [
        int(part) if part.isdigit() else part.lower()
        for part in re.split(r"(\d+)", text)
    ]


def file_sort_key(path: Path):
    """
    Если имя заканчивается числом перед расширением:
    abc-0.jpg, abc-1.jpg, abc-11.jpg
    сортируем именно по этому числу.
    Иначе используем естественную сортировку всего имени.
    """
    match = re.search(r"(\d+)$", path.stem)
    if match:
        return (0, int(match.group(1)), natural_key(path.name))

    return (1, 0, natural_key(path.name))


def main():
    folder = Path(__file__).resolve().parent
    template_path = folder / TEMPLATE_FILE

    if not template_path.exists():
        print(f"Не найден файл {TEMPLATE_FILE}")
        print("Создай его рядом со скриптом, например:")
        print("name_[001].jpg")
        input("\nНажми Enter для выхода...")
        return

    template = template_path.read_text(encoding="utf-8-sig").strip()

    matches = PLACEHOLDER_RE.findall(template)

    if len(matches) != 1:
        print("Неверный шаблон.")
        print("Используй формат, например:")
        print("name_[001].jpg")
        input("\nНажми Enter для выхода...")
        return

    example = matches[0]
    start_number = int(example)
    width = len(example)

    template_suffix = Path(template).suffix.lower()

    if not template_suffix:
        print("В шаблоне должно быть расширение файла, например .jpg")
        input("\nНажми Enter для выхода...")
        return

    files = [
        path for path in folder.iterdir()
        if path.is_file()
        and path.name not in {SCRIPT_NAME, TEMPLATE_FILE}
        and path.suffix.lower() == template_suffix
    ]

    if not files:
        print(f"Файлы {template_suffix} не найдены.")
        input("\nНажми Enter для выхода...")
        return

    files.sort(key=file_sort_key)

    rename_plan = []

    for index, old_path in enumerate(files):
        number = start_number + index
        formatted_number = f"{number:0{width}d}"

        new_name = PLACEHOLDER_RE.sub(
            formatted_number,
            template,
            count=1
        )

        new_path = folder / new_name
        rename_plan.append((old_path, new_path))

    target_names = [new.name.lower() for _, new in rename_plan]

    if len(target_names) != len(set(target_names)):
        print("Ошибка: шаблон создаёт повторяющиеся имена.")
        input("\nНажми Enter для выхода...")
        return

    print("Будут выполнены переименования:\n")

    for old, new in rename_plan:
        print(f"{old.name}  ->  {new.name}")

    answer = input("\nПродолжить? [y/N]: ").strip().lower()

    if answer not in {"y", "yes", "д", "да"}:
        print("Отменено.")
        return

    temporary = []

    try:
        for old, new in rename_plan:
            temp = folder / f".__rename_tmp_{uuid.uuid4().hex}{old.suffix}"
            old.rename(temp)
            temporary.append((temp, new))

        for temp, new in temporary:
            temp.rename(new)

    except Exception as exc:
        print(f"\nОшибка при переименовании: {exc}")
        print("Часть файлов могла остаться под временными именами.")
        input("\nНажми Enter для выхода...")
        return

    print(f"\nГотово. Переименовано файлов: {len(rename_plan)}")
    input("Нажми Enter для выхода...")


if __name__ == "__main__":
    main()
