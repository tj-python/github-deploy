[![PyPI version](https://badge.fury.io/py/github-deploy.svg)](https://badge.fury.io/py/github-deploy)
[![Upload Python Package](https://github.com/tj-python/github-deploy/actions/workflows/python-publish.yml/badge.svg)](https://github.com/tj-python/github-deploy/actions/workflows/python-publish.yml)

# github-deploy

## Problem
Using [poly repositories](https://github.com/joelparkerhenderson/monorepo_vs_polyrepo#what-is-polyrepo) to manage projects ?

This can introduce a number challenges one of which is maintaining consistency across multiple repositories, for files like shared configurations without introducing git submodules or mono repositories which requires a more complex deployment configuration.


> For example adding a github action or maintaing a consistent pull request template accross your organization.


`github-deploy` makes maintaining such configurations as easy as a single command.


## Usage

### Creating or Updating files on github


```shell script
github-deploy update --org [org] --token [PAT_TOKEN] --dest [LOCATION TO UPLOAD FILE] --source [SOURCE FILE LOCATION]
```

Example:

```shell script
github-deploy update --org tj-actions --token [PAT_TOKEN] --dest '.github/workflows/auto-approve.yml' --source auto-approve.yml
```

> NOTE: `auto-approve.yml` is located on your local system.


### Deleting files on github


```shell script
github-deploy delete --org [org] --token [PAT_TOKEN] --dest [LOCATION TO DELETE]
```

Example:

```shell script
github-deploy delete --org tj-actions --token [PAT_TOKEN] --dest '.github/auto-approve.yml'
```


### Resources
- http://www.gigamonkeys.com/mono-vs-multi/
