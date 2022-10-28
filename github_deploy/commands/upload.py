import asyncio

import aiohttp
import asyncclick as click

from github_deploy.commands._repo_utils import list_repos, check_exists, upload_content
from github_deploy.commands._utils import get_repo, can_upload


async def handle_file_upload(
    *, repo, source, dest, overwrite, token, semaphore, session
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
    current_content = check_exists_response.get("content")
    exists = current_sha is not None

    if exists and not overwrite:
        return click.style(
            "Skipped uploading {source} to {repo}/{path}: Found an existing copy.".format(
                source=source,
                repo=repo,
                path=dest,
            ),
            fg="blue",
            bold=True,
        )

    else:
        if exists:
            click.echo(
                click.style(
                    "Found an existing copy at {repo}/{path} overwriting it's contents...".format(
                        repo=repo, path=dest
                    ),
                    fg="blue",
                ),
            )

        upload_response = await upload_content(
            session=session,
            repo=repo,
            source=source,
            dest=dest,
            token=token,
            semaphore=semaphore,
            exists=exists,
            current_sha=current_sha,
            current_content=current_content,
        )

        if upload_response:
            return click.style(
                "Successfully uploaded '{source}' to {repo}/{dest}".format(
                    source=upload_response["content"]["name"],
                    repo=repo,
                    dest=upload_response["content"]["path"],
                ),
                fg="green",
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
    "--source",
    prompt=click.style("Enter path to source file", fg="blue"),
    help="Source file.",
    type=click.Path(exists=True),
)
@click.option(
    "--dest",
    prompt=click.style("Where should we upload this file", fg="blue"),
    help="Destination path.",
)
@click.option(
    "--overwrite/--no-overwrite",
    prompt=click.style(
        "Should we overwrite existing contents at this path", fg="blue"
    ),
    help="Overwrite existing files.",
    default=False,
)
@click.option(
    "--private/--no-private",
    prompt=click.style("Should we Include private repositories", bold=True),
    help="Upload files to private repositories.",
    default=True,
)
async def main(org, token, source, dest, overwrite, private):
    """Upload a file to all repositories owned by an organization/user."""
    # create instance of Semaphore: max concurrent requests.
    semaphore = asyncio.Semaphore(1000)

    tasks = []

    async with aiohttp.ClientSession() as session:
        response = await list_repos(org=org, token=token, session=session)
        repos = [
            get_repo(org=org, project=r["name"])
            for r in response["items"]
            if not r["archived"]
            and can_upload(repo=r, include_private=private)
        ]
        repo_type = "public and private" if private else "public"
        click.echo(
            click.style(
                "Found '{}' repositories non archived {} repositories:".format(
                    len(repos), repo_type
                ),
                fg="green",
            )
        )
        click.echo("\n".join(repos))

        if source not in dest:
            click.echo(
                click.style(
                    "The source file {} doesn't match the destination {}".format(
                        source, dest
                    ),
                    fg="bright_red",
                )
            )
        deploy_msg = (
            'Deploying "{source}" to "{path}" for all repositories'.format(
                source=source, path=dest
            )
            if overwrite
            else 'Deploying "{source}" to repositories that don\'t already have contents at "{path}"'.format(
                source=source, path=dest
            )
        )
        click.echo(click.style(deploy_msg, fg="blue"))
        c = click.prompt(click.style("Continue? [YN] ", fg="blue"))

        if c.lower() == "y":
            click.echo(click.style("Uploading...", blink=True, fg="green"))
        elif c.lower() == "n":
            click.echo("Abort!")
            return
        else:
            click.echo("Invalid input :(")
            return

        for repo in repos:
            task = asyncio.ensure_future(
                handle_file_upload(
                    repo=repo,
                    source=source,
                    dest=dest,
                    token=token,
                    overwrite=overwrite,
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
                    "Error uploading {source} to {repo}/{dest}: {error}".format(
                        source=source, repo=repo, dest=dest, error=result
                    ),
                    fg="red",
                ),
                err=True,
            )
        else:
            click.echo(result)


if __name__ == "__main__":
    main(_anyio_backend="asyncio")
