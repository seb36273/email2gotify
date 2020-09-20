# -*- coding: utf8 -*-


import os
import toml
import requests
import simplejson as json

from . import CFG_PATH 


class Gotify:
    def __init__(self):
        config = toml.load([os.path.abspath(CFG_PATH)])
        self.gotify_server = config["gotify"]["host"]
        self.gotify_token = config["gotify"]["token"]

        self.verbose = False
        if "verbose" in config["main"]:
            self.verbose = config["main"]["verbose"]

    def push(self, mail):

        if "token" in mail:
            self.gotify_token = mail["token"]

        params = {
            "title": mail["subject"],
            "message": mail["body"],
            "priority": mail["priority"],
        }

        if "extras" in mail:
            params["extras"] = mail["extras"]

        if self.verbose:
            print(json.dumps(params))

        push = requests.post(
            f"{self.gotify_server}/message?token={self.gotify_token}", json=params
        )

        if push.status_code != 200:
            print(f">>> Error: {push.status_code}")
            return False

        print(
            f">>>> Gotify for email: {params['title']} with priority {params['priority']}"
        )

        return True


if __name__ == "__main__":
    pass