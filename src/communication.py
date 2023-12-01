from typing import Union
import requests

class Channel:
    """
    Represents a communication channel with a host computer.

    Args:
        ip_addr (str): The IP address of the host computer.
        username (str): The username for authentication.
        password (str): The password for authentication.
    """

    def __init__(self, ip_addr: str, username:str, password:str) -> None:
        self.host_computer_ip = ip_addr
        self.username = username
        self.password = password

    def initialize_team(self) -> str:
        """
        Initializes the team on the host computer.

        Returns:
            str: The target of the team.
        """
        response = requests.get(f"http://{self.host_computer_ip}/initTeam/{self.username}/{self.password}", timeout=10)
        dct = response.json()
        return dct["target"]

    def practice_restart(self) -> None:
        """
        Restarts the practice session on the host computer.
        """
        requests.get(f"http://{self.host_computer_ip}/practiceRestart", timeout=10)

    def change_flower(self, tag_id:int, from_flower: str, to_flower: str) -> Union[int, None]:
        """
        Changes the flower on a specific tag.

        Args:
            tag_id (int): The ID of the tag.
            from_flower (str): The current flower.
            to_flower (str): The new flower.

        Returns:
            Union[int, None]: The score if the change is successful, None otherwise.
        """
        response = requests.get(f"http://{self.host_computer_ip}/change/{self.username}/{self.password}/at/{tag_id}/from/{from_flower}/to/{to_flower}",
                                 timeout=3)
        ret, score_text = response.text.split()
        if ret == "Wrong":
            return None
        return int(score_text)
    