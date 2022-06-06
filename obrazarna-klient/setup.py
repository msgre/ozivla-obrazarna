import os

from setuptools import find_packages, setup


with open("requirements.txt") as f:
    install_requires = [line for line in f if line and line[0] not in "#-"]


setup(
    name="obrazarna_klient",
    author="Michal Valoušek",
    author_email="michal@plovarna.cz",
    version=os.getenv("PACKAGE_VERSION") or "dev",
    url="https://github.com/msgre/ozivla-obrazarna",
    packages=find_packages(),
    install_requires=install_requires,
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Operating System :: Raspberry Pi OS",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
    ],
)
