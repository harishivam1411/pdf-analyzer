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

# Setting the dependent environment variables
ENV EMBEDDING_MODEL=all-MiniLM-L6-v2
ENV OPENAI_BASE_URL=https://api.openai.com/v1
ENV VECTOR_PERSIST=True

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev

# Copy the project into the image
COPY . /code

# Sync the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

# Place executables in the environment at the front of the path
ENV PATH="/code/.venv/bin:$PATH"

# Expose the port that the application will run on
EXPOSE 7000

# Reset the entrypoint, don't invoke `uv`
ENTRYPOINT []

# Start the Backend (FastAPI) applications
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7000"]