import asyncio
import os

from flask import Flask, url_for

from error import Error


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    @app.errorhandler(Error)
    def handle_error(error):
        return (error.message + f'<br><a class="action" href="{url_for("quotes.register")}">Go back</a>'), error.code

    from . import db
    db.init_app(app)

    from . import quotes
    app.register_blueprint(quotes.bp)

    from . import poke
    app.register_blueprint(poke.bp)
    app.add_url_rule('/', endpoint='index')

    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    return app