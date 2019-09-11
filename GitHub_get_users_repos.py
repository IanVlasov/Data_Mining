import requests
import json
import time
import random


class GitUserReposParser:
    USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 " \
                 "(KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36 "

    def __init__(self, username):
        self.username = str(username)
        self.user_url = f"https://api.github.com/users/{self.username}"
        self.repos_url = f"https://api.github.com/users/{self.username}/repos"
        self.repos = {}

    def parse(self):
        first_response = requests.get(self.user_url, headers={'User-Agent': self.USER_AGENT}).json()
        quantity_of_repos = first_response.get('public_repos')
        self.repos['Total_repos'] = quantity_of_repos

        for page_number in range(1, quantity_of_repos // 100 + 2):

            main_response = requests.get(self.repos_url, params={'page': page_number, 'per_page': 100},
                                         headers={'User-Agent': self.USER_AGENT}).json()
            print(len(main_response))

            for repo in main_response:
                self.repos[repo.get('name')] = repo.get('html_url')
            print(len(self.repos))

            time.sleep(random.randrange(0, 3))

        with open(f"repos_{self.username}.json", "w", encoding="utf-8") as file:
            json.dump(self.repos, file)


if __name__ == '__main__':
    test = GitUserReposParser('microsoft')
    test.parse()

