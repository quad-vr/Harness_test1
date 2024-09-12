# this file is *not* meant to cover or endorse the use of nox or pytest or
# testing in general,
#
#  It's meant to show the use of:
#
#  - check-manifest
#     confirm items checked into vcs are in your sdist
#  - readme_renderer (when using a reStructuredText README)
#     confirms your long_description will render correctly on PyPI.
#
#  and also to help confirm pull requests to this project.

import nox
import os

# Define the minimal nox version required to run
nox.options.needs_version = ">= 2024.3.2"

# Nox sessions
nox.options.sessions = ["lint", "tests"]

@nox.session
def lint(session):
    session.install("flake8")
    session.run(
        "flake8", "--exclude", ".nox,*.egg,build,data",
        "--select", "E,W,F", "."
    )

@nox.session
def build_and_check_dists(session):
    session.install("build", "check-manifest >= 0.42", "twine")
    
    # If your project uses README.rst, uncomment the following:
    # session.install("readme_renderer")

    # Check the manifest
    session.run("check-manifest", "--ignore", "noxfile.py,tests/**")

    # Build the package
    session.run("python", "-m", "build")

    # Check if the distribution files are valid
    session.run("python", "-m", "twine", "check", "dist/*")

@nox.session(python=["3.8", "3.9", "3.10", "3.11", "3.12"])
def tests(session):
    # Install pytest and any other dependencies
    session.install("pytest")

    # Notify Nox to run build_and_check_dists session before running tests
    session.notify("build_and_check_dists")

    # Get the list of files in the dist/ directory
    generated_files = os.listdir("dist/")
    
    # Filter the list for sdist files (.tar.gz or .zip)
    sdist_files = [f for f in generated_files if f.endswith(".tar.gz") or f.endswith(".zip")]

    # Ensure we found a valid sdist file
    if len(sdist_files) == 0:
        session.error("No sdist found in dist/ directory")
    else:
        generated_sdist = os.path.join("dist/", sdist_files[0])
        session.install(generated_sdist)

    # Run the tests with pytest
    session.run("pytest", "tests/", *session.posargs)
