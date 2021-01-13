import pytest
import os
import tempfile
from twittersupervisor import create_app, Database

TWITTER_USER_ID = 783214


def pytest_addoption(parser):
    parser.addoption("--allow_api_call", action="store_true", default=False, help="Do the tests calling "
                                                                                  "the Twitter API")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--allow_api_call"):
        return
    skip_api_call = pytest.mark.skip(reason="need --allow_api_call option to run")
    for item in items:
        if "api_call" in item.keywords:
            item.add_marker(skip_api_call)


# Fixtures
@pytest.fixture(scope="package")
def app():
    db_fd, db_path = tempfile.mkstemp()

    app = create_app({
        'TESTING': True,
        'DATABASE_FILE': db_path
    })

    with app.app_context():
        # init_db()
        # get_db().executescript(_data_sql)
        db = Database()
        db.create_tables()

    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()
