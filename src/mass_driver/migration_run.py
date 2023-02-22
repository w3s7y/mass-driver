"""Principal launchpoint for Mass-Driver"""

from copy import deepcopy
from pathlib import Path
from tempfile import mkdtemp

from mass_driver.models.migration import MigrationLoaded
from mass_driver.models.patchdriver import PatchOutcome, PatchResult
from mass_driver.repo import clone_if_remote, commit

DEFAULT_CACHE = Path(".mass_driver/repos/")


def main(
    migration: MigrationLoaded,
    repo_paths: list[str],
    cache: bool,
):
    """Run the program's main command"""
    repo_count = len(repo_paths)
    cache_folder = DEFAULT_CACHE
    if not cache:
        cache_folder = Path(mkdtemp(suffix=".cache"))
        print(f"Using repo cache folder: {cache_folder}/ (Won't wipe it on exit!)")
    print(f"Processing {repo_count} with {migration.driver=}")
    patch_results = {}
    for repo_index, repo_path in enumerate(repo_paths, start=1):
        try:
            print(f"[{repo_index:03d}/{repo_count:03d}] Processing {repo_path}...")
            # Ensure no driver persistence between repos
            migration_copy = deepcopy(migration)
            result = process_repo(repo_path, migration_copy, cache_path=cache_folder)
            patch_results[repo_path] = result
        except Exception as e:
            print(f"Error processing repo '{repo_path}'\nError was: {e}")
            patch_results[repo_path] = PatchResult(
                outcome=PatchOutcome.PATCH_ERROR,
                details=f"Unhandled exception caught during patching. Error was: {e}",
            )
            continue
    print("Action completed: exiting")
    return patch_results


def process_repo(
    repo_path: str,
    migration: MigrationLoaded,
    cache_path: Path,
) -> PatchResult:
    """Process a repo with Mass Driver"""
    repo = clone_if_remote(repo_path, cache_path)
    repo_as_path = Path(repo.working_dir)
    result = migration.driver.run(repo_as_path)
    print(result.outcome.value)
    if result.outcome != PatchOutcome.PATCHED_OK:
        print("Patch wasn't OK: skip commit")
        return result
    # Not a dry run: save the mutation
    print("Done patching, committing")
    commit(repo, migration)
    print("Done committing")
    return result
