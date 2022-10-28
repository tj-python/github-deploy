def get_repo(*, org, project):
    return "{org}/{project}".format(project=project, org=org)


def can_upload(*, repo, include_private):
    return (
        True
        if include_private and repo["private"] is True
        else not repo["private"]
    )


def get_headers(*, token):
    return {
        "Authorization": "Bearer {token}".format(token=token),
        "Accept": "application/vnd.github+json",
    }
