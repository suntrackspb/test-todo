"""CLI for administrative tasks (e.g. adding users manually).

Usage:
    python manage.py create-user <login> <password> [display_name]
    python manage.py list-users
"""
import sys

from app.core.security import hash_password
from app.database import Base, SessionLocal, engine
from app.models import User


def create_user(login: str, password: str, display_name: str | None = None) -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(User).filter(User.login == login).first():
            print(f"User '{login}' already exists")
            return
        user = User(
            login=login,
            password_hash=hash_password(password),
            display_name=display_name or login,
        )
        db.add(user)
        db.commit()
        print(f"Created user '{login}' (id={user.id})")
    finally:
        db.close()


def list_users() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        for user in db.query(User).all():
            print(f"{user.id}\t{user.login}\t{user.display_name}")
    finally:
        db.close()


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]
    if command == "create-user":
        if len(sys.argv) < 4:
            print("Usage: python manage.py create-user <login> <password> [display_name]")
            sys.exit(1)
        display_name = sys.argv[4] if len(sys.argv) > 4 else None
        create_user(sys.argv[2], sys.argv[3], display_name)
    elif command == "list-users":
        list_users()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
