# Setting arguments for the python and uv versions
ARG PYTHON_VERSION=3.12.8
ARG UV_VERSION=0.7.8

# Stage to extract uv binary
FROM ghcr.io/astral-sh/uv:${UV_VERSION} AS uvbin

# Base image for building the application
FROM python:${PYTHON_VERSION}-slim-bookworm AS builder

# Install uv
COPY --from=uvbin /uv /uvx /bin/

# Change the working directory to the `code` directory
WORKDIR /code

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev

# Copy only necessary application files
COPY main.py /code/
COPY app/ /code/app/
COPY pyproject.toml /code/
COPY uv.lock /code/
# Add other necessary files/directories here, avoid copying everything

# Sync the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

# Runtime stage - use same base image for compatibility
FROM python:${PYTHON_VERSION}-slim-bookworm AS runtime

# Setting the dependent environment variables
ENV EMBEDDING_MODEL=all-MiniLM-L6-v2
ENV OPENAI_BASE_URL=https://api.openai.com/v1
ENV VECTOR_PERSIST=True
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copy only the virtual environment and necessary files
COPY --from=builder /code/.venv /code/.venv
COPY --from=builder /code/main.py /code/main.py
COPY --from=builder /code/app /code/app
# Copy other necessary runtime files

# Set working directory
WORKDIR /code

# Place executables in the environment at the front of the path
ENV PATH="/code/.venv/bin:$PATH"

# Expose the port that the application will run on
EXPOSE 7000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:7000/health || exit 1

# Start the Backend (FastAPI) applications
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7000"]