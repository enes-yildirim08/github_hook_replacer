# GitHub Repository Hook Management

This script manages hooks in your GitHub repositories. It retrieves all projects from the specified organization, checks for old hooks, deletes them if necessary, and adds new hooks.

## Prerequisites

Before running the script, make sure you have the following:

- Python 3.x installed
- `requests` library installed (`pip install requests`)
- `config.ini` file in the same directory as the script, containing the necessary configuration (see Configuration section below)

## Configuration

Create a `config.ini` file in the same directory as the script with the following content:

```ini
[DEFAULT]
API_KEY = YOUR_GITHUB_API_KEY
REPO_OWNER = YOUR_ORGANIZATION_NAME
expired_hooks =
    https://old-hook-url-1.com
    https://old-hook-url-2.com
new_hook_url = https://new-hook-url.com
```