# wj_build

A simple script that updates, builds, packages, and uploads your game from Godot to Steam.

1. Updates your project (changes the version of your project to an inputted version)
2. Builds your project for Windows, MacOS, and Linux
    - Note that your export configurations should be called "Windows", "macOS" and "Linux".
3. Packages your builds into .zip files for non-Steam uploading
4. Generates Steam scripts and uses them to upload your content to a content depot, and each executable to a platform-specific depot.

## `.env` file

All custom values and project-specific settings are placed in a `.env` file next to the `make_build.py` file.

```py
GODOT_PATH = # Path to Godot executable
STEAMCMD_PATH = # Path to steamcmd exectuable
STEAM_USERNAME = # Your Steam username
PROJECT_PATH = # Path to your Godot Project
PROJECT_NAME = # Name of your game (for executables)

APPID = # Steam appid
CONTENT_DEPOT_ID = # Content depot ID
WINDOWS_DEPOT_ID = # Windows depot ID
MACOS_DEPOT_ID = # macOS depot ID
LINUX_DEPOT_ID = # Linux depot ID
```

## Credits

Written by Angus Goucher (@gusg21), 2025