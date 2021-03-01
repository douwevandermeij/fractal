from setuptools import find_packages, setup

REQUIREMENTS = ()
TEST_REQUIREMENTS = (
    "black",
    "flake8",
    "isort",
)


setup(
    name="fractal",
    version="0.0.1",
    author="Douwe van der Meij",
    author_email="douwe@karibu-online.nl",
    description="""Fractal is a scaffolding toolkit for building SOLID logic for your Python applications.
    """,
    long_description=open("README.md", "rt").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/douwevandermeij/fractal",
    packages=find_packages(),
    include_package_data=True,
    install_requires=REQUIREMENTS,
    tests_require=TEST_REQUIREMENTS,
    zip_safe=False,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python",
    ],
)
