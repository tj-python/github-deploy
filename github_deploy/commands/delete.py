import asyncio
import ssl

import aiohttp
import asyncclick as click
import certifi

from github_deploy.commands._constants import BASE_URL, REPOS_URL
from github_deploy.commands._utils import get_repo


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
        "Authorization": "token {token}".format(token=token),
        "Accept": "application/vnd.github.v3+json",
    }

    data = {"message": "Deleted {}".format(dest)}
    if exists:
        data["sha"] = current_sha

    url = BASE_URL.format(repo=repo, path=dest)

    async with semaphore:
        response = await delete(session=session, url=url, data=data, headers=headers)

    return response


async def check_exists(*, session, repo, dest, token, semaphore, skip_missing):
    headers = {"Authorization": "token {token}".format(token=token)}
    url = BASE_URL.format(repo=repo, path=dest)

    async with semaphore:
        response = await get(
            session=session, url=url, headers=headers, skip_missing=skip_missing
        )

    return response


async def handle_file_delete(
    *, repo, dest, token, semaphore, session
):
    check_exists_response = await check_exists(
        session=session,
        repo=repo,
        dest=dest,
        token=token,
        semaphore=semaphore,
        skip_missing=True,
    )

    current_sha = check_exists_response.get("sha")
    exists = current_sha is not None

    if exists:
        click.echo(
            click.style(
                "Found an existing copy at {repo}/{path} deleting it's contents...".format(
                    repo=repo, path=dest
                ),
                fg="blue",
            ),
        )

        delete_response = await delete_content(
            session=session,
            repo=repo,
            dest=dest,
            token=token,
            semaphore=semaphore,
            exists=exists,
            current_sha=current_sha,
        )
    
        if delete_response:
            return "Successfully deleted contents at {repo}/{dest}".format(
                repo=repo,
                dest=dest,
            )
    
    return "No content found at {repo}/{dest}".format(repo=repo, dest=dest)


async def list_repos(*, session, org, token):
    headers = {
        "Authorization": "token {token}".format(token=token),
        "Accept": "application/vnd.github.v3+json",
    }
    url = REPOS_URL.format(org=org)
    click.echo("Retrieving repos at {}".format(url))
    response = await get(session=session, url=url, headers=headers)
    return response


@click.command()
@click.option(
    "--org",
    prompt=click.style("Enter your github user/organization", bold=True),
    help="The github organization.",
)
@click.option(
    "--token",
    prompt=click.style("Enter your personal access token", bold=True),
    help="Personal Access token with read and write access to org.",
    hide_input=True,
    envvar='TOKEN',
)
@click.option(
    "--dest",
    prompt=click.style("What path should it's contents be deleted", fg="blue"),
    help="Destination path to delete.",
)
async def main(org, token, dest):
    """Delete a file in all repositories owned by an organization/user."""

    # create instance of Semaphore: max concurrent requests.
    semaphore = asyncio.Semaphore(1000)

    tasks = []

    async with aiohttp.ClientSession() as session:
        response = await list_repos(org=org, token=token, session=session)
        repos = [
            get_repo(org=org, project=v["name"])
            for v in response["items"]
            if not v["archived"]
        ]
        click.echo(
            click.style(
                "Found '{}' repositories non archived repositories".format(len(repos)),
                fg="green",
            )
        )
        click.echo(click.style('Deleting "{path}" for all repositories:'.format(path=dest), fg="blue"))
        click.echo("\n".join(repos))

        c = click.prompt(click.style("Continue? [Yn] ", fg="blue"))

        if c.lower() == "y":
            click.echo(click.style("Deleting...", blink=True, fg="green"))
        elif c.lower() == "n":
            click.echo("Abort!")
            return
        else:
            click.echo("Invalid input :(")
            return

        for repo in repos:
            task = asyncio.ensure_future(
                handle_file_delete(
                    repo=repo,
                    dest=dest,
                    token=token,
                    session=session,
                    semaphore=semaphore,
                )
            )
            tasks.append(task)

        responses = await asyncio.gather(*tasks, return_exceptions=True)

    for repo, result in zip(repos, responses):
        if isinstance(result, (ValueError, Exception)):
            click.echo(
                click.style(
                    "Error deleting contents at {repo}/{dest}: {error}".format(
                        repo=repo, dest=dest, error=result
                    ),
                    fg="red",
                ),
                err=True,
            )
        else:
            click.echo(click.style(result, fg="green", bold=True))


if __name__ == "__main__":
    main(_anyio_backend="asyncio")
