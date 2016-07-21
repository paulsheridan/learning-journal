# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from learning_journal.models import DBSession, Base, Entry
import pytest
import os


TEST_DATABASE = 'postgresql://paulsheridan:@localhost:5432/testdb'
DATA_SUCCESS = {'username': 'admin', 'password': 'secret'}


@pytest.fixture()
def auth_env():
    from learning_journal.security import pwd_context
    os.environ['AUTH_PASSWORD'] = pwd_context.encrypt('secret')
    os.environ['AUTH_USERNAME'] = 'admin'


@pytest.fixture(scope='session')
def sqlengine(request):
    engine = create_engine(TEST_DATABASE)
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)
    auth_env()

    def teardown():
        Base.metadata.drop_all(engine)

    request.addfinalizer(teardown)
    return engine


@pytest.fixture()
def dbtransaction(request, sqlengine):
    connection = sqlengine.connect()
    transaction = connection.begin()
    DBSession.configure(bind=connection)

    def teardown():
        transaction.rollback()
        connection.close()
        DBSession.remove()

    request.addfinalizer(teardown)
    return connection


@pytest.fixture(scope='function')
def new_entry(request):
    new_entry = Entry(title='something', text='whatever')
    DBSession.add(new_entry)
    DBSession.flush()

    def teardown():
        DBSession.query(Entry).filter(Entry.id == new_entry.id).delete()
        DBSession.flush()

    request.addfinalizer(teardown)
    return new_entry


@pytest.fixture()
def app(dbtransaction):
    from webtest import TestApp
    from learning_journal import main
    fake_settings = {'sqlalchemy.url': TEST_DATABASE}
    os.environ['JOURNAL_DB'] = TEST_DATABASE
    app = main({}, **fake_settings)
    return TestApp(app)


@pytest.fixture()
def authenticated_app(app, auth_env):
    # response = app.get('/login')
    # headers = response.headers
    app.post('/login', DATA_SUCCESS, status='3*')
    return app
