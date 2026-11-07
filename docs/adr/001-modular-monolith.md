# ADR 001: modular monolith and PostgreSQL job worker

Accepted for prototype. One FastAPI app and one worker share service modules and transactions.
DB leases and SKIP LOCKED avoid Redis/Celery/Kafka operations on a small VPS. This reduces deployment
cost and atomicity complexity; polling and per-payout queries trade throughput for inspectability.
One worker is the supported production target. A larger queue fleet requires load, lock and failure
validation; the included PostgreSQL concurrency check only proves two claims cannot own one row.
