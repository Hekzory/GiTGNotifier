import datetime


class GHRepository:
    """
    GHRepository class represents a tracked repository and some settings plus utility information
    """

    def __init__(self, full_name):
        """
        Constructor for the GHRepository class.
        Sets the full name of the repository and records the first access time.
        """
        self.full_name = full_name
        self.last_access_time = datetime.datetime.now()

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
            'first_access_time': self.last_access_time.strftime('%Y-%m-%d %H:%M:%S')
        }

    def update_access_time(self):
        """
        Updates last access time with current time
        """
        self.last_access_time = datetime.datetime.now()
