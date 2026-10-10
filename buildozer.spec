[app]

# (str) Title of your application
title = Roblox Overlay Assistant

# (str) Package name
package.name = robloxoverlayassistant

# (str) Package domain
package.domain = org.robloxassistant

# (str) Source code directory
source.dir = .

# (list) Source files to include
source.include_exts = py,png,jpg,kv,atlas,json

# (list) List of directories to exclude
source.exclude_dirs = tests, bin, .git, .github

# (str) Application version
version = 0.1

# (str) Requirements
requirements = python3,kivy,requests

# (str) Orientation of the application
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions needed by the app
android.permissions = INTERNET,SYSTEM_ALERT_WINDOW

# (int) Target Android API
android.api = 33

# (int) Minimum Android API
android.minapi = 21

# (list) Android architectures
android.archs = arm64-v8a

# (bool) Use --private data directory for android app
android.private_storage = True

# (bool) Accept SDK license
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
bin_dir = ./bin
