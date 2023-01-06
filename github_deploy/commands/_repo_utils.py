import base64
import os

import asyncclick as click
from aiofiles import os as aiofiles_os, open as aiofiles_open

from github_deploy.commands._constants import REPOS_URL, FILE_CONTENTS_URL
from github_deploy.commands._http_utils import get, delete, put
from github_deploy.commands._utils import get_headers


async def list_repos(*, session, org, token):
    url = REPOS_URL.format(org=org)
    click.echo(f"Retrieving repos at {url}")
    response = await get(session=session, url=url, headers=get_headers(token=token))
    return response


async def delete_content(
    *,
    session,
    repo,
    dest,
    token,
    semaphore,
    exists,
    current_sha,
):
    data = {"message": f"Deleted {dest}"}
    if exists:
        data["sha"] = current_sha

    url = FILE_CONTENTS_URL.format(repo=repo, path=dest)

    async with semaphore:
        response = await delete(
            session=session, url=url, data=data, headers=get_headers(token=token)
        )

    return response


async def check_exists(*, session, repo, dest, token, semaphore, skip_missing):
    url = FILE_CONTENTS_URL.format(repo=repo, path=dest)

    async with semaphore:
        response = await get(
            session=session,
            url=url,
            headers=get_headers(token=token),
            skip_missing=skip_missing,
        )

    return response


async def upload_content(
    *,
    session,
    repo,
    source,
    dest,
    token,
    semaphore,
    exists,
    only_update,
    current_sha,
    current_content
):
    async with semaphore:
        async with aiofiles_open(source, mode="rb") as f:
            output = await f.read()
            base64_content = base64.b64encode(output).decode("ascii")

    if current_content == base64_content:
        click.echo(
            click.style(
                f"Skipped uploading {source} to {repo}/{dest}: No changes detected.",
                fg="yellow",
                bold=True,
            )
        )
        return
    else:
        if exists:
            click.echo(
                click.style(
                    "Storing backup of existing file at {repo}/{path}...".format(
                        repo=repo, path=dest
                    ),
                    fg="cyan",
                ),
            )

            dirname, filename = os.path.split(f"{repo}/{dest}")

            await aiofiles_os.makedirs(dirname, exist_ok=True)

            async with aiofiles_open(f"{dirname}/{filename}", mode="wb") as f:
                await f.write(base64.b64decode(current_content))
        elif only_update:
            click.echo(
                click.style(
                    f"Updates only: Skipped uploading {source} to {repo}/{dest}. File does not exist.",
                    fg="yellow",
                    bold=True,
                )
            )
            return

    data = {
        "message": f"Updated {dest}"
        if exists
        else f"Added {dest}",
        "content": base64_content,
    }
    if exists:
        data["sha"] = current_sha

    url = FILE_CONTENTS_URL.format(repo=repo, path=dest)

    click.echo(
        click.style(
            f"Uploading {source} to {repo}/{dest}...",
            fg="green",
            bold=True,
        )
    )

    async with semaphore:
        response = await put(
            session=session, url=url, data=data, headers=get_headers(token=token)
        )

    return response
