[![PyPI version](https://badge.fury.io/py/github-deploy.svg)](https://badge.fury.io/py/github-deploy)
[![Upload Python Package](https://github.com/tj-python/github-deploy/actions/workflows/python-publish.yml/badge.svg)](https://github.com/tj-python/github-deploy/actions/workflows/python-publish.yml) [![Downloads](https://pepy.tech/badge/github-deploy)](https://pepy.tech/project/github-deploy)

# github-deploy

## Problem
Using [poly repositories](https://github.com/joelparkerhenderson/monorepo_vs_polyrepo#what-is-polyrepo) to manage projects ?

This can introduce a number challenges one of which is maintaining consistency across multiple repositories, for files like shared configurations without introducing git submodules or mono repositories which requires a more complex deployment configuration.


> For example adding a github action or maintaing a consistent pull request template accross your organization.


## Solution

`github-deploy` makes maintaining such configurations as easy as a single command.

**Alais** : `gh-deploy`


## Usage

### Creating or Updating files on github


```shell script
gh-deploy update --org [org] --token [PAT_TOKEN] --dest [LOCATION TO UPLOAD FILE] --source [SOURCE FILE LOCATION]
```

Example:

```shell script
gh-deploy update --org tj-actions --token [PAT_TOKEN] --dest '.github/workflows/auto-approve.yml' --source auto-approve.yml
```

> NOTE: `auto-approve.yml` is located on your local system.


### Deleting files on github


```shell script
gh-deploy delete --org [org] --token [PAT_TOKEN] --dest [LOCATION TO DELETE]
```

Example:

```shell script
gh-deploy delete --org tj-actions --token [PAT_TOKEN] --dest '.github/auto-approve.yml'
```



## COMMAND
`gh-deploy --help`

```
Usage: gh-deploy [OPTIONS] COMMAND [ARGS]...

  Deploy changes to multiple github repositories using a single command.

Options:
  --help  Show this message and exit.

Commands:
  delete  Delete a file in all repositories owned by an organization/user.
  upload  Upload a file to all repositories owned by an organization/user.

```

`gh-deploy upload --help`

```
Usage: gh-deploy upload [OPTIONS]

  Upload a file to all repositories owned by an organization/user.

Options:
  --org TEXT                    The github organization.
  --token TEXT                  Personal Access token with read and write
                                access to org.

  --source PATH                 Source file.
  --dest TEXT                   Destination path.
  --overwrite / --no-overwrite  Overwrite existing files.
  --private / --no-private      Upload files to private repositories.
  --help                        Show this message and exit.
```

`gh-deploy delete --help`

```
Usage: gh-deploy delete [OPTIONS]

  Delete a file in all repositories owned by an organization/user.

Options:
  --org TEXT    The github organization.
  --token TEXT  Personal Access token with read and write access to org.
  --dest TEXT   Destination path to delete.
  --help        Show this message and exit.
```

### Resources
- http://www.gigamonkeys.com/mono-vs-multi/
