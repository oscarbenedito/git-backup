# Git Backup

Very simple script to back up all the repositories the user is member of on
GitLab and GitHub.

## Prerequisites

In order to run the program, you will need `python3` and the python libraries
specified in the `requirements.txt` file. If you have `pip3` installed, you can
install the libraries with the command:

```
pip3 install -r requirements.txt
```

## Running the program

To run the program, execute the file `git-backup.py`, you must set the
`TARGET_DIR` variable to the path where you want the script to store all the
backed up repositories.

```
python3 git-backup.py
```

### Adding you GitLab and GitHub repositories

You will also need a GitLab and a GitHub access token and crete a file for each
token, with the content being only the token. You must set environment variables
`GITLAB_TOKEN_PATH` and `GITHUB_TOKEN_PATH` with the path of the file with each
token.

Finally, you must upload your ssh key to GitLab or GitHub if you have any
private or internal repositories.

### Adding custom repositories

If you want to backup repositories from which you are not a member on the
currently supported hosts, or if you want to add repositories from other hosts,
you can do so creating a file with the following structure:

```json
[
  {
    "name":"<Repository name - for backup information>",
    "description":"<Repository description - for backup information>",
    "path":"<Repository path where the backup will be saved>",
    "ssh_url":"<Repository url>",
    "host":"<Repository host - for backup information and establishing saving directory>"
  }
]
```

You can add more than one object to the array and it will backup all of the
repositories. Make sure that you upload your ssh key to the hosts in case it is
needed for authentification. Set the environment variable
`CUSTOM_REPOSITORIES_PATH` to the path of the file.

## Future updates

- [ ] More information on the output file or the terminal: how many new
      repositories were added, how many have been deleted on the hosting
      services.
- [ ] Manage what happens if history has changed in the hosting service.

## License

The program is licensed under the GNU Affero General Public License version 3 or
later (available [here][agpl]).

## Author

- **Oscar Benedito** - oscar@oscarbenedito.com

[agpl]: <https://www.gnu.org/licenses/agpl-3.0.html> "GNU Affero General Public License v3.0"
