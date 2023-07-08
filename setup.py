from distutils.core import setup


def get_readme_contents():
    with open("README.md") as rfh:
        return rfh.read().strip()


dev_deps = [
    "black",
    "flake8",
    "ruff",
]

test_deps = [
    "pytest",
]

setup(
    author_email="joseph.bylund@gmail.com",
    author="Joseph Bylund",
    description=" ".join(
        [
            "Provide locks with interface similar to those from threading",
            "and multiprocessing, which are applicable in other situations.",
        ]
    ),
    long_description_content_type="text/markdown",
    long_description=get_readme_contents(),
    maintainer_email="joseph.bylund@gmail.com",
    maintainer="Joseph Bylund",
    install_requires=[
        "boto3>=1.10.23",
        "redis>=3.3.11",
    ],
    extras_require={
        "all": dev_deps + test_deps,
        "dev": dev_deps,
        "test": test_deps,
    },
    name="locking",
    packages=[
        "locking",
        "locking.dynamolock",
        "locking.filelock",
        "locking.redislock",
        "locking.socketlock",
    ],
    url="https://github.com/jbylund/locking",
    version="1.1.5",
)
