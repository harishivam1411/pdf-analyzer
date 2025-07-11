# Building and running your application with Docker

1. **Build and start the application:**

   ```bash
   docker compose up --build
   ```

   - The FastAPI backend will be available at [http://localhost:7000](http://localhost:7000).
   - The Streamlit frontend will be available at [http://localhost:8501](http://localhost:8501).

2. **Environment variables:**
   - Make sure to create a `.env` file in the project root with your OpenAI API key and other settings (see `README.md` for details).

## Deploying your application to the cloud

1. **Build your image for the correct architecture:**

   ```bash
   docker build --platform=linux/amd64 -t myapp .
   ```

   _(Use `--platform` if your cloud provider uses a different CPU architecture than your local machine.)_

2. **Push the image to your registry:**

   ```bash
   docker push myregistry.com/myapp
   ```

3. **Run your container in the cloud using your preferred orchestration platform (e.g., Docker Compose, Kubernetes, etc.).**

---

**Note:**

- The backend and frontend services are defined in `compose.yaml`.
- For development, code changes are synced automatically in the container.
- For troubleshooting, check logs with `docker compose logs`.
