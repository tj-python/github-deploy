import base64

import aiofiles
import asyncclick as click

from github_deploy.commands._constants import REPOS_URL, BASE_URL
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

    url = BASE_URL.format(repo=repo, path=dest)

    async with semaphore:
        response = await delete(
            session=session, url=url, data=data, headers=get_headers(token=token)
        )

    return response


async def check_exists(*, session, repo, dest, token, semaphore, skip_missing):
    url = BASE_URL.format(repo=repo, path=dest)

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

    data = {
        "message": f"Updated {dest}"
        if exists
        else f"Added {dest}",
        "content": base64_content,
    }
    if exists:
        data["sha"] = current_sha

    url = BASE_URL.format(repo=repo, path=dest)

    async with semaphore:
        response = await put(
            session=session, url=url, data=data, headers=get_headers(token=token)
        )

    return response
