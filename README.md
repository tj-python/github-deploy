[![Codacy Badge](https://app.codacy.com/project/badge/Grade/867aeabe457f4367b9e0013b713add6b)](https://www.codacy.com/gh/tj-python/github-deploy/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=tj-python/github-deploy&amp;utm_campaign=Badge_Grade)
[![PyPI version](https://badge.fury.io/py/github-deploy.svg)](https://badge.fury.io/py/github-deploy)
[![Upload Python Package](https://github.com/tj-python/github-deploy/actions/workflows/deploy.yml/badge.svg)](https://github.com/tj-python/github-deploy/actions/workflows/deploy.yml) [![Downloads](https://pepy.tech/badge/github-deploy)](https://pepy.tech/project/github-deploy)

# github-deploy

## Using [polyrepo's](https://github.com/joelparkerhenderson/monorepo_vs_polyrepo#what-is-polyrepo) to manage projects ?

This can introduce a number challenges one of which is maintaining consistency across multiple repositories, for files like shared configurations without introducing git submodules or mono repositories which requires a more complex deployment configuration.


> For example adding a github action or maintaing a consistent pull request template accross your organization.

## Solution

`github-deploy` makes maintaining such configurations as easy as a single command.

**Alias** : `gh-deploy`


## Installation

```shell script
pip install github-deploy
```

## Setup 
A Personal Access Token which can be created using this [guide](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)

### Required Scopes
The required scopes are `repo` and `workflow`
<img width="852" alt="Screen Shot 2022-06-11 at 8 16 01 AM" src="https://user-images.githubusercontent.com/17484350/173187599-483bf220-6263-4a81-917f-d0e0dcef3ed9.png">


## Usage

### Upload files to github


```shell script
gh-deploy upload --org [org] --token [PAT_TOKEN] --dest [LOCATION TO UPLOAD FILE] --source [SOURCE FILE LOCATION]
```

Example:

```shell script
gh-deploy upload --org tj-actions --token [PAT_TOKEN] --dest '.github/workflows/auto-approve.yml' --source auto-approve.yml
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
