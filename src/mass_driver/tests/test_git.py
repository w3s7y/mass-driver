from mass_driver import git


def test_github_ssh_url():
    test_str = "git@github.com:w3s7y/mass-driver.git"
    result = git.build_clone_target(test_str)
    assert result == ".mass_driver/w3s7y/mass-driver.git"


def test_github_https_url():
    test_str = "https://github.com/w3s7y/mass-driver.git"
    result = git.build_clone_target(test_str)
    assert result == ".mass_driver/w3s7y/mass-driver.git"


def test_gitlab_ssh_url():
    test_str = "git@gitlab.com:test-grouping1/deeper-group/deep-project.git"
    result = git.build_clone_target(test_str)
    assert result == ".mass_driver/test-grouping1/deeper-group/deep-project.git"


def test_gitlab_https_url():
    test_str = "https://gitlab.com/test-grouping1/deeper-group/deep-project.git"
    result = git.build_clone_target(test_str)
    assert result == ".mass_driver/test-grouping1/deeper-group/deep-project.git"
