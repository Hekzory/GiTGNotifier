import datetime


class GHRepository:
    """
    GHRepository class represents a tracked repository and some settings plus utility information
    """

    def __init__(self, chat_id, full_name, last_pr_time=datetime.datetime.now(), last_commit_time=datetime.datetime.now(),):
        """
        Constructor for the GHRepository class.
        Sets the full name of the repository and records the first access time.
        """
        self.chat_id = chat_id
        self.full_name = full_name
        self.last_pr_time = last_pr_time
        self.last_commit_time = last_commit_time

    def update_name(self, new_name):
        """
        Updates the full name of the repository.
        """
        self.full_name = new_name

    def get_details(self) -> dict:
        """
        Returns a dictionary with the repository's details.
        """
        return {
            'full_name':         self.full_name,
            'last_pr_time': self.last_pr_time.strftime('%Y-%m-%d %H:%M:%S'),
            'last_commit_time': self.last_commit_time.strftime('%Y-%m-%d %H:%M:%S')
        }

    def update_pr_time(self):
        """
        Updates last access time with current time
        """
        self.last_pr_time = datetime.datetime.now()

    def update_commit_time(self):
        """
        Updates last access time with current time
        """
        self.last_commit_time = datetime.datetime.now()