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

    session.run("check-manifest", "--ignore", "noxfile.py,tests/**")
    session.run("python", "-m", "build")
    session.run("python", "-m", "twine", "check", "dist/*")


@nox.session(python=["3.8", "3.9", "3.10", "3.11", "3.12"])
def tests(session):
    session.install("pytest")
    
    # Ensure build_and_check_dists is necessary before running tests
    build_and_check_dists(session)

    generated_files = os.listdir("dist/")
    if len(generated_files) > 1:
        generated_sdist = os.path.join("dist/", generated_files[1])
        session.install(generated_sdist)
    else:
        session.error("No sdist found in dist/ directory")

    session.run("pytest", "tests/", *session.posargs)

