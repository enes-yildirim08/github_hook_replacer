import requests
import json
import configparser

# Retrieve the API key and other configuration from the config file
config = configparser.ConfigParser()
config.read('config.ini')

API_KEY = config['DEFAULT']['API_KEY']
REPO_OWNER = config['DEFAULT']['REPO_OWNER']
expired_hooks = [hook.strip() for hook in config['DEFAULT']['expired_hooks'].split('\n') if hook.strip()]
new_hook_url = config['DEFAULT']['new_hook_url']

# Header information for GitHub API requests
headers = {
    'Authorization': f'token {API_KEY}',
    'Accept': 'application/vnd.github.v3+json'
}

# Use the GitHub API to get all projects
def get_projects():
    project_list = []
    page = 1
    per_page = 500

    while True:
        url = f'https://api.github.com/orgs/{REPO_OWNER}/repos?per_page={per_page}&page={page}'
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if not data:
                break
            
            project_list.extend(data)
            
            link_header = response.headers.get('Link')
            if link_header and 'rel="next"' not in link_header:
                break
            
            page += 1
        
        except requests.exceptions.RequestException as e:
            print(f'Error while fetching projects: {e}')
            break

    return project_list


# Use the GitHub API to get the hooks of a project
def get_hooks(project_name):
    url = f'https://api.github.com/repos/{REPO_OWNER}/{project_name}/hooks'
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f'Error while getting hooks: {e}')
        return []

# Use the GitHub API to delete a hook
def delete_hook(project_name, hook_id):
    url = f'https://api.github.com/repos/{REPO_OWNER}/{project_name}/hooks/{hook_id}'
    try:
        response = requests.delete(url, headers=headers)
        response.raise_for_status()
        return response.status_code
    except requests.exceptions.RequestException as e:
        print(f'Error while deleting hook: {e}')
        return None

# Use the GitHub API to create a hook
def create_hook(project_name, hook_config):
    url = f'https://api.github.com/repos/{REPO_OWNER}/{project_name}/hooks'
    try:
        response = requests.post(url, headers=headers, data=json.dumps(hook_config))
        response.raise_for_status()
        return response.status_code
    except requests.exceptions.RequestException as e:
        print(f'Error while creating hook: {e}')
        return None

# Get all projects
projects = get_projects()

# Check each project
for project in projects:
    project_name = project['name']
    hooks = get_hooks(project_name)

    # Only process repositories with old hooks
    add_hook = False

    is_already_in_hooks = any(hook['config']['url'] == new_hook_url for hook in hooks)

    if is_already_in_hooks:
        print(f'Hook already exists in project {project_name}')

    if len(hooks) == 0 or hooks[0]['name'] != 'web':
        continue

    # Check each hook
    for hook in hooks:
        hook_id = hook['id']

        # Check and delete the hooks you want to remove here
        if hook['name'] == 'web' and hook['config']['url'] in expired_hooks:
            status_code = delete_hook(project_name, hook_id)
            if status_code == 204:
                print(f'Successfully deleted hook {hook_id} from project {project_name}')
                add_hook = True
            else:
                print(f'Failed to delete hook {hook_id} from project {project_name}')

    # Check and add the hooks you want to add here
    if add_hook and not is_already_in_hooks:
        hook_config_to_add = {
            'name': 'web',
            'active': True,
            'events': ['pull_request', 'push'],
            'config': {
                'url': new_hook_url,
                'content_type': 'json',
                'insecure_ssl': 0
            }
        }
        status_code = create_hook(project_name, hook_config_to_add)
        if status_code == 201:
            print(f'Successfully created hook in project {project_name}')
        else:
            print(f'Failed to create hook in project {project_name}')
