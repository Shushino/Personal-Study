# 24-Hour Digital Clock

This is a small beginner Tkinter desktop clock project that updates every second and now runs as a GUI-only application.

## Features

- Live local time updates every second
- 24-hour mode by default
- Optional 12-hour mode with AM/PM
- Optional date display shown below the time
- Three date display presets:
  - `YYYY-MM-DD`
  - `DD/MM/YYYY`
  - `Month DD, YYYY`
- Saved user preferences for time format, date visibility, and date format
- Windows packaging support for a portable `.exe` folder build

## Project Structure

- `24-Hour-Digital-Clock.py` - main GUI launcher
- `clock_gui.py` - alternate GUI launcher
- `clock_app/` - shared clock logic, GUI code, and settings persistence
- `tests/` - unit tests for formatting, GUI state, and settings persistence
- `build_exe.ps1` - PowerShell build script for the Windows `onedir` package
- `24-Hour-Digital-Clock-Pseudocode.txt` - maintained pseudocode for the current design
- `24-Hour-Digital-Clock-Flowchart.jpg` - an older flowchart image kept as a reference

## Menu Options

- `File -> Exit`
- `Format -> 12-hour / 24-hour`
- `Format -> Date Format -> YYYY-MM-DD / DD/MM/YYYY / Month DD, YYYY`
- `View -> Show Date`

## Settings Persistence

The app stores its last-used settings in:

```text
%LOCALAPPDATA%\24-Hour-Digital-Clock\settings.json
```

If that file is missing or invalid, the app falls back to the default settings.

## Running From Source

From the project folder:

```powershell
python clock_gui.py
```

Or use the main launcher:

```powershell
python 24-Hour-Digital-Clock.py
```

For a window-only launch on Windows without an attached console:

```powershell
pythonw 24-Hour-Digital-Clock.py
```

## Building The Portable EXE Folder

Install PyInstaller once:

```powershell
python -m pip install pyinstaller
```

Run the build script from this folder:

```powershell
.\build_exe.ps1
```

The portable app folder will be created at:

```text
dist\24-Hour-Digital-Clock\
```

You can copy that entire folder into an asset folder or move it anywhere on a Windows machine.

## Testing

Run the test suite with:

```powershell
python -m unittest discover -s tests -v
```

## Notes

- The runtime app uses only the Python standard library.
- PyInstaller is only needed when you want to create the Windows executable build.
- This project is intentionally simple and beginner-friendly.
