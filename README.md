# GitHub Repository Scheduler

This script automates the process of uploading repositories to GitHub on a scheduled basis. It supports automatic repo creation, file commits, and push operations. Additionally, it provides a notification after each upload and asks the user if they want to upload more repositories after all scheduled uploads are completed.

## Features
- **Automated Uploads**: Schedules and uploads repositories to GitHub based on user-defined time and days.
- **GitHub API Integration**: Automatically creates repositories and pushes code.
- **Interactive UI**: Uses dialog boxes for file selection, directory selection, and user confirmation.
- **Persistence**: Stores user credentials (GitHub username, email, and name) for future runs.
- **Post-Upload Confirmation**: Asks the user if they want to upload more repositories after all scheduled uploads are completed.
- **Systemd Service Support**: Can run as a background daemon on Linux systems.

## Installation
### Prerequisites
Ensure you have **Python 3** installed.

### Install Dependencies
```sh
pip install -r requirements.txt
