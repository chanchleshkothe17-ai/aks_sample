import os

# Use SQLite for CI tests
os.environ["DATABASE_URL"] = "sqlite:///./test.db"