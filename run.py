from flask_back_1 import create_app

app = create_app()


if __name__ == "__main__":
    app.run(
        port=4000,
        debug=True,
        use_debugger=False,
        use_reloader=False,
        passthrough_errors=True,
    )
