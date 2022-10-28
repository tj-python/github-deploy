import os
from setuptools import setup, find_packages

BASE_DIR = os.path.dirname(__file__)
README_PATH = os.path.join(BASE_DIR, "README.md")
LONG_DESCRIPTION_TYPE = "text/markdown"

if os.path.isfile(README_PATH):
    with open(README_PATH, encoding="utf-8") as f:
        LONG_DESCRIPTION = f.read()
else:
    LONG_DESCRIPTION = ""

deploy_requires = [
    "bump2version",
    "readme_renderer[md]",
]

extras_require = {
    "deploy": deploy_requires,
}


setup(
    name="github-deploy",
    version="1.0.2",
    description="Deploy yaml files to a large number of repositories in seconds.",
    long_description=LONG_DESCRIPTION,
    long_description_content_type=LONG_DESCRIPTION_TYPE,
    url="https://github.com/tj-python/github-deploy",
    entry_points={
        "console_scripts": [
            "github-deploy=github_deploy.main:main",
            "gh-deploy=github_deploy.main:main",
        ],
    },
    keywords=[
        "yaml",
        "deploy",
        "poly repository",
        "github",
        "single configuration",
    ],
    author="Tonye Jack",
    author_email="jtonye@ymail.com",
    license="MIT",
    packages=find_packages(),
    python_requires=">=3.7",
    extras_require=extras_require,
    install_requires=[
        "asyncclick",
        "asyncio",
        "aiohttp",
        "certifi",
        "colorama",
        "aiofiles",
        "anyio",
    ],
)
