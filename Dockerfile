FROM python:3.12-slim@sha256:cb33f7f771ecec2ef1225cf39b159591a040391bd73e4c01f00fdfc4c47611d2
WORKDIR /app
RUN useradd --uid 10001 --create-home researcher
COPY summary.py ./
COPY data/bookings.csv ./data/bookings.csv
USER researcher
CMD ["python", "summary.py", "data/bookings.csv", "--column", "duration_minutes", "--output", "/tmp/result.json"]
