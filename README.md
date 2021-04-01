[![PyPI version](https://badge.fury.io/py/github-deploy.svg)](https://badge.fury.io/py/github-deploy)
[![Upload Python Package](https://github.com/tj-python/github-deploy/actions/workflows/python-publish.yml/badge.svg)](https://github.com/tj-python/github-deploy/actions/workflows/python-publish.yml)

# github-deploy

## Problem
Using [poly repositories](https://github.com/joelparkerhenderson/monorepo_vs_polyrepo#what-is-polyrepo) to manage projects ?

This can introduce a number challenges one of which is maintaining consistency across multiple repositories for files like shared configurations in your organization without introducing git submodules.


> For example adding a github action or maintaing a consistent pull request template accross your organization.


## Usage

#### Creating or Updating files on github

`github-deploy`

```shell script
github-deploy --org [org] --token [PAT_TOKEN] --dest [LOCATION TO UPLOAD FILE] --source [SOURCE FILE LOCATION]
```

Example:

```shell script
github-deploy --org tj-actions --token [PAT_TOKEN] --dest '.github/workflows/auto-approve.yml' --source auto-approve.yml
```

> NOTE: `auto-approve.yml` is located on your local system.


#### Deleting files on github

`github-delete`

```shell script
github-delete --org [org] --token [PAT_TOKEN] --dest [LOCATION TO DELETE]
```

Example:

```shell script
github-delete --org tj-actions --token [PAT_TOKEN] --dest '.github/auto-approve.yml'
```


### Resources
- http://www.gigamonkeys.com/mono-vs-multi/
