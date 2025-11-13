# GitHub Actions Workflows

## Build and Push Container Image

This workflow builds a container image using Podman and pushes it to Docker Hub. The project uses `Containerfile` (OCI-standard) instead of `Dockerfile` for vendor-agnostic container builds.

### Required Secrets

Configure the following secrets in your GitHub repository settings (Settings → Secrets and variables → Actions):

1. **DOCKER_TOKEN**: Your Docker Hub access token
   - Generate at: https://hub.docker.com/settings/security
   - Needs "Read, Write & Delete" permissions

2. **DOCKER_USERNAME**: Your Docker Hub username
   - This is your Docker Hub account username

### Workflow Triggers

The workflow runs on:
- Push to `main` or `master` branch
- Push of tags starting with `v*` (e.g., `v1.0.0`)
- Pull requests to `main` or `master` (builds but doesn't push)
- Manual trigger via `workflow_dispatch`

### Image Tags

The workflow creates the following tags:
- `latest` - Always points to the latest build from the default branch
- `{sha}` - Git commit SHA (e.g., `abc123def456`)
- `{branch}-{sha}` - Branch name and SHA for non-default branches
- Semantic version tags (e.g., `v1.0.0`, `v1.0`) when pushing version tags

### Usage

After pushing to the repository, the workflow will automatically:
1. Build the container image using Podman from `Containerfile`
2. Tag it with multiple tags
3. Push to Docker Hub (unless it's a pull request)

You can then pull and use the image:
```bash
podman pull <your-username>/crm-api:latest
# or with Docker
docker pull <your-username>/crm-api:latest
```

### Building Locally

You can build the container image locally using either Podman or Docker:

```bash
# With Podman
podman build -t crm-api:local -f Containerfile .

# With Docker
docker build -t crm-api:local -f Containerfile .
```

