# flask_backend
flask_backend is an api, and part of the [webportal](https://github.com/BorodaUA/webportal) project.

## This api have next resources:

1. Users - CRUD operations with users
2. Blog_news - CRUD operations with stories, and comments
3. Hacker_news - CRUD operations with comments, and serving parsed [Hacker News](https://news.ycombinator.com/) data

## How to use:
### Local development mode:
1. Clone the repo
2. Create FLASK_BACKEND_DATABASE and HACKER_NEWS_DATABASE in the [postgres_server](https://github.com/BorodaUA/postgres_server) by command line inside that container, or by using [pgadmin4](https://github.com/BorodaUA/pgadmin4) web tool
3. Create .env file inside the repo with following data:
   - SECRET_KEY=string for flask app secret key
   - POSTGRES_DATABASE_URI=postgresql+psycopg2://username:password@postgres_server_url:postgres_server_port/name of the postgres database 
   - HACKER_NEWS_DATABASE_URI=postgresql+psycopg2://username:password@postgres_server_url:postgres_server_port/name of the postgres database
   - TEST_HACKER_NEWS_DATABASE_URI=postgresql+psycopg2://username:password@postgres_server_url:postgres_server_port/name of the postgres test database
   - FLASK_BACKEND_DATABASE_URI=postgresql+psycopg2://username:password@postgres_server_url:postgres_server_port/name of the postgres database
   - TEST_FLASK_BACKEND_DATABASE_URI=postgresql+psycopg2://username:password@postgres_server_url:postgres_server_port/name of the postgres test database
4. Run migrations:
      - For flask_backend_alembic:
        - cd to the folder /usr/src/flask_backend/flask_backend_alembic/
        - run command: "alembic upgrade head"
     - For hn_db_alembic:
       - cd to the folder /usr/src/flask_backend/hn_db_alembic
       - run command: "alembic upgrade head"
5. cd to the folder /usr/src/flask_backend/ and run command: "python `run.py`"