def get_repo(*, org, project):
    return f"{org}/{project}"


def can_upload(*, repo, include_private):
    return (
        True
        if include_private and repo["private"] is True
        else not repo["private"]
    )


def get_headers(*, token):
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }
