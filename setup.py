from distutils.core import setup
import datetime

def get_readme_contents():
    with open("README.md") as rfh:
        return rfh.read().strip()

setup(
    author_email="joseph.bylund@gmail.com",
    author="Joseph Bylund",
    description=" ".join(
        [
            "Provide locks with interface similar to those from threading",
            " and multiprocessing, which are applicable in other situations.",
        ]
    ),
    long_description_content_type="text/markdown",
    long_description=get_readme_contents(),
    maintainer_email="joseph.bylund@gmail.com",
    maintainer="Joseph Bylund",
    name="locking",
    packages=[
        "locking",
        "locking.dynamolock",
        "locking.filelock",
        "locking.redislock",
        "locking.socketlock",
    ],
    url="https://github.com/jbylund/locking",
    version=f"1.1.4",
)
