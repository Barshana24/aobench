"""Allow ``python -m aobench`` as an alias for the ``aobench`` console script.

Useful when the console script is not on ``PATH`` — a common situation inside CI
containers, tox environments, and `pip install --user` setups.
"""

from aobench.cli.main import app

if __name__ == "__main__":
    app()
