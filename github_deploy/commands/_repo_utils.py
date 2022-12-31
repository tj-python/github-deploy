import base64
import os

import aiofiles
import asyncclick as click
from aiofiles import os as aiofiles_os

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
        async with aiofiles.open(source, mode="rb") as f:
            output = await f.read()
            base64_content = base64.b64encode(output).decode("ascii")

    if current_content == base64_content:
        click.echo("Skipping: Contents are the same.")
        return
    else:
        if exists:
            click.echo("Storing backup of existing file...")

            dirname, filename = os.path.split(f"{repo}/{dest}")

            await aiofiles_os.makedirs(dirname, exist_ok=True)

            async with aiofiles.open(f"{dirname}/{filename}", mode="wb") as f:
                await f.write(base64.b64decode(current_content))
        elif only_update:
            click.echo(f"Skipping: only updating existing files.")
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

    click.echo(f"Uploading {source} to {repo}/{dest}...")

    async with semaphore:
        response = await put(
            session=session, url=url, data=data, headers=get_headers(token=token)
        )

    return response
