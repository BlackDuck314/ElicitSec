FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
COPY fixtures ./fixtures
COPY suites ./suites
COPY scripts ./scripts
RUN pip install --no-cache-dir -e .
CMD ["elicitsec", "run", "--suites", "suites", "--adapter", "mock"]
