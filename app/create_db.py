from app.db.database import engine
from app.models.load import Base

Base.metadata.create_all(bind=engine)

print("Database and tables created successfully!")
