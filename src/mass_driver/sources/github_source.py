"""Github repository search as Source"""

from github import AppAuthentication, Github

from mass_driver.models.source import IndexedRepos, Repo, Source


class GithubBaseSource(Source):
    """Base for github source"""

    _github_api: Github
    search_query: str
    """The github repo search query"""

    def discover(self) -> IndexedRepos:
        """Discover a list of repositories"""
        repos = self._github_api.search_repositories(query=self.search_query)
        return {
            repo.full_name: Repo(repo_id=repo.full_name, clone_url=repo.ssh_url)
            for repo in repos
        }


class GithubPersonalSource(GithubBaseSource):
    """Github API wrapper for personal user token use, capable of searching repos

    Reliance on pygithub means only able to deliver personal user token PRs, no
    Github app authentication.
    """

    token: str
    """Github personal access token"""

    def __init__(self, **data):
        """Log in to Github first"""
        super().__init__(**data)
        self._github_api = Github(login_or_token=self.token)


class GithubAppSource(GithubBaseSource):
    """Search repos on Github as a Github App, not user"""

    app_id: str
    app_private_key: str
    app_installation_id: int

    def __init__(self, **data):
        """Log in to Github first"""
        super().__init__(**data)
        auth = AppAuthentication(
            app_id=self.app_id,
            private_key=self.app_private_key,
            installation_id=self.app_installation_id,
        )
        self._github_api = Github(app_auth=auth)
