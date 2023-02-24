"""Tests to validate the Counter driver is valid

Counter is just about the simplest driver we can make, so showcasing it is kinda neat.#


Feature: Validate the Counter Driver
  As the mass-driver dev
  I need to write test harness for a simple PatchDriver
  To template it for downstream plugin-driver developers

Sample config files counter_config1.toml and counter_config2.toml are set up for the
Counter driver with target values 1 and 2 respectively, with counter's in-repo data
being set to 1. This validates both the case for bumping by 1, and the case where
bumping is not needed.

"""

# test-start marker
from pathlib import Path

import pytest

from mass_driver.models.activity import load_activity_toml
from mass_driver.models.patchdriver import PatchOutcome
from mass_driver.tests.fixtures import copy_folder, massdrive


@pytest.mark.parametrize(
    "configfilename,expected_outcome",
    [
        ("config_count1.toml", PatchOutcome.ALREADY_PATCHED),
        ("config_count2.toml", PatchOutcome.PATCHED_OK),
    ],
)
def test_counter_bumped(
    tmp_path, datadir, shared_datadir, configfilename, expected_outcome
):
    """Scenario: Counter file bumped properly"""
    # Given a sample repo to mass-drive
    # And sample repo has counter at value 1
    repo_path = Path(tmp_path / "test_repo/")
    copy_folder(Path(shared_datadir / "sample_repo"), repo_path)
    config_filepath = datadir / configfilename
    activity = load_activity_toml(config_filepath.read_text())
    migration = activity.migration
    # When I run mass-driver
    migration_result, forge_result = massdrive(
        str(repo_path),
        config_filepath,
    )
    assert migration_result.outcome == expected_outcome, "Wrong outcome from patching"
    counter_text_post = (
        repo_path / migration.driver_config["counter_file"]
    ).read_text()
    # Then the counter is bumped to config value
    # Note: Different configfilename set the target_count to different value
    assert (
        int(counter_text_post) == migration.driver_config["target_count"]
    ), "Counter not updated properly"
    # test-end marker


# def test_counter_borked(
#     tmp_path,
#     datadir,
#     shared_datadir,
# ):
#     """Scenario: Counter not an integer crashes"""
#     # Given a sample repo to mass-drive
#     # But counter is not digits
#     repo_path = Path(tmp_path / "test_repo/")
#     copy_folder(Path(shared_datadir / "sample_repo"), repo_path)
#     config_fullpath = datadir / "counter_config2.toml"
#     migration = MigrationLoaded.from_config(config_fullpath.read_text())
#     with open(repo_path / migration.driver.counter_file, "w") as counter_fd:
#         counter_fd.write("Hello World! Not an integer!")
#     # When I run mass-driver
#     massdrive(repo_path, config_fullpath)
#     # TODO Then some error handling should occur
