# Running Minimeter2 on macOS

This guide helps you set up and run the `minimeter2` project on your MacBook.

## 1. Prerequisites

Ensure you have the following installed:
- **Python 3.12+**: [Download Python](https://www.python.org/downloads/)
- **Docker** (Optional, for containerized run): [Download Docker Desktop](https://www.docker.com/products/docker-desktop/)

## 2. Setup (Local Python)

1.  **Clone the repository** (if you haven't already):
    ```bash
    git clone https://github.com/aliucer/minimeter2.git
    cd minimeter2
    ```

2.  **Add Secrets**:
    > [!IMPORTANT]
    > The file `psychic-destiny-*.json` (GCP Service Account Key) is **NOT** included in the repository for security.
    > You must manually copy this file from your original environment to the root of the `minimeter2` project folder on your Mac.

3.  **Create a Virtual Environment**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

4.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

5.  **Run the API**:
    ```bash
    uvicorn api.main:app --reload
    ```

## 3. Setup (Docker)

If you prefer using Docker to match the Linux environment closely:

1.  **Build the Image**:
    ```bash
    docker build -t minimeter2 .
    ```

2.  **Run the Container**:
    *Make sure the JSON key file is present in the directory before building/running!*
    ```bash
    docker run -p 8080:8080 minimeter2
    ```

## 4. Mac-Specific Notes

- **M1/M2/M3 Apple Silicon**:
    - If you encounter issues with `psycopg2-binary`, try installing `psycopg2` from source or ensure Rosetta is used if needed. However, `psycopg2-binary` usually works fine on newer macOS versions.
    - If `pip install` fails for some libraries, you might need to install build tools: `xcode-select --install`.

- **Ports**:
    - The default port `8080` is often used by other services. If it's busy, change the `--port` flag in the `uvicorn` command or the `-p` flag in Docker (e.g., `-p 8081:8080`).
