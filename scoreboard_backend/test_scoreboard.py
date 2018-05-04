from __future__ import print_function
import hashlib
import time

import pytest
import requests

from const import TIMESTAMP_MAX_DELTA


BASE_URL = {
    'dev': 'https://bv30jcdr5b.execute-api.us-east-2.amazonaws.com/dev'}
PATHS = {'token': 'token', 'user_confirm': 'user_confirm/{id}',
         'user_register': 'user_register'}

SUCCESS_EMAIL = 'a{}@a.co'.format(int(time.time()))


def assert_failure(response, message):
    assert response.status_code == 422
    data = response.json()
    assert set(data.keys()) == {'message', 'success'}
    assert not data['success']
    assert data['message'] == message


def compute_nonce(message, prefix):
    nonce = -1
    sha = ''
    timestamp = int(time.time())
    while not sha.startswith(prefix):
        nonce += 1
        sha = hashlib.sha256('{}!{}!{}'.format(message, timestamp, nonce)
                             .encode()).hexdigest()
    return nonce, timestamp


@pytest.fixture(params=[None, 1, 'a' * 35, 'a' * 37])
def invalid_confirmation_id(request):
    return request.param


@pytest.fixture(params=[None, 1, '', 'a@a.c', 'aa.com', 'a@acom',
                        '{}@a.c'.format('a' * 317)])
def invalid_email(request):
    return request.param


@pytest.fixture(params=[None, '', '0'])
def invalid_int(request):
    return request.param


@pytest.fixture(params=[None, 1, '', 'a' * 9, 'a' * 73])
def invalid_password(request):
    return request.param


@pytest.fixture(params=[None, 1, '0', '100001'])
def invalid_team_id(request):
    return request.param


@pytest.fixture(params=[None, 1, '', 'a' * 81])
def invalid_team_name(request):
    return request.param


@pytest.fixture(params=[None, '', '0'])
def invalid_timestamp(request):
    return request.param


def request_token(stage):
    email = 'bbzbryce@gmail.com'
    password = 'bbzbryce@gmail.com'

    nonce, timestamp = compute_nonce('{}!{}'.format(email, password), '00c7f')
    response = requests.post(url('token', stage), json={
        'email': email, 'nonce': nonce, 'password': password,
        'timestamp': timestamp})
    assert response.status_code == 200
    data = response.json()
    assert data['success']
    token = data['message']['token']
    assert len(token) == 144
    assert token.count('.') == 2
    return token


@pytest.fixture
def stage():
    return 'dev'


def test_user_confirm_with_incorrect_confirmation_id(stage):
    confirmation_url = url('user_confirm', stage, id='a' * 36)
    response = requests.get(confirmation_url)
    assert_failure(response, 'invalid confirmation or confirmation already '
                   'completed')


def test_user_confirm_with_invalid_confirmation_id(invalid_confirmation_id,
                                                   stage):
    confirmation_url = url('user_confirm', stage, id=invalid_confirmation_id)
    response = requests.get(confirmation_url)
    assert_failure(response, 'invalid id')


#def test_submit(stage):
#    token = request_token(stage)
#    print(token)


def test_token_with_extra_parameter(stage):
    email = 'a@a.co'
    nonce = 0  # Doesn't need to be valid
    password = 'a' * 10
    timestamp = int(time.time())
    response = requests.post(url('token', stage), json={
        'email': email, 'nonce': nonce, 'password': password,
        'timestamp': timestamp, 'x': 1})
    assert_failure(response, 'unexpected x')


def test_token_with_expired_timestamp(stage):
    email = 'a@a.co'
    nonce = 0  # Doesn't need to be valid
    password = 'a' * 10
    response = requests.post(url('token', stage), json={
        'email': email, 'nonce': nonce, 'password': password,
        'timestamp': int(time.time()) - TIMESTAMP_MAX_DELTA - 1})
    assert_failure(response, 'timestamp has expired')


