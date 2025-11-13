# Building the Container Image

## Quick Build

Use the provided build script:

```bash
./build.sh
```

Or specify a custom image name:

```bash
./build.sh crm-api:v1.0.0
```

## Manual Build

### With Podman (Recommended)

If you encounter network/netavark errors, use the `--network=host` flag:

```bash
# Rootless Podman
podman build --network=host -t crm-api:local -f Containerfile .

# Or with sudo (if rootless doesn't work)
sudo podman build --network=host -t crm-api:local -f Containerfile .
```

### With Docker

```bash
docker build -t crm-api:local -f Containerfile .
```

## Troubleshooting Podman Network Issues

If you see errors like:
```
netavark: nftables error: "nft" did not return successfully
```

**Solutions:**

1. **Use --network=host flag** (recommended):
   ```bash
   podman build --network=host -t crm-api:local -f Containerfile .
   ```

2. **Fix Podman network configuration**:
   ```bash
   # For rootless Podman
   podman network reload
   
   # Or reset Podman
   podman system reset
   ```

3. **Use Docker instead** (if Podman issues persist):
   ```bash
   docker build -t crm-api:local -f Containerfile .
   ```

## Testing the Image

After building, test the image:

```bash
# With Podman
podman run -p 8080:8080 crm-api:local

# With Docker
docker run -p 8080:8080 crm-api:local
```

The application will be available at `http://localhost:8080`

## GitHub Actions

The GitHub Actions workflow automatically builds and pushes the image to Docker Hub. No manual intervention needed - just push to the repository!

