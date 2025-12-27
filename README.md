# WIP: qBittorrent Manager

_Warning: This is a vibe coded tool, most of it is unchecked because I personally do not give it a high priority, it must just work for me. Maybe I'll improve it in the future and clean up the AI shit a bit more_

A modular, extensible tool for managing qBittorrent torrents with automatic tracker health monitoring and other automation features.

## Installation


1. **Create docker-compose.yaml** and copy the content from `docker-compose.prod.yaml`

2. **Start the container**:
   ```bash
   docker-compose up -d
   ```

4. **Edit the configuration**:
   Stop the container again and edit the configuration.
   ```bash
   nano config/config.yaml
   ```


---

## Development setup

### With docker

1. **Run with Docker Compose** (builds locally, mounts source code):
   ```bash
   docker-compose up
   ```


### Local Python Development (Without Docker)

1. **Create a virtual environment** (recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install the package**:
   ```bash
   pip install -e .
   ```

5. Start:
   ```bash
   python -m my_qbit_manager.main --mode once
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
- Tags torrents with not working trackers (and removes the tag if it's working again)
- Define amount of minimum working trackers (if a torrent has less than the minimum tracker amount, all of them must be available)
- Restrict to specific categories


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


### Service Architecture

The Docker setup is designed to be extensible:
- **Scheduler service**: Default mode (runs modules on their configured schedules)
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
