import os
from setuptools import setup, find_packages

BASE_DIR = os.path.dirname(__file__)
README_PATH = os.path.join(BASE_DIR, "README.md")
LONG_DESCRIPTION_TYPE = "text/markdown"

if os.path.isfile(README_PATH):
    with io.open(README_PATH, encoding="utf-8") as f:
        LONG_DESCRIPTION = f.read()
else:
    LONG_DESCRIPTION = ""


setup(
    name="github-deploy",
    version="0.0.2",
    description="Deploy yaml files to a large number of repositories in seconds.",
    long_description=LONG_DESCRIPTION,
    long_description_content_type=LONG_DESCRIPTION_TYPE,
    url="https://github.com/tj-python/github-deploy",
    entry_points={
        "console_scripts": [
            "github-deploy=deploy:main",
            "github-delete=delete:main",
        ],
    },
    keywords=["yaml", "deploy", "poly repository", "github", "single configuration"],
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
