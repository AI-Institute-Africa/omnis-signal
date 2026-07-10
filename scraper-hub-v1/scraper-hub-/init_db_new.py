from app.db.base import Base
from app.db.session import engine
import app.db.models  # Import models to register them with Base

def init_db():
    print("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    print("Done.")

if __name__ == "__main__":
    init_db()
