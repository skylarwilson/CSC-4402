import os
import subprocess
from pathlib import Path


def test_cli():
    def delete_file_subprocess(path: str | os.PathLike, timeout: int = 30):
        """Delete a file via subprocess. Raises if the command fails."""
        path = str(Path(path))

        if os.name == "nt":
            # Windows: use the built-in `del` via cmd
            cmd = ["cmd", "/c", "del", "/f", "/q", path]
        else:
            # POSIX: use rm -f, with `--` to avoid treating names starting with '-' as flags
            cmd = ["rm", "-f", "--", path]

        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if p.returncode != 0:
            raise RuntimeError(
                f"Delete failed ({p.returncode}) for {path}\n"
                f"stdout:\n{p.stdout}\n"
                f"stderr:\n{p.stderr}"
            )
        

    # subprocess.run(["cards", "delete_db"], check=True)
    delete_file_subprocess("./shop.db")
    assert subprocess.run(["cards", "init-db"], capture_output=True, text=True).returncode == 0
    assert subprocess.run(["cards", "list_c"], capture_output=True, text=True).returncode == 0
    assert subprocess.run(["cards", "list_e"], capture_output=True, text=True).returncode == 0
    assert subprocess.run(["cards", "get", "1"], capture_output=True, text=True).returncode == 0
    assert subprocess.run(["cards", "get_emp", "1"], capture_output=True, text=True).returncode == 0
    assert subprocess.run(["cards", "add", "name", "set_name", "rarity", "67", "--stock", "67"], capture_output=True, text=True).returncode == 0
    assert subprocess.run(["cards", "delete", "67"], capture_output=True, text=True).returncode == 0
    assert subprocess.run(["cards", "add_emp", "67", "hello", "world", "mad"], capture_output=True, text=True).returncode == 0
    assert subprocess.run(["cards", "delete_e", "67"], capture_output=True, text=True).returncode == 0
    assert subprocess.run(["cards", "update", "1", "--stock", "67"], capture_output=True, text=True).returncode == 0
    assert subprocess.run(["cards", "update_e", "1", "--city", "67"], capture_output=True, text=True).returncode == 0
    assert subprocess.run(["cards", "list_c"], capture_output=True, text=True).returncode == 0
    assert subprocess.run(["cards", "list_e"], capture_output=True, text=True).returncode == 0
    print("All tests passed.")
    
if __name__ == "__main__":
    test_cli()