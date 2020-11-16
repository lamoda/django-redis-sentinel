from setuptools import setup

description = """
Plugin for django-redis that supports Redis Sentinel
"""

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="django-sentinel",
    url="https://github.com/lamoda/django-sentinel",
    author="Aleksey Partilov",
    author_email="aleksey.partilov@lamoda.ru",
    version="0.1.0",
    packages=[
        "django_sentinel",
    ],
    description=description.strip(),
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=[
        "django-redis>=4.7.0",
    ],
    zip_safe=False,
    include_package_data=True,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Operating System :: OS Independent",
        "Environment :: Web Environment",
        "Framework :: Django",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        "Topic :: Software Development :: Libraries",
        "Topic :: Utilities",
    ],
)
