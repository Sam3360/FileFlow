# FileFlow

FileFlow is a keyboard-first terminal file manager for Windows built with Python and Textual.

## Features

- Browse folders and drives in a desktop-style terminal interface
- Open folders and files using the system default application
- Rename, copy, move, paste, and delete items with confirmation dialogs
- Multi-select and filter hidden items
- Search filenames recursively with a cancelable worker
- Text preview for files and item properties panel
- Quick access to common Windows locations
- Safe handling of file conflicts and filesystem errors

## Requirements

- Python 3.11+
- Windows 10 or Windows 11
- Textual and PyInstaller

## Installation

From a Windows terminal:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
```

## Launching

```powershell
python -m fileflow
```

Or use the provided script:

```powershell
.\scripts\launch.bat
```

## Keyboard shortcuts

- Arrow keys: move through items
- Enter: open selected item or enter folder
- Space: toggle selection
- Tab / Shift+Tab: move focus between panels
- Escape: close dialog or go back
- Ctrl+L: show location prompt
- Ctrl+F: focus search
- Ctrl+S: toggle hidden files
- Ctrl+R: refresh
- Delete: delete selected item(s)

## Testing

```powershell
pytest
```

## Standalone executable

```powershell
pyinstaller --onefile --windowed --name FileFlow --distpath dist .\fileflow\__main__.py
```

## Known limitations

- Image previews are not implemented in the MVP.
- Some Windows terminal environments may not support all mouse or color features.
- File operations are intentionally conservative and do not overwrite files without explicit confirmation.