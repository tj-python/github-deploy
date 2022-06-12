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
        "Authorization": "token {token}".format(token=token),
        "Accept": "application/vnd.github.v3+json",
    }
    url = REPOS_URL.format(org=org)
    click.echo("Retrieving repos at {}".format(url))
    response = await get(session=session, url=url, headers=headers)
    return response
