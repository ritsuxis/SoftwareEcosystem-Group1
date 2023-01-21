import os
import json
import requests
from string import Template
from dotenv import load_dotenv

load_dotenv('.env')
token = os.environ.get('GITHUB_TOKEN')

def post(query):
    headers = {"Authorization": "bearer " + token}
    res = requests.post('https://api.github.com/graphql', json={"query":query}, headers=headers)
    if res.status_code != 200:
      raise Exception("failed : {}".format(res.status_code))
    return res.json()

top_100_repos_query ="""
  query {
    search(query: "stars:>=10000 sort:stars", type: REPOSITORY, first: 100) {
      edges {
        node {
          ... on Repository {
            nameWithOwner
            url
          }
        }
      }
    }
  }
  """

# タイトルか本文に"master"と"branch"が含まれるissueを取得するクエリ
issue_search_query =  Template("""
  query {
    search(
      query: "repo:${repo_name} rename master branch in:title,body",
      type: ISSUE,
      first: 100
  ) {
    nodes {
      ... on Issue {
        url
        title
      }
      ... on PullRequest {
        url
        title
      }
    }
  }
}
""")

# star数上位100のリポジトリを取得
top_100_repos = post(top_100_repos_query)

for i in range(100):
  repo_name = top_100_repos['data']['search']['edges'][i]['node']['nameWithOwner']
  issues = post(issue_search_query.substitute(repo_name=repo_name))
  path = 'data/' + repo_name.split('/')[1] + '.json'
  with open(path, 'w') as f:
    f.write(json.dumps(issues, indent=2))
