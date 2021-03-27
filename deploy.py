import asyncio
import base64
import ssl
from hashlib import md5

import aiofiles
import aiohttp
import asyncclick as click
import certifi

from utils import get_repo

REPOS_URL = "https://api.github.com/search/repositories?q=org:{org}"
BASE_URL = "https://api.github.com/repos/{repo}/contents/{path}"


async def get(*, session, url, headers=None):
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    
    async with session.get(
        url,
        headers=headers,
        timeout=70,
        ssl_context=ssl_context,
        raise_for_status=True,
    ) as response:
        if response.status >= 300:
            raise ValueError('{}'.format(response.body))
        
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
        if response.status >= 300:
            raise ValueError('{}'.format(response.body))
        
        value = await response.json()
        return value


async def upload_content(*, session, repo, source, dest, token, semaphore, exists):
    headers = {
        "Authorization": "token {token}".format(token=token),
        "Accept": "application/vnd.github.v3+json"
    }
    
    async with semaphore:
        async with aiofiles.open(source, mode='rb') as f:
            output = await f.read()
            sha = md5(output).hexdigest()
            base64_content = base64.b64encode(output).decode("ascii")
    
    data = {
        "message": "Updated {}".format(dest) if exists else "Added {}".format(dest),
        "content": base64_content,
        "sha": sha,
    }
    url = BASE_URL.format(repo=repo, path=dest)
    
    async with semaphore:
        print(data)
        response = await put(session=session, url=url, data=data, headers=headers)
    
    return response


async def check_exists(*, session, repo, dest, token, semaphore):
    headers = {
        "Authorization": "token {token}".format(token=token)
    }
    url = BASE_URL.format(repo=repo, path=dest)
    
    async with semaphore:
        response = await get(session=session, url=url, headers=headers)
    
    return response


async def handle_file_upload(*, repo, source, dest, overwrite, token, semaphore, session):
    exists = False
    
    if not overwrite:
        response = await check_exists(session=session, repo=repo, dest=dest, token=token, semaphore=semaphore)
        exists = response is not None
        
        if exists:
            return "Config already exists at {}".format(response)
    
    response = await upload_content(
        session=session,
        repo=repo,
        source=source,
        dest=dest,
        token=token,
        semaphore=semaphore,
        exists=exists,
    )
    
    return "Successfully uploaded: {path} to {repo}: {response}".format(path=dest, repo=repo, response=response)


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
        repos = [get_repo(org=org, project=v['name']) for v in response['items']]
        
        click.echo(click.style("Found '{}' repositories".format(len(repos)), fg='green'))
        
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
                (
                    'Error uploading {source} to {repo}/{dest}: {error}'
                    .format(source=source, repo=repo, dest=dest, error=result)
                ),
                err=True,
            )
        else:
            click.echo(result)


if __name__ == '__main__':
    main(_anyio_backend="asyncio")
