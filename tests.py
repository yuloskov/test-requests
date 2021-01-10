"""
Tests for ApiClient queries

Usage:
    pytest tests.py
"""

from api_client import ApiClient
from aiohttp.web_request import Request
from aiohttp import web, test_utils, ClientSession


async def test_auth():
    """
    Test authentication query.
    """

    app = web.Application()

    async def auth(request: Request):
        """
        Function to process auth request.

        :param request: request from ApiClient.
        :return: test json response
        """

        # Check query params
        query = request.rel_url.query
        assert 'login' in query
        assert query['login'] == 'login'

        assert 'pass' in query
        assert query['pass'] == '12345'

        return web.json_response({
            'status': 'OK',
            'token': 'dsfd79843r32d1d3dx23d32d'
        })

    # Register route
    app.router.add_route('get', '/auth', auth)
    # Create server
    server = test_utils.TestServer(app)

    async with server:
        async with ClientSession() as session:
            client = ApiClient(
                session,
                'http://127.0.0.1',
                server.port,
            )
            resp = await client.auth('login', '12345')
            # Check response
            assert 'status' in resp
            assert resp['status'] == 'OK'

            assert 'token' in resp
            assert resp['token'] == 'dsfd79843r32d1d3dx23d32d'


async def test_get_user():
    """
    Test get user query.
    """

    app = web.Application()

    async def get_user(request: Request):
        """
        Function to process get user request.

        :param request: request from ApiClient.
        :return: test json response
        """

        query = request.rel_url.query
        # Check query params
        assert 'token' in query
        assert query['token'] == 'dsfd79843r32d1d3dx23d32d'

        # Check params in the url
        assert request.match_info.get('username') == 'ivanov'

        return web.json_response({
            'status': 'OK',
            'active': '1',
            'blocked': False,
            'created_at': 1587457590,
            'id': 23,
            'name': 'Ivanov Ivan',
            'permissions': [
                {
                    'id': 1,
                    'permission': 'comment'
                },
                {
                    'id': 2,
                    'permission': 'upload photo'
                },
                {
                    'id': 3,
                    'permission': 'add event'
                }
            ]
        })

    # Register route
    app.router.add_route('get', '/get-user/{username}', get_user)
    # Create server
    server = test_utils.TestServer(app)

    async with server:
        async with ClientSession() as session:
            client = ApiClient(
                session,
                'http://127.0.0.1',
                server.port,
            )
            resp = await client.get_user('ivanov', 'dsfd79843r32d1d3dx23d32d')
            # Check response
            assert 'status' in resp
            assert resp['status'] == 'OK'
            assert 'active' in resp
            assert resp['active'] == '1'


async def test_update_user():
    """
    Test update user query.
    """

    app = web.Application()

    async def update_user(request: Request):
        """
        Function to process update user request.

        :param request: request from ApiClient.
        :return: test json response
        """

        query = request.rel_url.query
        # Check query params
        assert 'token' in query
        assert query['token'] == 'dsfd79843r32d1d3dx23d32d'

        # Check params in the url
        assert request.match_info.get('user_id') == '23'

        data = await request.json()
        # Check data payload
        assert 'active' in data
        assert data['active'] == '1'

        assert 'blocked' in data
        assert data['blocked']

        assert 'name' in data
        assert data['name'] == 'Petr Petrovich'

        assert 'permissions' in data
        assert data['permissions'] == [
            {
                'id': 1,
                'permission': 'comment',
            },
        ]

        return web.json_response({
            'status': 'OK',
        })

    # Register route
    app.router.add_route('post', '/user/{user_id}/update', update_user)
    # Create server
    server = test_utils.TestServer(app)

    async with server:
        async with ClientSession() as session:
            client = ApiClient(
                session,
                'http://127.0.0.1',
                server.port,
            )
            resp = await client.update_user(
                user_id='23',
                token='dsfd79843r32d1d3dx23d32d',
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
            # Check response
            assert 'status' in resp
            assert resp['status'] == 'OK'
