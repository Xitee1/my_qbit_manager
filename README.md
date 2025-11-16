# qBittorrent Manager

A modular, extensible tool for managing qBittorrent torrents with automatic tracker health monitoring and other automation features.

## Features

- 🔌 **Modular Architecture**: Easy to add new features as independent modules
- 🏷️ **Tracker Checker**: Automatically detects and tags torrents with non-working trackers
- ⚙️ **Configurable**: YAML-based configuration with environment variable support
- 🐳 **Dockerized**: Ready to run in Docker with docker-compose
- 📊 **Comprehensive Logging**: Detailed logs for monitoring and debugging
- 🔄 **Extensible**: Simple base class for creating new modules

## Project Structure

```
my_qbit_manager/
├── src/
│   └── my_qbit_manager/
│       ├── __init__.py
│       ├── main.py              # Application entry point
│       ├── config_manager.py    # Configuration handling
│       ├── qbit_client.py       # qBittorrent API wrapper
│       ├── module_manager.py    # Module loading and execution
│       ├── modules/
│       │   ├── __init__.py
│       │   ├── base_module.py   # Base class for all modules
│       │   └── tracker_checker.py  # Tracker health checker module
│       └── utils/
├── config/
│   └── config.yaml              # Main configuration file
├── tests/                       # Unit tests
├── docker/
│   ├── Dockerfile.cron         # Dockerfile with cron scheduler
│   └── entrypoint-cron.sh      # Cron entrypoint script
├── logs/                        # Application logs
├── Dockerfile                   # Main Dockerfile
├── docker-compose.yml          # Docker Compose configuration
├── pyproject.toml              # Project metadata and dependencies
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Quick Start

### Using Docker Compose (Recommended)

1. **Clone or create the project directory**

2. **Copy and configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your qBittorrent credentials
   ```

3. **Edit the configuration**:
   ```bash
   nano config/config.yaml
   # Update qBittorrent connection details and module settings
   ```

4. **Run with Docker Compose**:
   ```bash
   docker-compose up -d
   ```

5. **View logs**:
   ```bash
   docker-compose logs -f
   # or check the logs directory
   tail -f logs/qbit_manager.log
   ```

### Manual Installation

1. **Install Python 3.8 or higher**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the application**:
   ```bash
   cp .env.example .env
   # Edit .env and config/config.yaml
   ```

4. **Run the application**:
   ```bash
   python -m my_qbit_manager.main
   ```

## Configuration

### Environment Variables

Configuration can be set via environment variables (these override `config.yaml`):

- `QBIT_HOST`: qBittorrent host address
- `QBIT_PORT`: qBittorrent port
- `QBIT_USERNAME`: qBittorrent username
- `QBIT_PASSWORD`: qBittorrent password
- `QBIT_USE_SSL`: Use HTTPS (true/false)

### config.yaml

The main configuration file controls all aspects of the application:

```yaml
qbittorrent:
  host: "localhost"
  port: 8080
  username: "admin"
  password: "adminpass"
  use_ssl: false

modules:
  tracker_checker:
    enabled: true
    categories: []  # Empty = check all torrents
    tag: "broken-tracker"
    remove_tag_when_fixed: true
```

## Modules

### Current Modules

#### Tracker Checker

Monitors torrent trackers and tags torrents with non-working trackers.

**Features**:
- Checks all trackers for each torrent
- Detects tracker failures by status code
- Analyzes tracker error messages
- Applies configurable tags to affected torrents
- Optionally filters by category
- Automatically removes tags when trackers are working again

**Configuration**:
```yaml
tracker_checker:
  enabled: true
  categories: []  # Filter by categories, or [] for all
  tag: "broken-tracker"
  remove_tag_when_fixed: true
  check_message_for_errors: true
  error_keywords:
    - "not registered"
    - "invalid passkey"
    # ... more keywords
```

### Creating New Modules

To create a new module:

1. **Create a new file** in `src/my_qbit_manager/modules/`:
   ```python
   # src/my_qbit_manager/modules/my_new_module.py
   from my_qbit_manager.modules.base_module import BaseModule
   
   class MyNewModule(BaseModule):
       def run(self):
           # Your module logic here
           torrents = self.qbit_client.get_torrents()
           # ... process torrents
   ```

2. **Add configuration** in `config.yaml`:
   ```yaml
   modules:
     my_new_module:
       enabled: true
       # Your module settings
   ```

3. **The module will be automatically loaded** when enabled!

## Command Line Options

```bash
# Run all enabled modules
python -m my_qbit_manager.main

# Run a specific module
python -m my_qbit_manager.main --module tracker_checker

# Use a custom config file
python -m my_qbit_manager.main --config /path/to/config.yaml

# Show version
python -m my_qbit_manager.main --version
```

## Docker Deployment

### One-time Execution

Use the standard docker-compose setup to run the manager once:

```bash
docker-compose up
```

### Scheduled Execution (Cron)

To run the manager on a schedule, uncomment the cron service in `docker-compose.yml`:

```yaml
services:
  qbit-manager-cron:
    build:
      context: .
      dockerfile: docker/Dockerfile.cron
    environment:
      - CRON_SCHEDULE=0 */6 * * *  # Every 6 hours
    # ... other settings
```

Then start with:
```bash
docker-compose up -d qbit-manager-cron
```

## Development

### Install Development Dependencies

```bash
pip install -r requirements-dev.txt
```

### Run Tests

```bash
pytest
```

### Code Formatting

```bash
black src/
```

### Linting

```bash
flake8 src/
pylint src/my_qbit_manager/
```

## Logging

Logs are written to:
- Console (stdout)
- `logs/qbit_manager.log`

Log level can be configured in `config.yaml`:
```yaml
logging:
  level: "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

## Troubleshooting

### Connection Issues

- Verify qBittorrent Web UI is enabled
- Check qBittorrent host/port settings
- Ensure credentials are correct
- Check firewall/network settings

### Module Not Loading

- Check module is enabled in config.yaml
- Verify module file exists in `modules/` directory
- Check logs for import errors
- Ensure module class name matches file name pattern

### Docker Issues

- Check container logs: `docker-compose logs`
- Verify volume mounts in docker-compose.yml
- Ensure config.yaml is properly mounted

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

## Roadmap

Future module ideas:
- Automatic torrent cleanup based on seeding ratio/time
- Stalled torrent detector
- Duplicate torrent finder
- Category organizer based on trackers
- Health report generator
- Webhook notifications

## Support

For issues, questions, or feature requests, please open an issue on GitHub.
