# Dockerfile
FROM postgres:16

# Optional: set default env vars (you can override via docker run or docker-compose)
ENV POSTGRES_USER=admin
ENV POSTGRES_PASSWORD=admin
ENV POSTGRES_DB=localdb

# Copy any init SQL (optional)
# COPY init.sql /docker-entrypoint-initdb.d/

EXPOSE 5432
