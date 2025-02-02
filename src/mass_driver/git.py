"""Manipulating git repos natively, without much knowledge of mass-driver models"""

import logging
from pathlib import Path
from git import Repo as GitRepo

from mass_driver.models.migration import MigrationLoaded


def build_clone_target(repo_path: str) -> str:
    """
    Resolves the repos clone URL into something we can write locally (a filesystem path)

    Args:
        repo_path: The clone URL

    Returns:
        clone_target
    """
    if repo_path.startswith("https://"):
        proto_cut = repo_path.split("https://")[1]
        minus_host = proto_cut.split("/")[1:]
    elif repo_path.startswith("git@"):
        proto_cut = repo_path.split("git@")[1]
        minus_host = proto_cut.split(":")[1:]
    else:
        org = "local"
        repo_name = Path(repo_path).name
        return f".mass_driver/{org}/{repo_name}"

    repo_name = minus_host[len(minus_host)-1]
    minus_host.remove(repo_name)
    org = ""
    for p in minus_host:
        org = org + p + "/"

    return f".mass_driver/{org}{repo_name}"


def clone_if_remote(repo_path: str, logger: logging.Logger) -> GitRepo:
    """Build a GitRepo; If repo_path isn't a directory, clone it"""
    if Path(repo_path).is_dir():
        logger.info("Given an existing (local) repo: no cloning")
        # Clone it into cache anyway
        return GitRepo(path=repo_path)  # TODO: Actually clone-move the repo on the way.

    clone_target = build_clone_target(repo_path)
    split_target = clone_target.split("/")
    repo_name = split_target[len(split_target)-1]

    logger.info(f"Using {clone_target} to store repo {repo_name}")

    if clone_target.is_dir():
        logger.info("Given a URL for we cloned already: no cloning")
        return GitRepo(clone_target)
    logger.info("Given a URL, cache miss: cloning")
    cloned = GitRepo.clone_from(
        url=repo_path,
        to_path=clone_target,
        multi_options=["--depth=1"],
    )
    return cloned


def commit(repo: GitRepo, migration: MigrationLoaded):
    """Commit the repo's changes in branch_name, given the PatchDriver that did it"""
    assert repo.is_dirty(
        untracked_files=True
    ), "GitRepo shouldn't be clean on committing"
    branch = repo.create_head(migration.branch_name)
    branch.checkout()
    repo.git.add(A=True)
    author = None  # If stays None, git uses default commit author
    if migration.commit_author_email or migration.commit_author_name:
        name, email = migration.commit_author_name, migration.commit_author_email
        author = f"{name} <{email}>"  # Actor(name=migration.commit_author_name,
        #       email=migration.commit_author_email)
    repo.git.commit(m=migration.commit_message, author=author)


def push(repo: GitRepo, branch_name: str):
    """Push a branch of the repo to a remote"""
    remote = repo.remote()
    remote.push(refspec=branch_name)


def switch_branch_then_pull(repo: GitRepo, pull: bool, branch_name: str | None = None):
    """Switch branch then pull"""
    if branch_name is not None:
        repo.git.checkout(branch_name)
    if pull:
        repo.remote().pull()


def get_default_branch(r: GitRepo) -> str:
    """Get the default branch of a repository"""
    # From https://github.com/gitpython-developers/GitPython/discussions/1364#discussioncomment-1530384
    try:
        return r.remotes.origin.refs.HEAD.ref.remote_head
    except Exception:
        raise ValueError(
            "base_branch param could not be autodetected: no git remote available"
        )
