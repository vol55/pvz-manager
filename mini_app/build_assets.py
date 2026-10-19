from pathlib import Path

from rcssmin import cssmin
from rjsmin import jsmin

SRC = Path("static")

# Минимизирует все файлы в папке static
for file in SRC.iterdir():
    if file.suffix == ".js" and not file.stem.endswith(".min"):
        output = file.with_name(f"{file.stem}.min.js")
        output.write_text(
            jsmin(file.read_text(encoding="utf-8")),
            encoding="utf-8",
        )

    elif file.suffix == ".css" and not file.stem.endswith(".min"):
        output = file.with_name(f"{file.stem}.min.css")
        output.write_text(
            cssmin(file.read_text(encoding="utf-8")),
            encoding="utf-8",
        )

print("Done")