def test_token_with_future_timestamp(stage):
    email = 'a@a.co'
    nonce = 0  # Doesn't need to be valid
    password = 'a' * 10
    response = requests.post(url('token', stage), json={
        'email': email, 'nonce': nonce, 'password': password,
        'timestamp': int(time.time()) + 60})
    assert_failure(response, 'timestamp is too recent')


def test_token_with_incorrect_nonce(stage):
    email = 'a@a.co'
    nonce = 0
    password = 'a' * 10
    timestamp = int(time.time())
    response = requests.post(url('token', stage), json={
        'email': email, 'nonce': nonce, 'password': password,
        'timestamp': timestamp})
    assert_failure(response, 'incorrect nonce')


def test_token_with_invalid_email(invalid_email, stage):
    nonce = 0  # Doesn't need to be valid
    password = 'a' * 10
    timestamp = int(time.time())
    response = requests.post(url('token', stage), json={
        'email': invalid_email, 'nonce': nonce, 'password': password,
        'timestamp': timestamp})
    assert_failure(response, 'invalid email')


def test_token_with_invalid_nonce(invalid_int, stage):
    email = 'a@a.co'
    nonce = invalid_int
    password = 'a' * 10
    timestamp = int(time.time())
    response = requests.post(url('token', stage), json={
        'email': email, 'nonce': nonce, 'password': password,
        'timestamp': timestamp})
    assert_failure(response, 'invalid nonce')


def test_token_with_invalid_password(invalid_password, stage):
    email = 'a@a.co'
    nonce = 0  # Doesn't need to be valid
    timestamp = int(time.time())
    response = requests.post(url('token', stage), json={
        'email': email, 'nonce': nonce, 'password': invalid_password,
        'timestamp': timestamp})
    assert_failure(response, 'invalid password')


def test_token_with_invalid_timestamp(invalid_timestamp, stage):
    email = 'a@a.co'
    nonce = 0  # Doesn't need to be valid
    password = 'a' * 10
    response = requests.post(url('token', stage), json={
        'email': email, 'nonce': nonce, 'password': password,
        'timestamp': invalid_timestamp})
    assert_failure(response, 'invalid timestamp')


@pytest.mark.slow
def test_user_register(stage):
    ctf_time_team_id = '1'
    email = SUCCESS_EMAIL
    password = 'a' * 10
    nonce, timestamp = compute_nonce(email, '000c7f')
    response = requests.post(
        url('user_register', stage), headers={'origin': 'a'}, json={
            'ctf_time_team_id': ctf_time_team_id, 'email': email,
            'nonce': nonce, 'password': password, 'team_name': email,
            'timestamp': timestamp})
    assert response.status_code == 201


@pytest.mark.slow
def test_user_register_fail_with_duplicate_email(stage):
    ctf_time_team_id = '1'
    email = SUCCESS_EMAIL
    password = 'a' * 10
    nonce, timestamp = compute_nonce(email, '000c7f')
    response = requests.post(
        url('user_register', stage), headers={'origin': 'a'}, json={
            'ctf_time_team_id': ctf_time_team_id, 'email': email,
            'nonce': nonce, 'password': password, 'team_name': email + 'm',
            'timestamp': timestamp})
    assert_failure(response, 'duplicate email')


@pytest.mark.slow
def test_user_register_fail_with_duplicate_team_name(stage):
    ctf_time_team_id = '1'
    email = SUCCESS_EMAIL + 'm'
    password = 'a' * 10
    nonce, timestamp = compute_nonce(email, '000c7f')
    team_name = SUCCESS_EMAIL
    response = requests.post(
        url('user_register', stage), headers={'origin': 'a'}, json={
            'ctf_time_team_id': ctf_time_team_id, 'email': email,
            'nonce': nonce, 'password': password, 'team_name': team_name,
            'timestamp': timestamp})
    assert_failure(response, 'duplicate team name')


