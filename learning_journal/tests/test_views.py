# -*- coding: utf-8 -*-
from learning_journal.views import post_index, view_post
from pyramid.testing import DummyRequest
import os
from bs4 import BeautifulSoup

DATA_SUCCESS = {'username': 'admin', 'password': 'secret'}


def test_post_index(dbtransaction, new_entry):
    test_request = DummyRequest()
    response_dict = post_index(test_request)
    response = response_dict['entries']
    assert response[0] == new_entry


def test_view_post(dbtransaction, new_entry):
    test_request = DummyRequest()
    test_request.matchdict = {'id': new_entry.id}
    response_dict = view_post(test_request)
    assert response_dict['entry'] == new_entry


def test_access(authenticated_app):
    response = authenticated_app.get('/')
    assert response.status_code == 200


def test_add_response(dbtransaction, authenticated_app):
    response = authenticated_app.get('/add')
    assert response.status_code == 200


def test_detail_response(dbtransaction, authenticated_app, new_entry):
    new_entry_id = new_entry.id
    response = authenticated_app.get('/entries/{}'.format(new_entry_id))
    assert response.status_code == 200


def test_edit_response(dbtransaction, authenticated_app, new_entry):
    new_entry_id = new_entry.id
    response = authenticated_app.get('/entries/{}/edit'.format(new_entry_id))
    assert response.status_code == 200


def test_detail_response_html(dbtransaction, authenticated_app, new_entry):
    new_entry_id = new_entry.id
    response = authenticated_app.get('/entries/{}'.format(new_entry_id))
    soup = BeautifulSoup(response.html, 'html.parser')
    anchors = soup.findall('a')
    assert '<li class="tab"><a href="/entries/{{entry.id}}/edit">Edit</a></li>' in anchors


def test_edit_response_html(dbtransaction, authenticated_app, new_entry):
    new_entry_id = new_entry.id
    response = authenticated_app.get('/entries/{}/edit'.format(new_entry_id))
    assert response.status_code == 200


def test_password_exist(app):
    assert os.environ.get('AUTH_PASSWORD', None) is not None


def test_username_exist(app):
    assert os.environ.get('AUTH_USERNAME', None) is not None


def test_check_password_success(auth_env):
    from learning_journal.security import check_password
    password = 'secret'
    assert check_password(password)


def test_stored_password_is_encrypted(auth_env):
    assert os.environ.get('AUTH_PASSWORD', None) != 'secret'


def check_password_fails(auth_env):
    from learning_journal.security import check_password
    password = 'not secret'
    assert not check_password(password)


def test_get_login_view(app):
    response = app.get('/login')
    assert response.status_code == 200


def test_post_login_success(app, auth_env):
    response = app.post('/login', DATA_SUCCESS)
    assert response.status_code == 302


def test_post_login_password_fail(app):
    data = {'username': 'admin', 'password': 'whatever'}
    response = app.post('/login', data)
    assert response.status_code == 200


def test_post_login_redirect(app, auth_env):
    response = app.post('/login', DATA_SUCCESS)
    headers = response.headers
    domain = 'http://localhost'
    actual_path = headers.get('Location', '')[len(domain):]
    assert actual_path == '/'


def test_post_login_auth_tkt_resent(app, auth_env):
    response = app.post('/login', DATA_SUCCESS)
    headers = response.headers
    cookies_set = headers.getall('Set-Cookie')
    assert cookies_set
    for cookie in cookies_set:
        if cookie.startswith('auth_tkt'):
            break
        else:
            assert False
