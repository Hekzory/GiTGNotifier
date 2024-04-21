from datetime import datetime

import requests

from models.GHRepository import GHRepository


async def check_for_new_pr(repo: GHRepository) -> str:
    """
    Utility function for checking if there are any new PRs since last access time
    """

    url = f'https://api.github.com/repos/{repo.full_name}/pulls'

    response = requests.get(url)

    if response.status_code == 200:
        pull_requests = response.json()
        new_pull_requests = []

        for pr in pull_requests:
            pr_created_at = datetime.strptime(pr['created_at'], '%Y-%m-%dT%H:%M:%SZ')
            if pr_created_at > repo.last_access_time:
                new_pull_requests.append(pr)

        if new_pull_requests:
            return "\n".join([f"New Pull Request: {pr['title']}" for pr in new_pull_requests])
        else:
            return "No new pull requests found."
    else:
        return f"Error fetching pull requests: {response.status_code}"
