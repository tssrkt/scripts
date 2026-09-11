from pathlib import Path
from PIL import Image

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_FILE = SCRIPT_DIR / "data.txt"

SUPPORTED_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp"
}


def read_width() -> int:
    if not DATA_FILE.exists():
        raise FileNotFoundError("Не найден файл data.txt рядом со скриптом.")

    text = DATA_FILE.read_text(encoding="utf-8").strip()

    if not text.isdigit():
        raise ValueError("В файле data.txt должно быть только число — ширина картинки в пикселях.")

    width = int(text)

    if width <= 0:
        raise ValueError("Ширина должна быть больше 0.")

    return width


def convert_images(target_width: int) -> None:
    output_dir = SCRIPT_DIR / f"img_{target_width}"
    output_dir.mkdir(exist_ok=True)

    image_paths = sorted(
        path for path in SCRIPT_DIR.iterdir()
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    )

    for index, image_path in enumerate(image_paths, start=1):
        output_path = output_dir / f"{index}.webp"

        with Image.open(image_path) as img:
            img = img.convert("RGB")

            width, height = img.size
            new_height = round(height * target_width / width)

            img = img.resize((target_width, new_height), Image.LANCZOS)

            img.save(output_path, "WEBP", quality=90, method=6)

        print(f"Готово: {image_path.name} → {output_path.name}")


def main():
    target_width = read_width()
    convert_images(target_width)
    print("Конвертация завершена.")


if __name__ == "__main__":
    main()