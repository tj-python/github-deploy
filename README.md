# github-deploy

Using poly repositories to manage projects can introduce a number challenges one of which is maintaining consitency across multiple repositories for configurations that needs be the same accross all of them in your organization.


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
