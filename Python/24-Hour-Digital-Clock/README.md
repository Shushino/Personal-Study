# 24-Hour Clock App

This is a small beginner-friendly Tkinter clock project that can switch between digital and analogue views while keeping the app fully desktop-based.

## Features

- Digital and analogue clock modes
- 24-hour mode by default for the digital view
- Optional 12-hour digital mode with AM/PM
- Optional date display shown below the active clock view
- Three date display presets:
  - `YYYY-MM-DD`
  - `DD/MM/YYYY`
  - `Month DD, YYYY`
- Timezone selection with common presets and typed IANA names like `Africa/Lagos`
- `Show Seconds` toggle for digital text and the analogue second hand
- Multiple alarms with daily or one-time repeat behavior
- Saved settings for display mode, timezone, alarms, and formatting choices
- Windows packaging support for a portable `.exe` folder build or a single-file `.exe`

## Project Structure

- `24-Hour-Digital-Clock.py` - main GUI launcher
- `clock_gui.py` - alternate GUI launcher
- `clock_app/` - shared clock logic, GUI code, analogue rendering, alarms, and settings persistence
- `tests/` - unit tests for core formatting, GUI state, alarms, and storage behavior
- `build_exe.ps1` - PowerShell build script for Windows packaging
- `build_exe.cmd` - Command Prompt friendly wrapper for the PowerShell build script
- `24-Hour-Digital-Clock-Pseudocode.txt` - maintained pseudocode for the current design
- `24-Hour-Digital-Clock-Flowchart.jpg` - an older flowchart image kept as a reference

## Controls

### Menu Bar

- `File -> Exit`
- `Format -> 12-hour / 24-hour`
- `Format -> Date Format -> YYYY-MM-DD / DD/MM/YYYY / Month DD, YYYY`
- `View -> Show Date`

### Settings Panel

- Switch between digital and analogue clock mode
- Choose a timezone from common presets or type a valid IANA timezone
- Toggle `Show Seconds`
- Add, edit, delete, enable, and disable alarms

## Alarm Notes

- Alarm times use `HH:MM`
- Daily alarms stay active until you disable or delete them
- One-time alarms fire on the next matching occurrence and then turn themselves off
- Alarm notifications use a popup window plus a system beep

## Settings Persistence

The app stores its last-used settings in a platform-appropriate local settings directory:

- Windows: `%LOCALAPPDATA%\24-Hour-Digital-Clock\settings.json`
- macOS: `~/Library/Application Support/24-Hour-Digital-Clock/settings.json`
- Linux: `~/.local/share/24-Hour-Digital-Clock/settings.json`

If the settings file is missing or contains invalid values, the app falls back to safe defaults.

## Running From Source

This project requires Python 3.10 or later.

From the project folder:

```powershell
python clock_gui.py
```

Or use the main launcher:

```powershell
python 24-Hour-Digital-Clock.py
```

On macOS or Linux, use the same commands with the Python interpreter available on your system:

```bash
python3 clock_gui.py
```

You can also launch the package as a module from the project folder:

```bash
python3 -m clock_app
```

For a window-only launch on Windows without an attached console:

```powershell
pythonw 24-Hour-Digital-Clock.py
```

## Building The Portable EXE Folder

Install PyInstaller once:

```powershell
"C:\Path\To\Python\python.exe" -m pip install pyinstaller
```

Run the build script from this folder:

```powershell
.\build_exe.ps1
```

If PowerShell blocks local scripts on your machine, use the wrapper instead:

```cmd
build_exe.cmd
```

The portable app folder will be created at:

```text
dist\24-Hour-Digital-Clock\
```

You can copy that whole folder into an asset folder or move it anywhere on a Windows machine.

To produce a single-file `.exe` instead:

```powershell
.\build_exe.ps1 -OneFile
```

Or from Command Prompt:

```cmd
build_exe.cmd -OneFile
```

That output will be created at:

```text
dist\24-Hour-Digital-Clock.exe
```

## Building On macOS / Linux

This repository also includes a Unix-friendly build script.

Install PyInstaller if needed:

```bash
python3 -m pip install --user pyinstaller
```

Run the build script from this folder:

```bash
./build_exe.sh
```

The portable app folder will be created at:

```text
dist/24-Hour-Digital-Clock/
```

Note: `build_exe.sh` and `build_exe.ps1` each produce a platform-specific output. A Windows `.exe` bundle is useful if you want to distribute to users who do not have Python installed, but it is not required for macOS or Linux deployments.

## Testing

Run the test suite with:

```powershell
python -m unittest discover -s tests -v
```

## Notes

- The runtime app uses only the Python standard library.
- Time format changes affect the digital view; the analogue face stays analogue-only.
- PyInstaller is only needed when you want to create the Windows executable build.
- The script ignores the Microsoft Store `python.exe` alias and looks for a real Python interpreter on your PATH.
- This project is intentionally simple and beginner-friendly.
