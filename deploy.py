import asyncio
import base64
import ssl

import aiofiles
import aiohttp
import asyncclick as click
import certifi

from utils import get_repo

REPOS_URL = "https://api.github.com/search/repositories?q=org:{org}"
BASE_URL = "https://api.github.com/repos/{repo}/contents/{path}"


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


async def upload_content(*, session, repo, source, dest, token, semaphore, exists, current_sha, current_content):
    headers = {
        "Authorization": "token {token}".format(token=token),
        "Accept": "application/vnd.github.v3+json"
    }
    
    async with semaphore:
        async with aiofiles.open(source, mode='rb') as f:
            output = await f.read()
            base64_content = base64.b64encode(output).decode("ascii")
    
    if current_content == base64_content:
        click.echo("Skipping: Contents are the same.")
        return
    
    data = {
        "message": "Updated {}".format(dest) if exists else "Added {}".format(dest),
        "content": base64_content,
    }
    if exists:
        data['sha'] = current_sha
    
    url = BASE_URL.format(repo=repo, path=dest)
    
    async with semaphore:
        response = await put(session=session, url=url, data=data, headers=headers)
    
    return response


async def check_exists(*, session, repo, dest, token, semaphore, skip_missing):
    headers = {
        "Authorization": "token {token}".format(token=token)
    }
    url = BASE_URL.format(repo=repo, path=dest)
    
    async with semaphore:
        response = await get(session=session, url=url, headers=headers, skip_missing=skip_missing)
    
    return response


async def handle_file_upload(*, repo, source, dest, overwrite, token, semaphore, session):
    check_exists_response = await check_exists(
        session=session,
        repo=repo,
        dest=dest,
        token=token,
        semaphore=semaphore,
        skip_missing=True,
    )

    current_sha = check_exists_response.get('sha')
    current_content = check_exists_response.get('content')
    exists = current_sha is not None

    if exists and not overwrite:
        return "Skipped uploading {source} to {repo}: Found an existing copy.".format(source=source, repo=repo)

    else:
        if exists:
            click.echo(
                click.style(
                    "Found an existing copy at {repo}/{path} overwriting it's contents...".format(repo=repo, path=dest),
                    fg='blue'
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
            return (
                "Successfully uploaded '{source}' to {repo}/{dest}"
                .format(
                    source=upload_response['content']['name'],
                    repo=repo,
                    dest=upload_response['content']['path'],
                )
            )


async def list_repos(*, session, org, token):
    headers = {
        "Authorization": "token {token}".format(token=token),
        "Accept": "application/vnd.github.v3+json"
    }
    url = REPOS_URL.format(org=org)
    click.echo("Retrieving repos at {}".format(url))
    response = await get(session=session, url=url, headers=headers)
    return response


@click.command()
@click.option('--org', prompt='Your github organization', help='The github organization.')
@click.option(
    '--token',
    prompt='Enter your personal access token',
    help='Personal Access token with read and write access to org.',
    hide_input=True,
)
@click.option('--dest', prompt='Where should we upload this file', help='Destination.')
@click.option('--overwrite/--no-overwrite', help='Overwrite existing files.', default=True)
async def main(org, token, dest, overwrite):
    """Token deployment command."""
    # create instance of Semaphore: max concurent requests.
    semaphore = asyncio.Semaphore(1000)
    
    tasks = []
    
    async with aiohttp.ClientSession() as session:
        response = await list_repos(org=org, token=token, session=session)
        repos = [get_repo(org=org, project=v['name']) for v in response['items'] if not v["archived"]]

        click.echo(click.style("Found '{}' repositories non archived repositories".format(len(repos)), fg='green'))

        source = click.prompt(
            click.style("Enter path to source file", fg='blue'),
            type=click.Path(exists=True)
        )
        
        click.echo(click.style("Deploying \"{path}\" to all repositories:".format(path=dest), fg='blue'))
        click.echo("\n".join(repos))
        
        c = click.prompt(click.style('Continue? [Yn] ', fg='blue'))
        
        if c.lower() == 'y':
            click.echo(click.style("Uploading...", blink=True, fg='green'))
        elif c.lower() == 'n':
            click.echo('Abort!')
            return
        else:
            click.echo('Invalid input :(')
            return
        
        for repo in repos:
            click.echo("Uploading {path} to repository {repo}...".format(path=dest, repo=repo))
            
            task = asyncio.ensure_future(
                handle_file_upload(
                    repo=repo,
                    source=source,
                    dest=dest,
                    token=token,
                    overwrite=overwrite,
                    session=session,
                    semaphore=semaphore
                )
            )
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
    
    for repo, result in zip(repos, responses):
        if isinstance(result, (ValueError, Exception)):
            click.echo(
                click.style(
                    'Error uploading {source} to {repo}/{dest}: {error}'
                    .format(source=source, repo=repo, dest=dest, error=result),
                    fg='red',
                ),
                err=True,
            )
        else:
            click.echo(result)


if __name__ == '__main__':
    main(_anyio_backend="asyncio")