def test_user_register_with_invalid_ctf_time_team_id(invalid_team_id, stage):
    email = 'a@a.co'
    nonce = 0  # Doesn't need to be valid
    password = 'a' * 10
    team_name = 'A'
    timestamp = int(time.time())
    response = requests.post(
        url('user_register', stage), headers={'origin': 'a'}, json={
            'ctf_time_team_id': invalid_team_id, 'email': email,
            'nonce': nonce, 'password': password, 'team_name': team_name,
            'timestamp': timestamp})
    assert_failure(response, 'invalid ctf_time_team_id')


def test_user_register_with_invalid_email(invalid_email, stage):
    ctf_time_team_id = '1'
    nonce = 0  # Doesn't need to be valid
    password = 'a' * 10
    team_name = 'A'
    timestamp = int(time.time())
    response = requests.post(
        url('user_register', stage), headers={'origin': 'a'}, json={
            'ctf_time_team_id': ctf_time_team_id, 'email': invalid_email,
            'nonce': nonce, 'password': password, 'team_name': team_name,
            'timestamp': timestamp})
    assert_failure(response, 'invalid email')


def test_user_register_with_invalid_nonce(invalid_int, stage):
    ctf_time_team_id = '1'
    email = 'a@a.co'
    password = 'a' * 10
    team_name = 'A'
    timestamp = int(time.time())
    response = requests.post(
        url('user_register', stage), headers={'origin': 'a'}, json={
            'ctf_time_team_id': ctf_time_team_id, 'email': email,
            'nonce': invalid_int, 'password': password,
            'team_name': team_name, 'timestamp': timestamp})
    assert_failure(response, 'invalid nonce')


def test_user_register_with_invalid_password(invalid_password, stage):
    ctf_time_team_id = '1'
    email = 'a@a.co'
    nonce = 0  # Doesn't need to be valid
    team_name = 'A'
    timestamp = int(time.time())
    response = requests.post(
        url('user_register', stage), headers={'origin': 'a'}, json={
            'ctf_time_team_id': ctf_time_team_id, 'email': email,
            'nonce': nonce, 'password': invalid_password, 'team_name':
            team_name, 'timestamp': timestamp})
    assert_failure(response, 'invalid password')


def test_user_register_with_invalid_team_name(invalid_team_name, stage):
    ctf_time_team_id = '1'
    email = 'a@a.co'
    password = 'a' * 10
    nonce = 0  # Doesn't need to be valid
    timestamp = int(time.time())
    response = requests.post(
        url('user_register', stage), headers={'origin': 'a'}, json={
            'ctf_time_team_id': ctf_time_team_id, 'email': email,
            'nonce': nonce, 'password': password,
            'team_name': invalid_team_name, 'timestamp': timestamp})
    assert_failure(response, 'invalid team_name')


def test_user_register_with_invalid_timestamp(invalid_timestamp, stage):
    ctf_time_team_id = '1'
    email = 'a@a.co'
    password = 'a' * 10
    nonce = 0  # Doesn't need to be valid
    team_name = 'A'
    response = requests.post(
        url('user_register', stage), headers={'origin': 'a'}, json={
            'ctf_time_team_id': ctf_time_team_id, 'email': email,
            'nonce': nonce, 'password': password, 'team_name': team_name,
            'timestamp': invalid_timestamp})
    assert_failure(response, 'invalid timestamp')


def test_user_register_with_missing_origin_header(stage):
    ctf_time_team_id = '1'
    email = 'a@a.co'
    password = 'a' * 10
    nonce = 0  # Doesn't need to be valid
    team_name = 'A'
    timestamp = int(time.time())
    response = requests.post(
        url('user_register', stage), headers={'origin': ''}, json={
            'ctf_time_team_id': ctf_time_team_id, 'email': email,
            'nonce': nonce, 'password': password, 'team_name': team_name,
            'timestamp': timestamp})
    assert_failure(response, 'origin header missing')


def url(action, stage, **path_params):
    return '{}/{}'.format(BASE_URL[stage], PATHS[action].format(**path_params))