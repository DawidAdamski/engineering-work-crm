#!/bin/bash
# Build script for CRM API container image
# This script handles Podman network issues by using --network=host

set -e

IMAGE_NAME="${1:-crm-api:local}"
CONTAINERFILE="${2:-Containerfile}"

echo "Building container image: $IMAGE_NAME"
echo "Using Containerfile: $CONTAINERFILE"

# Try building with --network=host to bypass netavark issues
if command -v podman &> /dev/null; then
    echo "Using Podman..."
    if podman build --network=host -t "$IMAGE_NAME" -f "$CONTAINERFILE" .; then
        echo "✅ Build successful with Podman!"
        exit 0
    else
        echo "⚠️  Podman build failed, trying with sudo..."
        if sudo podman build --network=host -t "$IMAGE_NAME" -f "$CONTAINERFILE" .; then
            echo "✅ Build successful with sudo Podman!"
            exit 0
        fi
    fi
fi

# Fallback to Docker if Podman fails
if command -v docker &> /dev/null; then
    echo "Using Docker as fallback..."
    if docker build -t "$IMAGE_NAME" -f "$CONTAINERFILE" .; then
        echo "✅ Build successful with Docker!"
        exit 0
    fi
fi

echo "❌ Build failed with all available tools"
exit 1

