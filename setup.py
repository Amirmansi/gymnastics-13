from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in gymnastics/__init__.py
from gymnastics import __version__ as version

setup(
	name="gymnastics",
	version=version,
	description="Manage all gym related features",
	author="Bhavesh Maheshwari",
	author_email="maheshwaribhavesh95863@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
