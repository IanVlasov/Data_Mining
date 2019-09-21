import requests
import json

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 " \
             "(KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36 "

api_url = "https://api.github.com/user/repos"

response_without_auth = requests.get(api_url, headers={'User-Agent': USER_AGENT}).json()

with open(f"response_without_auth.json", "w", encoding="utf-8") as file:
    json.dump(response_without_auth, file)

response_with_auth = requests.get(api_url, params={'access_token': '----------------------------'},
                                  headers={'User-Agent': USER_AGENT}).json()

repos = {}

for repo in response_with_auth:
    repos[repo.get('name')] = repo.get('html_url')

with open(f"response_with_auth.json", "w", encoding="utf-8") as file:
    json.dump(repos, file)
