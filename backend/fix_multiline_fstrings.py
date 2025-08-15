# fix_multiline_fstrings.py
from pathlib import Path
import re, sys

src = Path(sys.argv[1])
code = src.read_text(encoding="utf-8", errors="replace")

def collapse(s: str) -> str:
    def squish(fragment: str) -> str:
        def repl(m):
            inner = re.sub(r"\s+", " ", m.group(1)).strip()
            return "{" + inner + "}"
        return re.sub(r"\{\s*\n\s*(.+?)\}", repl, fragment, flags=re.S)

    s = re.sub(r'(f"[^"\n]*\{\s*\n.*?\}[^"\n]*")',
               lambda m: squish(m.group(1)), s, flags=re.S)
    s = re.sub(r"(f'[^'\n]*\{\s*\n.*?\}[^'\n]*')",
               lambda m: squish(m.group(1)), s, flags=re.S)
    return s

fixed = collapse(code)
Path(src.with_name(src.stem + "_fixed.py")).write_text(fixed, encoding="utf-8")
print("Wrote:", src.with_name(src.stem + "_fixed.py"))
