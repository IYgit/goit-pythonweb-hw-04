import argparse
import asyncio
import aiofiles
import aiofiles.os
import aiofiles.ospath
import shutil
from pathlib import Path
import logging

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Асинхронне копіювання файлу
async def copy_file(src_path: Path, dest_folder: Path):
    try:
        ext = src_path.suffix.lower().strip('.') or 'no_extension'
        target_dir = dest_folder / ext
        await aiofiles.os.makedirs(target_dir, exist_ok=True)
        dest_path = target_dir / src_path.name

        # Копіювання файлу (асинхронно через потік)
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, shutil.copy2, src_path, dest_path)

        logging.info(f"Copied: {src_path} -> {dest_path}")
    except Exception as e:
        logging.error(f"Failed to copy {src_path}: {e}")

# Асинхронне читання папки рекурсивно
async def read_folder(src_folder: Path, dest_folder: Path):
    tasks = []

    for path in src_folder.rglob("*"):
        if await aiofiles.ospath.isfile(path):
            task = copy_file(path, dest_folder)
            tasks.append(task)

    await asyncio.gather(*tasks)

# Головна функція
async def main():
    parser = argparse.ArgumentParser(description="Async File Sorter by Extension")
    parser.add_argument("source", type=str, help="Source folder path")
    parser.add_argument("output", type=str, help="Output folder path")
    args = parser.parse_args()

    src_folder = Path(args.source)
    dest_folder = Path(args.output)

    if not src_folder.exists():
        logging.error("Source folder does not exist.")
        return

    await read_folder(src_folder, dest_folder)

# Запуск скрипта
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
