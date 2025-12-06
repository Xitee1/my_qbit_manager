# WIP: qBittorrent Manager

_Warning: This is a vibe coded tool, most of it is unchecked because I personally do not give it a high priority, it must just work for me. Maybe I'll improve it in the future and clean up the AI shit a bit more_

A modular, extensible tool for managing qBittorrent torrents with automatic tracker health monitoring and other automation features.

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
   # Configure module settings and schedules
   ```

4. **Run with Docker Compose** (scheduler mode - runs continuously):
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

2. **Install the package**:
   ```bash
   pip install -e .
   ```

3. **Configure the application**:
   ```bash
   cp .env.example .env
   # Edit .env and config/config.yaml
   ```

4. **Run the application**:
   ```bash
   # Run once and exit
   python -m my_qbit_manager.main --mode once
   
   # Run scheduler (continuous mode with per-module schedules)
   python -m my_qbit_manager.main --mode scheduler
   
   # Run a specific module
   python -m my_qbit_manager.main --mode module --module tracker_checker
   ```

## Configuration

### Environment Variables

Environment variables **always take priority** over `config.yaml` for qBittorrent settings:

- `QBIT_HOST`: qBittorrent host address
- `QBIT_PORT`: qBittorrent port
- `QBIT_USERNAME`: qBittorrent username
- `QBIT_PASSWORD`: qBittorrent password
- `QBIT_USE_SSL`: Use HTTPS (true/false)

**Note**: Only qBittorrent connection settings can be overridden via environment variables. All other settings (modules, schedules, etc.) must be configured in `config.yaml`.

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
  schedule:
    enabled: true           # Enable scheduled execution
    interval_minutes: 360   # Run every 6 hours
    run_on_start: true      # Run immediately on start
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
# Run as service with configured schedulers
python -m my_qbit_manager.main

# Run a specific module once
python -m my_qbit_manager.main --module tracker_checker

# Use a specific config file
python -m my_qbit_manager.main --config /path/to/config.yaml

# Show version
python -m my_qbit_manager.main --version
```

## Docker Deployment

### Scheduler Service (Default)

The default Docker Compose configuration runs the scheduler service, which executes modules based on their individual schedules:

```bash
docker-compose up -d
```

This runs continuously and checks module schedules every minute. Each module's schedule is configured in `config.yaml`.

### One-time Execution

To run all modules once and exit:

```bash
docker-compose run --rm qbit-manager --mode once
```

### Service Architecture

The Docker setup is designed to be extensible:
- **Scheduler service**: Current default (runs modules on their schedules)
- **One-time service**: Run on-demand or via external scheduler
- **API service**: Future enhancement (not yet implemented)

The same Docker image supports all modes via command-line arguments.

## Development

### Install Development Dependencies

```bash
pip install -e ".[dev]"
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
