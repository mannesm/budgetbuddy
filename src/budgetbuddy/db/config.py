DATABASE_TYPE = "postgresql"
DATABASE_DRIVER = "psycopg2"
DATABASE_USER = "postgres"
DATABASE_PASSWORD = "postgres"
DATABASE_HOST = "localhost"
DATABASE_PORT = "5432"
DATABASE_NAME = "budgetbuddy"

DATABASE_URL = f"{DATABASE_TYPE}+{DATABASE_DRIVER}://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"

NAMING_CONVENTION = {
    "ix": "ix__%(column_0_N_label)s",
    "uq": "uq__%(table_name)s__%(column_0_N_name)s",
    "ck": "ck__%(table_name)s__%(constraint_name)s",
    "fk": "fk__%(table_name)s__%(column_0_N_name)s__%(referred_table_name)s",
    "pk": "pk__%(table_name)s",
}
