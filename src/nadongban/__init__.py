def create_app(config=None):
    from flask import Flask

    from .config import Config
    from .routes import web

    config = config or Config
    app = Flask(__name__)
    app.config.from_object(config)
    app.register_blueprint(web)

    with app.app_context():
        app.extensions["memory_store"] = config.build_memory_store()
        app.extensions["chatbot"] = config.build_chatbot(
            app.extensions["memory_store"]
        )

    return app
