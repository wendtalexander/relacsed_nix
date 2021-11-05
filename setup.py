from setuptools import find_packages, setup

NAME = "rlxnix"
VERSION = 0.5
AUTHOR = "Jan Grewe"
CONTACT = "jan.grewe@g-node.org"
DESCRIPTION = "Reader for relacs written nix files"

classifiers = [
    'Development Status :: 3 - Alpha',
    'License :: OSI Approved :: BSD License',
    'Programming Language :: Python :: 3',
    'Topic :: Scientific/Engineering'
]

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
    classifiers=classifiers,
    packages=find_packages(),
    install_requires=install_req,
    include_package_data=True,
    long_description=description_text,
    long_description_content_type="text/markdown",
    license="BSD"
)