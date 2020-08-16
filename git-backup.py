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

import os
import requests
import json
import datetime
import git


def get_repositories_data_gitlab(url, page):
    response = requests.get(url + '&page=' + str(page))
    return response.json()


def get_repositories_data_github(url, token, page):
    headers = {'Authorization': 'token ' + token}
    response = requests.get(url + '?page=' + str(page), headers=headers)
    return response.json()


backup_data = {}
backup_data['time'] = str(datetime.datetime.now())
backup_data['sites'] = {}

with open('tokens.json', 'r') as tokens_file:
    tokens = json.load(tokens_file)


# gitlab.com
if 'gitlab.com' in tokens:
    url = 'https://gitlab.com/api/v4/projects?private_token=' + tokens['gitlab.com'] + '&per_page=100&membership=true'
    page = 1
    repositories = get_repositories_data_gitlab(url, page)

    backup_data['sites']['gitlab.com'] = []
    while len(repositories) != 0:
        for repository in repositories:
            clone_dir = 'repositories/gitlab.com/' + repository['path_with_namespace']
            print('gitlab.com/' + repository['path_with_namespace'])
            if os.path.isdir(clone_dir):
                git.cmd.Git(clone_dir).fetch()
            else:
                os.system('git clone --mirror ' + repository['ssh_url_to_repo'] + ' ' + clone_dir)
            backup_data['sites']['gitlab.com'].append({
                'name': repository['name'],
                'description': repository['description'],
                'path': repository['path_with_namespace'],
                'ssh_url': repository['ssh_url_to_repo']
            })
        page += 1
        repositories = get_repositories_data_gitlab(url, page)

# github.com
if 'github.com' in tokens:
    url = 'https://api.github.com/user/repos'
    page = 1
    repositories = get_repositories_data_github(url, tokens['github.com'], page)

    backup_data['sites']['github.com'] = []
    while len(repositories) != 0:
        for repository in repositories:
            clone_dir = 'repositories/github.com/' + repository['full_name']
            print('github.com/' + repository['full_name'])
            if os.path.isdir(clone_dir):
                git.cmd.Git(clone_dir).fetch()
            else:
                os.system('git clone --mirror ' + repository['ssh_url'] + ' ' + clone_dir)
            backup_data['sites']['github.com'].append({
                'name': repository['name'],
                'description': repository['description'],
                'path': repository['full_name'],
                'ssh_url': repository['ssh_url']
            })
        page += 1
        repositories = get_repositories_data_github(url, tokens['github.com'], page)

# custom
if os.path.exists('custom_directories.json'):
    with open('custom_directories.json', 'r') as custom_file:
        repositories = json.load(custom_file)

    for repository in repositories:
        clone_dir = 'repositories/' + repository['host'] + '/' + repository['path']
        print(repository['host'] + '/' + repository['path'])
        if os.path.isdir(clone_dir):
            git.cmd.Git(clone_dir).fetch()
        else:
            os.system('git clone --mirror ' + repository['ssh_url'] + ' ' + clone_dir)
        if repository['host'] not in backup_data['sites']:
            backup_data['sites'][repository['host']] = []
        backup_data['sites'][repository['host']].append({
            'name': repository['name'],
            'description': repository['description'],
            'path': repository['path'],
            'ssh_url': repository['ssh_url']
        })

with open('backup_data.json', 'w', encoding='utf-8') as output_file:
    json.dump(backup_data, output_file, ensure_ascii=False)
    output_file.close()
