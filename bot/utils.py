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
            if pr_created_at > repo.last_pr_time:
                new_pull_requests.append(pr)

        if new_pull_requests:
            return "\n".join(
                [f"New Pull Request at '{repo.full_name}': \"{pr['title']}\"\n" for pr in new_pull_requests])
        else:
            # return f"No new pull requests found for '{repo.full_name}'.\n"
            return ""
    else:
        return f"Error fetching pull requests for '{repo.full_name}': \"{response.status_code}\"\n"


async def check_for_pr_auto(chat_id):
    """
    Utility function for auto checking all new PRs for chat_id since last access time
    """
    result: list[GHRepository] = await DatabaseManager.get_repos_by_chat_id(chat_id)
    text = ""
    if len(result) > 0:
        for repo in result:
            text += await check_for_new_pr(repo)
            await DatabaseManager.update_repos_pr_time_by_chat_id(chat_id)
    return text


async def check_for_pr(chat_id):
    """
    Utility function for checking all new PRs for chat_id since last access time
    """
    result: list[GHRepository] = await DatabaseManager.get_repos_by_chat_id(chat_id)
    if len(result) > 0:
        text = ""
        for repo in result:
            text += await check_for_new_pr(repo)
            await DatabaseManager.update_repos_pr_time_by_chat_id(chat_id)
        if len(text) > 0:
            return "Current results for pull requests are: \n" + text
        else:
            return "No updates"
    else:
        return "Tracked repositories are currently not set."


async def check_for_new_commits(repo: GHRepository) -> str:
    """
    Utility function for checking specific repo's commits since last access time
    """

    url = f'https://api.github.com/repos/{repo.full_name}/commits'

    response = requests.get(url)

    if response.status_code == 200:
        commits = response.json()
        new_commits = []

        for commit in commits:
            commit_created_at = datetime.strptime(commit['commit']['committer']['date'], '%Y-%m-%dT%H:%M:%SZ')
            if commit_created_at > repo.last_commit_time:
                new_commits.append(commit)

        if new_commits:
            return "\n".join(
                [f"New commit at '{repo.full_name}': \"{commit['commit']['message']}\"\n" for commit in new_commits])
        else:
            # return f"No new commits found for '{repo.full_name}'.\n"
            return ""
    else:
        return f"Error fetching commits for '{repo.full_name}': \"{response.status_code}\"\n"


async def check_for_commits_auto(chat_id):
    """
    Utility function for auto checking all new commits for chat_id since last access time
    """
    result: list[GHRepository] = await DatabaseManager.get_repos_by_chat_id(chat_id)
    text = ""
    if len(result) > 0:
        for repo in result:
            text += await check_for_new_commits(repo)
            await DatabaseManager.update_repos_commit_time_by_chat_id(chat_id)
    return text


async def check_for_commits(chat_id):
    """
    Utility function for checking all new commits for chat_id since last access time
    """
    result: list[GHRepository] = await DatabaseManager.get_repos_by_chat_id(chat_id)
    text = ""
    if len(result) > 0:
        for repo in result:
            text += await check_for_new_commits(repo)
            await DatabaseManager.update_repos_commit_time_by_chat_id(chat_id)
        if len(text) > 0:
            return "Current results for commits are: \n" + text
        else:
            return "No updates"
    else:
        return "Tracked repositories are currently not set."
