from flask_backend import create_app

app = create_app("development")


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=4000,
        debug=True,
        use_debugger=False,
        use_reloader=False,
        passthrough_errors=True,
    )


# POSTGRES_DATABASE_URI = os.environ.get('POSTGRES_DATABASE_URI')
# HACKER_NEWS_DATABASE_URI = os.environ.get('HACKER_NEWS_DATABASE_URI')
# TEST_HACKER_NEWS_DATABASE_URI = os.environ.get('TEST_HACKER_NEWS_DATABASE_URI')
# FLASK_BACKEND_DATABASE_URI = os.environ.get('FLASK_BACKEND_DATABASE_URI')
# TEST_FLASK_BACKEND_DATABASE_URI = os.environ.get('TEST_FLASK_BACKEND_DATABASE_URI')

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
# config = context.config

###
# db_credentials = config.config_ini_section
# config.set_section_option("POSTGRES_DATABASE_URI", "sqlalchemy.url", os.environ.get('POSTGRES_DATABASE_URI'))
# config.set_section_option("HACKER_NEWS_DATABASE_URI", "sqlalchemy.url", os.environ.get('HACKER_NEWS_DATABASE_URI'))
# config.set_section_option("TEST_HACKER_NEWS_DATABASE_URI", "sqlalchemy.url", os.environ.get('TEST_HACKER_NEWS_DATABASE_URI'))
# config.set_section_option("FLASK_BACKEND_DATABASE_URI", "sqlalchemy.url", os.environ.get('FLASK_BACKEND_DATABASE_URI'))
# config.set_section_option("TEST_FLASK_BACKEND_DATABASE_URI", "sqlalchemy.url", os.environ.get('TEST_FLASK_BACKEND_DATABASE_URI'))
