from pathlib import Path
from alembic import command
from alembic.config import Config
import argparse
import os
import json

settings_path = Path(__file__).with_name("local.settings.json")
if settings_path.exists():
    values = json.loads(settings_path.read_text()).get("Values", {})
    os.environ.update(values)


BASE_DIR = Path(__file__).resolve().parent
ALEMBIC_INI_PATH = BASE_DIR / "alembic.ini"
MIGRATIONS_DIR = BASE_DIR / "migrations"


def run_migrations(revision: str = "head", sql: bool = False) -> None:
    cfg = Config(str(ALEMBIC_INI_PATH))
    cfg.set_main_option("script_location", str(MIGRATIONS_DIR))
    cfg.set_main_option("sqlalchemy.url", os.environ["DB_URL"])

    if sql:
        command.upgrade(cfg, revision, sql=True)
    else:
        command.upgrade(cfg, revision)


def create_revision(message: str, autogenerate: bool = True) -> None:
    cfg = Config(str(ALEMBIC_INI_PATH))
    cfg.set_main_option("script_location", str(MIGRATIONS_DIR))
    cfg.set_main_option("sqlalchemy.url", os.environ["DB_URL"])

    command.revision(cfg, message=message, autogenerate=autogenerate)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Alembic helpers")
    sub = parser.add_subparsers(dest="cmd", required=True)

    up_parser = sub.add_parser("upgrade", help="Upgrade to a revision (default: head)")
    up_parser.add_argument("revision", nargs="?", default="head", help="Revision identifier")

    rev_parser = sub.add_parser("revision", help="Create a new revision")
    rev_parser.add_argument("-m", "--message", required=True, help="Revision message")

    args = parser.parse_args()

    if args.cmd == "upgrade":
        run_migrations(revision=args.revision)
    elif args.cmd == "revision":
        create_revision(message=args.message, autogenerate=True)
