import json
import re
import socket
from typing import Optional
from urllib.parse import urlparse


import requests as r
from requests.exceptions import ConnectionError, InvalidSchema

from icarus.checks.core import (get_value_from_env, get_values_from_env,
                                is_check_enabled, save_to_file)

import urllib3

urllib3.disable_warnings()


class HTTPException(Exception):
    pass


class HostParseException(Exception):
    pass


class HostResolveException(Exception):
    pass


class URLExtractError(Exception):
    pass


class RepoChecker:
    def __init__(self, initrc_path: str, repo_pattern=None) -> None:
        if not repo_pattern:
            repo_pattern = r'REPO[0-9]'
        self.initrc = initrc_path
        self.repo_pattern = repo_pattern
        self.repos = get_values_from_env(
            self.initrc,
            pattern=self.repo_pattern).values()
        self.APTKEY = get_value_from_env('APIKEY0', self.initrc)

    def run(self, as_json=False):
        self.last_check = self._check_repository()
        if as_json:
            import json
            return json.dumps(self.last_check, indent=4)

        return self.last_check

    def _check_repository(self, repo_list: Optional[list] = None) -> dict:
        if not repo_list:
            repo_list = self.repos
        return {repo: self._check_req(repo) for repo in repo_list}

    @classmethod
    def _check_req(cls, raw_url: str) -> str:
        try:
            url = cls._extract_url(raw_url)
            cls._check_hostname(url)
            response = r.get(url=url, timeout=1.0)
            code = response.status_code
            # if code == HTTPStatus.FORBIDDEN:
            #     return self._check_signed_repo(url)
            return f'ok, {code}' if code // 100 == 2 else f'error, {code}'
        except URLExtractError as err:
            return f'error: {raw_url}: {err}'
        except HostResolveException as err:
            return f'error: {err}'
        except ConnectionError as err:
            return f'unable to connect to {err.args[0].pool.host}'
        except InvalidSchema as err:
            return f'unable to set a connection with {cls._get_hostname(raw_url)}'
        except Exception as err:
            raise HTTPException(f'unknown error: {err}') from err

    @staticmethod
    def _get_hostname(url: str) -> str:
        try:
            hostname = urlparse(url)[1]
            return hostname
        except Exception as err:
            raise HostParseException(f'unable to parse {url}')

    @staticmethod
    def _extract_url(string):
        try:
            return re.compile(r'http\S+').search(string).group()
        except Exception as e:
            raise URLExtractError(f'unable to fetch url from {string}') from e

    @classmethod
    def _check_hostname(cls, url: str) -> str:
        try:
            host = cls._get_hostname(url)
            return socket.gethostbyname(host)
        except socket.gaierror as err:
            raise HostResolveException(f'unable to resolve {url}') from err

    def _check_signed_repo(self, url: str) -> str:
        pass


@is_check_enabled(check_name='check_repo')
def main_check_repo(conf, check_name, *args, **kwargs) -> None:
    repo_pattern = conf.get_regexp('repo_pattern', r'REPO[0-9]?')
    result = {initrc: RepoChecker(
        initrc, repo_pattern=repo_pattern).run() for initrc in conf.initrc_list}
    save_to_file(check_name=check_name, content=json.dumps(result, indent=4))


if __name__ == '__main__':
    json.dumps(main_check_repo(), indent=4)
