import argparse
from .database import Base, SessionLocal, engine
from .models import User
from .services.security import hash_password

def main():
    parser=argparse.ArgumentParser(description="Create or promote a CleanCut admin")
    parser.add_argument("--email", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--name", default="CleanCut Admin")
    args=parser.parse_args()
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        user=db.query(User).filter(User.email==args.email.strip().lower()).first()
        if user is None:
            user=User(name=args.name,email=args.email.strip().lower(),password_hash=hash_password(args.password),is_admin=True)
            db.add(user)
        else:
            user.password_hash=hash_password(args.password); user.is_admin=True
        db.commit()
        print(f"Admin ready: {user.email}")

if __name__ == "__main__": main()
