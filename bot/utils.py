from datetime import datetime

import requests

from database import DatabaseManager
from models.GHRepository import GHRepository


async def check_for_new_pr(repo: GHRepository) -> str:
    """
    Utility function for checking specific repo's PRs since last access time
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
            return "\n".join([f"New Pull Request at {repo.full_name}: {pr['title']}\n" for pr in new_pull_requests])
        else:
            return f"No new pull requests found for {repo.full_name}.\n"
    else:
        return f"Error fetching pull requests for {repo.full_name}: {response.status_code}\n"


async def check_for_pr(chat_id):
    """
    Utility function for checking all new PRs for chat_id since last access time
    """
    result: list[GHRepository] = await DatabaseManager.get_repos_by_chat_id(chat_id)
    if len(result) > 0:
        text = "Current results for repositories are: \n"
        for repo in result:
            text += await check_for_new_pr(repo)
            await DatabaseManager.update_repos_access_time_by_chat_id(chat_id)
        return text
    else:
        return "Tracked repositories is currently not set."
