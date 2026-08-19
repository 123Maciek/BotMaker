"""Opens generated/console text in Notepad. Replaces program.py's
`os.system(f'notepad.exe {temp_file_path}')` (unquoted shell string) with a real
subprocess.run argv call — no shell interpretation of the path."""
import subprocess
import tempfile


def show_in_notepad(text, suffix=".txt"):
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=suffix, encoding="utf-8") as f:
        f.write(text)
        path = f.name
    subprocess.run(["notepad.exe", path])
    return path
