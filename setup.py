from setuptools import find_packages, setup

NAME = "rlxnix"
VERSION = 0.5
AUTHOR = "Jan Grewe"
CONTACT = "jan.grewe@g-node.org"
CLASSIFIERS = "science"
DESCRIPTION = "Reader for relacs written nix files"

README = "README.md"
with open(README) as f:
    description_text = f.read()

install_req = ["nixio>=1.5", "pandas", "matplotlib", "numpy", "tqdm"]
setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=CONTACT,
    packages=find_packages(),
    install_requires=install_req,
    include_package_data=True,
    long_description=description_text,
    long_description_content_type="text/markdown",
    classifiers=CLASSIFIERS,
    license="BSD"
)