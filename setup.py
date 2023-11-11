import os
import json

from setuptools import find_packages, setup

here = os.path.dirname(__file__)
with open(os.path.join(here, "rlxnix", "info.json"), encoding="utf-8") as infofile:
    infodict = json.load(infofile)


NAME = infodict["NAME"]
VERSION = infodict["VERSION"]
AUTHOR = infodict["AUTHOR"]
CONTACT = infodict["CONTACT"]
DESCRIPTION = infodict["BRIEF"]

classifiers = [
    'Development Status :: 3 - Alpha',
    'License :: OSI Approved :: BSD License',
    'Programming Language :: Python :: 3',
    'Topic :: Scientific/Engineering'
]

README = "README.md"
with open(README) as f:
    description_text = f.read()

install_req = ["numpy", "scipy", "matplotlib", "pandas", "nixio>=1.5",
               "tqdm", "markdown", "mkdocs", "ipython"]

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=CONTACT,
    classifiers=classifiers,
    packages=find_packages(),
    install_requires=install_req,
    package_data={"rlxnix": [
        'utils/default_config.json'], 'rlxnix': ['info.json']},
    include_package_data=True,
    long_description=description_text,
    long_description_content_type="text/markdown",
    license="BSD"
)
