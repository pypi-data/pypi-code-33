#!/usr/bin/env python

from .views import app
import click


@click.command()
@click.argument("url", default=app.config["witness_url"])
@click.option("--listen", default=8088)
def main(listen, url):
    app.config["witness_url"] = url or app.config["witness_url"]
    app.config["port"] = listen or app.config["port"]
    app.run(port=app.config["port"], host="0.0.0.0", debug=True)


if __name__ == "__main__":
    main()
