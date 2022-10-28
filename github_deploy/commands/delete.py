import asyncio

import aiohttp
import asyncclick as click

from github_deploy.commands._repo_utils import list_repos, delete_content, check_exists
from github_deploy.commands._utils import get_repo


async def handle_file_delete(*, repo, dest, token, semaphore, session):
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
            return click.style(
                "Successfully deleted contents at {repo}/{dest}".format(
                    repo=repo,
                    dest=dest,
                ),
                fg="green",
                bold=True,
            )

    return click.style(
        f"No content found at {repo}/{dest}",
        fg="blue",
        bold=True,
    )


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
    envvar="TOKEN",
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
                "Found '{}' repositories non archived repositories".format(
                    len(repos)
                ),
                fg="green",
            )
        )
        click.echo(
            click.style(
                f'Deleting "{dest}" for all repositories:',
                fg="blue",
            )
        )
        click.echo("\n".join(repos))

        c = click.prompt(click.style("Continue? [YN] ", fg="blue"))

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
            click.echo(result)


if __name__ == "__main__":
    main(_anyio_backend="asyncio")
