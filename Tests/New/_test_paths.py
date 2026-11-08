"""Result paths for copied tests; input data stays in the original Tests folder."""

from pathlib import Path

save_path = (Path(__file__).resolve().parent / "Results").as_posix()
save_plot_path = (Path(save_path) / "Plot").as_posix()
save_validation_path = (Path(save_path) / "Validation").as_posix()
save_load_path = (Path(save_path) / "Save_Load").as_posix()
save_gui_path = (Path(save_path) / "GUI").as_posix()
SCHEMATICS_PATH = (Path(save_plot_path) / "Schematics").as_posix()
SCHEMATICS_POINT_PATH = (Path(SCHEMATICS_PATH) / "Point").as_posix()

for path in (
    save_plot_path,
    save_validation_path,
    save_load_path,
    save_gui_path,
    SCHEMATICS_PATH,
    SCHEMATICS_POINT_PATH,
):
    Path(path).mkdir(parents=True, exist_ok=True)
