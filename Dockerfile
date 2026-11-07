FROM node:22-alpine AS assets
WORKDIR /assets
COPY package*.json frontend.css ./
RUN npm ci --ignore-scripts
COPY scripts/vendor.mjs scripts/vendor.mjs
COPY frontend frontend
COPY reconflow/templates reconflow/templates
RUN mkdir -p reconflow/static && npm run build

FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN pip install --no-cache-dir uv==0.11.8 && useradd --create-home --uid 10001 reconflow
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev
COPY reconflow reconflow
COPY migrations migrations
COPY alembic.ini ./
COPY docs docs
COPY public-docs public-docs
COPY scripts scripts
COPY --from=assets /assets/reconflow/static/ reconflow/static/
USER reconflow
ENV PATH="/app/.venv/bin:$PATH"
CMD ["uvicorn", "reconflow.main:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log", "--no-proxy-headers"]
