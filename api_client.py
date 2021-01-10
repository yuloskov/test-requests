"""
A module for making simple requests.
It supports requests for authentication, getting and updating user data.
The module is written in accordance with the given API.

Usage:
    python3 api_client.py
"""

import asyncio
from urllib.parse import urljoin
from aiohttp import ClientSession


class ApiClient:
    def __init__(self, session, host='http://testapi.ru', port='80'):
        """
        Initialize the ApiClient object.

        :param session: current aiohttp session.
        :param host: string with the server's scheme and host.
        :param port: string with the port number.
        """

        # NOTE: HTTPS should be used for passing sensitive data
        self._base_url = f'{host}:{port}'
        self._session = session

    async def auth(self, login: str, password: str) -> dict:
        """
        Make auth request to the server.

        :param login: login for auth.
        :param password: password for auth.

        :return: dict response with auth token.
        """

        auth_url = urljoin(self._base_url, 'auth')
        params = {'login': login, 'pass': password}

        # Passing sensitive data in the query string is not a good idea
        # https://blog.httpwatch.com/2009/02/20/how-secure-are-query-strings-over-https/
        # For better security POST request should be used
        async with self._session.get(auth_url, params=params) as resp:
            assert resp.status == 200
            return await resp.json()

    async def get_user(self, username: str, token: str) -> dict:
        """
        Make a get request to the server.

        :param username: username of the user to get the data.
        :param token: auth token.

        :return: dict response with user data from the server.
        """

        path = f'get-user/{username}'
        get_user_url = urljoin(self._base_url, path)
        params = {'token': token}
        async with self._session.get(get_user_url, params=params) as resp:
            assert resp.status == 200
            return await resp.json()

    async def update_user(self, user_id: str, token: str, **data) -> dict:
        """
        Make a post request to the server to update user data.

        :param user_id: id of the user to update data.
        :param token: auth token.
        :param data: data to be updated. According to the current API,
            data can include:
            active: str,
            blocked: bool,
            name: str,
            permissions: list of dicts.

        :return: dict response from the server.
        """

        path = f'user/{user_id}/update'
        update_user_url = urljoin(self._base_url, path)
        params = {'token': token}
        async with self._session.post(
                update_user_url,
                params=params,
                json=data,
        ) as resp:
            assert resp.status == 200
            return await resp.json()


def is_status_ok(response: dict) -> bool:
    """
    Check if the response of the server is correct.

    :param response: dict response from the server.
    :return: True if status is ok, False otherwise.
    """

    if 'status' not in response:
        return False

    if (status := response['status']) == 'OK':
        return True

    print(f'Request failed with status: {status}')
    return False


async def main():
    """
    Make requests according to the legend.

    First, authorize to the server.
    Second, get user data.
    Third, update user data.
    """

    # Create ClientSession
    async with ClientSession() as session:
        client = ApiClient(session)

        # Log in to the system
        response = await client.auth('test', '12345')
        if not is_status_ok(response):
            raise Exception('Authentication failed')
        auth_token = response['token']

        # Get user data
        response = await client.get_user('ivanov', auth_token)
        if not is_status_ok(response):
            raise Exception('Unable to receive user data')
        user_id = response['id']

        # Update user data
        response = await client.update_user(
            user_id,
            auth_token,
            active='1',
            blocked=True,
            name='Petr Petrovich',
            permissions=[
                {
                    'id': 1,
                    'permission': 'comment',
                },
            ],
        )
        if not is_status_ok(response):
            raise Exception('Unable to update user data')


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
