import ssl
import certifi

import asyncclick as click

from github_deploy.commands._constants import REPOS_URL


async def get(*, session, url, headers=None, skip_missing=False):
    ssl_context = ssl.create_default_context(cafile=certifi.where())

    async with session.get(
            url,
            headers=headers,
            timeout=70,
            ssl_context=ssl_context,
            raise_for_status=not skip_missing,
    ) as response:
        if skip_missing and response.status == 404:
            return {}

        value = await response.json()
        return value


async def put(*, session, url, data, headers=None):
    ssl_context = ssl.create_default_context(cafile=certifi.where())

    async with session.put(
            url,
            json=data,
            headers=headers,
            timeout=70,
            ssl_context=ssl_context,
            raise_for_status=True,
    ) as response:
        value = await response.json()
        return value


async def delete(*, session, url, data, headers=None):
    ssl_context = ssl.create_default_context(cafile=certifi.where())

    async with session.delete(
            url,
            json=data,
            headers=headers,
            timeout=70,
            ssl_context=ssl_context,
            raise_for_status=True,
    ) as response:
        value = await response.json()
        return value


async def list_repos(*, session, org, token):
    headers = {
        "Authorization": "Bearer {token}".format(token=token),
        "Accept": "application/vnd.github+json",
    }
    url = REPOS_URL.format(org=org)
    click.echo("Retrieving repos at {}".format(url))
    response = await get(session=session, url=url, headers=headers)
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
    headers = {
        "Authorization": "Bearer {token}".format(token=token),
        "Accept": "application/vnd.github+json",
    }

    data = {"message": "Deleted {}".format(dest)}
    if exists:
        data["sha"] = current_sha

    url = BASE_URL.format(repo=repo, path=dest)

    async with semaphore:
        response = await delete(
            session=session, url=url, data=data, headers=headers
        )

    return response


async def check_exists(*, session, repo, dest, token, semaphore, skip_missing):
    headers = {"Authorization": "Bearer {token}".format(token=token)}
    url = BASE_URL.format(repo=repo, path=dest)

    async with semaphore:
        response = await get(
            session=session,
            url=url,
            headers=headers,
            skip_missing=skip_missing,
        )

    return response
