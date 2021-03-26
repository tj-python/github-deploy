from setuptools import setup



setup(
  name='counter',
  version='0.0.1',
  description='A Python package for getting list of numbers from 1 to 100',
  url='https://github.com/tj-python/github-yaml-deploy',
  entry_points={'console_scripts': ['counter=deploy:main']},
  keywords=['counter', 'programming language ranking', 'index', 'programming language'],
  author='Tonye Jack',
  author_email='jtonye@ymail.com',
  license='MIT',
  packages=['counter'],
  install_requires=['requests', 'click'],
)
