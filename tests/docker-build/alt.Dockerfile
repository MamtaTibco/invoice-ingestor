FROM busybox:latest AS test
WORKDIR /app

# A benign change to trigger test workflow
ENV TAINT="Mon Jan 27 10:04:49 EST 2025"

# simulate test artifacts
COPY requirements.txt ./

# Simulate test logic (echo statement)
RUN echo "Running tests..." && \
    echo "Tests passed!"

# Production stage
FROM busybox:latest AS production
WORKDIR /app

# Copy files from the test stage
COPY --from=test /app/requirements.txt ./

# Simulate build logic
CMD ["echo", "Build successful!"]
