#!/usr/bin/env python3
# Copyright (C) 2019 Oscar Benedito
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import datetime
import json
import os
import sys
import git
import requests


ENV_GITLAB_TOKEN_PATH = "GITLAB_TOKEN_PATH"
ENV_GITHUB_TOKEN_PATH = "GITHUB_TOKEN_PATH"
ENV_CUSTOM_REPOSITORIES_PATH = "CUSTOM_REPOSITORIES_PATH"
ENV_TARGET_DIR = "TARGET_DIR"


def read_file(env_var):
    token_path = os.environ.get(env_var)
    if not token_path:
        return None
    try:
        with open(token_path, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        print("Error: File {token_path} not found", file=sys.stderr)
        return None


def backup_gitlab(token):
    def get_repositories_data_gitlab(url, page):
        response = requests.get(url + "&page=" + str(page))
        return response.json()

    url = "https://gitlab.com/api/v4/projects?private_token=" + token + "&per_page=100&membership=true"
    page = 1
    repositories = get_repositories_data_gitlab(url, page)

    backup_data["sites"]["gitlab.com"] = []
    while len(repositories) != 0:
        for repository in repositories:
            clone_dir = "repositories/gitlab.com/" + repository["path_with_namespace"]
            print("gitlab.com/" + repository["path_with_namespace"])
            if os.path.isdir(clone_dir):
                git.cmd.Git(clone_dir).fetch()
            else:
                os.system("git clone --mirror " + repository["ssh_url_to_repo"] + " " + clone_dir)
            backup_data["sites"]["gitlab.com"].append(
                {
                    "name": repository["name"],
                    "description": repository["description"],
                    "path": repository["path_with_namespace"],
                    "clone_url": repository["ssh_url_to_repo"],
                }
            )
        page += 1
        repositories = get_repositories_data_gitlab(url, page)


def backup_github(token):
    def get_repositories_data_github(url, token, page):
        headers = {"Authorization": "token " + token}
        response = requests.get(url + "?page=" + str(page), headers=headers)
        return response.json()

    url = "https://api.github.com/user/repos"
    page = 1
    repositories = get_repositories_data_github(url, token, page)

    backup_data["sites"]["github.com"] = []
    while len(repositories) != 0:
        for repository in repositories:
            clone_dir = "repositories/github.com/" + repository["full_name"]
            print("github.com/" + repository["full_name"])
            if os.path.isdir(clone_dir):
                git.cmd.Git(clone_dir).fetch()
            else:
                os.system("git clone --mirror " + repository["ssh_url"] + " " + clone_dir)
            backup_data["sites"]["github.com"].append(
                {
                    "name": repository["name"],
                    "description": repository["description"],
                    "path": repository["full_name"],
                    "clone_url": repository["ssh_url"],
                }
            )
        page += 1
        repositories = get_repositories_data_github(url, token, page)


def backup_custom_repositories(repositories):
    for repository in repositories:
        clone_dir = "repositories/" + repository["host"] + "/" + repository["path"]
        print(repository["host"] + "/" + repository["path"])
        if os.path.isdir(clone_dir):
            git.cmd.Git(clone_dir).fetch()
        else:
            os.system("git clone --mirror " + repository["clone_url"] + " " + clone_dir)
        if repository["host"] not in backup_data["sites"]:
            backup_data["sites"][repository["host"]] = []
        backup_data["sites"][repository["host"]].append(
            {
                "name": repository["name"],
                "description": repository["description"],
                "path": repository["path"],
                "clone_url": repository["clone_url"],
            }
        )


def main():
    try:
        os.makedirs(os.environ.get(ENV_TARGET_DIR), exist_ok=True)
        os.chdir(os.environ.get(ENV_TARGET_DIR))
    except Exception as e:
        print(f"Failed to create directory due to error: {e}", file=sys.stderr)
        return

    backup_data["time"] = str(datetime.datetime.now())
    backup_data["sites"] = {}

    token_path = os.environ.get(ENV_GITLAB_TOKEN_PATH)
    if token_path:
        try:
            with open(token_path, "r") as f:
                token = f.read().strip()
            backup_gitlab(token)
        except FileNotFoundError:
            print("Error: File " + token_path + " not found", file=sys.stderr)

    token_path = os.environ.get(ENV_GITHUB_TOKEN_PATH)
    if token_path:
        try:
            with open(token_path, "r") as f:
                token = f.read().strip()
            backup_github(token)
        except FileNotFoundError:
            print("Error: File " + token_path + " not found", file=sys.stderr)

    custom_repositories_path = os.environ.get(ENV_CUSTOM_REPOSITORIES_PATH)
    if custom_repositories_path:
        try:
            with open(custom_repositories_path, "r") as f:
                repositories = json.load(f)
            backup_custom_repositories(repositories)
        except FileNotFoundError:
            print("Error: File " + custom_repositories_path + " not found", file=sys.stderr)

    with open("backup_data.json", "w", encoding="utf-8") as output_file:
        json.dump(backup_data, output_file, ensure_ascii=False)
        output_file.close()


backup_data = {}
main()
