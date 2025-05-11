#!/bin/bash -xe

REPO_NAME=umd_data605
IMAGE_NAME=umd_data605_template
FULL_IMAGE_NAME="${REPO_NAME}/${IMAGE_NAME}"

# Verify the image exists
docker image ls "${FULL_IMAGE_NAME}"

# Name your container
CONTAINER_NAME="${IMAGE_NAME}"

# Mount YOUR project directory (the folder containing this script) as /data
PROJECT_ROOT="$(pwd)"  

echo "Launching container '${CONTAINER_NAME}' with '${FULL_IMAGE_NAME}', mounting '${PROJECT_ROOT}' at /data"

docker run --rm -ti \
    --name "${CONTAINER_NAME}" \
    -p 8888:8888 \
    -v "${PROJECT_ROOT}":/data \
    --entrypoint /bin/bash \
    "${FULL_IMAGE_NAME}"

