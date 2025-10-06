from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import sessionmaker

# I have created a seperate Postgress test database named budgetbuddy_test
# Update the connection string as per your test database configuration

TEST_DATABASE_URL = (
    "postgresql+psycopg2://postgres:password@localhost:5432/budgetbuddy_test"
)
TEST_DB_NAME = "budgetbuddy_test"
TEST_SCHEMA = "test_schema"

TEST_ENGINE = create_engine(
    TEST_DATABASE_URL,
    connect_args={"options": f"-csearch_path={TEST_SCHEMA}"},
    poolclass=StaticPool,
)

TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=TEST_ENGINE)
