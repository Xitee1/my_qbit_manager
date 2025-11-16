# Quick Setup Guide

## Prerequisites

- Python 3.8 or higher (for local development)
- Docker and Docker Compose (for containerized deployment)
- Access to a qBittorrent instance with Web UI enabled

## Installation Steps

### Option 1: Docker Compose (Recommended)

1. **Navigate to the project directory**:
   ```bash
   cd /home/mato/projects/tools/my_qbit_manager
   ```

2. **Set up environment variables**:
   ```bash
   cp .env.example .env
   nano .env  # Edit with your qBittorrent credentials
   ```

3. **Configure the application**:
   ```bash
   nano config/config.yaml  # Adjust settings as needed
   ```

4. **Build and run**:
   ```bash
   docker-compose build
   docker-compose up -d
   ```

5. **Check logs**:
   ```bash
   docker-compose logs -f
   # or
   tail -f logs/qbit_manager.log
   ```

### Option 2: Local Python Installation

1. **Navigate to the project directory**:
   ```bash
   cd /home/mato/projects/tools/my_qbit_manager
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Linux/Mac
   # or
   venv\Scripts\activate  # On Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up configuration**:
   ```bash
   cp .env.example .env
   nano .env  # Edit with your credentials
   nano config/config.yaml  # Adjust settings
   ```

5. **Run the application**:
   ```bash
   python -m my_qbit_manager.main
   ```

### Using Makefile (Linux/Mac)

The project includes a Makefile for common tasks:

```bash
# Initialize project
make init

# Install dependencies
make install

# Run the application
make run

# Run with Docker
make docker-build
make docker-run

# View available commands
make help
```

## Configuration Overview

### qBittorrent Settings

Edit `config/config.yaml`:

```yaml
qbittorrent:
  host: "localhost"      # Your qBittorrent host
  port: 8080            # Web UI port
  username: "admin"     # Web UI username
  password: "adminpass" # Web UI password
  use_ssl: false        # true if using HTTPS
```

Or use environment variables (override config.yaml):
- `QBIT_HOST`
- `QBIT_PORT`
- `QBIT_USERNAME`
- `QBIT_PASSWORD`
- `QBIT_USE_SSL`

### Module Configuration

Enable/disable modules and configure their behavior in `config/config.yaml`:

```yaml
modules:
  tracker_checker:
    enabled: true
    categories: []  # Filter by categories, or [] for all torrents
    tag: "broken-tracker"
    remove_tag_when_fixed: true
```

## Testing the Setup

1. **Test qBittorrent connection**:
   ```bash
   # Docker
   docker-compose logs
   
   # Local
   python -m my_qbit_manager.main
   ```

2. **Check for errors** in the logs:
   - Console output
   - `logs/qbit_manager.log`

3. **Verify in qBittorrent Web UI**:
   - Check if tags are being applied
   - Look for the tag configured in your settings (e.g., "broken-tracker")

## Troubleshooting

### Cannot connect to qBittorrent

1. Verify qBittorrent Web UI is enabled:
   - Tools → Options → Web UI → Check "Web User Interface"

2. Check host and port:
   - Default is usually `localhost:8080`
   - If qBittorrent is remote, use the IP address

3. Verify credentials:
   - Username and password must match Web UI settings

### Module not running

1. Check if module is enabled in `config/config.yaml`:
   ```yaml
   modules:
     tracker_checker:
       enabled: true  # Must be true
   ```

2. Check logs for errors:
   ```bash
   tail -f logs/qbit_manager.log
   ```

### Docker issues

1. Check if containers are running:
   ```bash
   docker-compose ps
   ```

2. View container logs:
   ```bash
   docker-compose logs -f
   ```

3. Rebuild containers:
   ```bash
   docker-compose down
   docker-compose build --no-cache
   docker-compose up -d
   ```

## Next Steps

1. **Run the application** and verify it works
2. **Check the logs** to see what it's doing
3. **Customize module settings** in `config/config.yaml`
4. **Set up scheduled execution** (optional):
   - Use the cron Docker setup
   - Or set up a system cron job
5. **Create new modules** as needed (see README.md)

## Getting Help

- Check `README.md` for detailed documentation
- Review logs for error messages
- Verify qBittorrent API connectivity
- Check Docker container status (if using Docker)
