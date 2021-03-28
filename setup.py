from setuptools import setup, find_packages


setup(
    name="github-deploy",
    version="0.0.1",
    description="Deploy yaml files to a large number of repositories in seconds.",
    url="https://github.com/tj-python/github-deploy",
    entry_points={"console_scripts": ["github-deploy=deploy:main"]},
    keywords=["yaml", "deploy", "poly repository"],
    author="Tonye Jack",
    author_email="jtonye@ymail.com",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "asyncclick",
        "asyncio",
        "aiohttp",
        "certifi",
        "colorama",
        "aiofiles",
    ],
)
