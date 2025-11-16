# Project Architecture

## Overview

The qBittorrent Manager is designed with a modular architecture that allows easy extension with new features. The project follows Python best practices and uses a clean, maintainable structure.

## Core Design Principles

1. **Modularity**: Features are isolated in independent modules
2. **Extensibility**: Easy to add new modules without modifying core code
3. **Configuration-driven**: All behavior controlled through YAML configuration
4. **Clean separation of concerns**: Each component has a single responsibility
5. **Docker-first**: Designed to run reliably in containers

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        main.py                              │
│                   (Application Entry)                       │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ├─────────────────────┬──────────────────────┐
                 │                     │                      │
        ┌────────▼─────────┐  ┌───────▼───────┐   ┌─────────▼────────┐
        │ ConfigManager    │  │  QBitClient   │   │ ModuleManager    │
        │ - Load YAML      │  │ - qBit API    │   │ - Load modules   │
        │ - Env vars       │  │ - Connection  │   │ - Run modules    │
        │ - Validation     │  │ - Operations  │   │ - Orchestration  │
        └──────────────────┘  └───────────────┘   └─────────┬────────┘
                                                              │
                                                              │
                                    ┌─────────────────────────┼─────────────────┐
                                    │                         │                 │
                           ┌────────▼─────────┐    ┌─────────▼────────┐   ┌───▼────────┐
                           │  BaseModule      │    │ TrackerChecker   │   │  Future    │
                           │  (Abstract)      │    │  - Check status  │   │  Modules   │
                           │  - run()         │    │  - Tag torrents  │   │  ...       │
                           │  - config access │    │  - Filter cats   │   │            │
                           └──────────────────┘    └──────────────────┘   └────────────┘
```

## Component Details

### 1. Entry Point (`main.py`)

**Responsibility**: Application initialization and orchestration

**Key Functions**:
- Parse command-line arguments
- Initialize core components
- Coordinate module execution
- Handle errors and logging
- Manage application lifecycle

**Usage**:
```python
manager = QBitManager(config_path="config/config.yaml")
manager.run()  # Run all enabled modules
manager.run_specific_module("tracker_checker")  # Run specific module
```

### 2. Configuration Manager (`config_manager.py`)

**Responsibility**: Configuration loading and management

**Features**:
- Load YAML configuration files
- Override with environment variables
- Validate configuration structure
- Provide configuration access methods

**Configuration Hierarchy** (highest priority first):
1. Environment variables
2. config.yaml
3. Default values

**Example**:
```python
config_manager = ConfigManager("config/config.yaml")
config = config_manager.load_config()
value = config_manager.get("qbittorrent.host", "localhost")
```

### 3. qBittorrent Client (`qbit_client.py`)

**Responsibility**: qBittorrent API communication

**Features**:
- Connection management
- Authentication
- Torrent operations (get, filter, tag)
- Tracker operations
- Error handling

**API Methods**:
- `connect()` / `disconnect()`
- `get_torrents(category, tag)`
- `get_torrent_trackers(hash)`
- `add_tag(hashes, tag)`
- `remove_tag(hashes, tag)`

### 4. Module Manager (`module_manager.py`)

**Responsibility**: Module lifecycle management

**Features**:
- Dynamic module loading
- Module instantiation
- Execution orchestration
- Error isolation (one module failure doesn't stop others)

**Module Discovery**:
- Reads module configuration from `config.yaml`
- Dynamically imports from `modules/` directory
- Converts module names to class names (snake_case → PascalCase)

**Example**:
```
File: modules/tracker_checker.py
Class: TrackerChecker
Config key: tracker_checker
```

### 5. Base Module (`modules/base_module.py`)

**Responsibility**: Abstract base for all modules

**Provides**:
- Common configuration access
- Logger instance
- Configuration validation helpers
- Shared qBittorrent client access

**Contract**:
- All modules must inherit from `BaseModule`
- Must implement `run()` method
- Can access `self.qbit_client` and `self.config`

### 6. Tracker Checker Module (`modules/tracker_checker.py`)

**Responsibility**: Monitor tracker health and tag affected torrents

**Features**:
- Check all torrents or filter by category
- Analyze tracker status codes
- Check tracker error messages
- Apply/remove tags based on status
- Configurable error keywords

**Configuration**:
```yaml
tracker_checker:
  enabled: true
  categories: []  # All torrents
  tag: "broken-tracker"
  remove_tag_when_fixed: true
  check_message_for_errors: true
  error_keywords: ["not registered", "invalid passkey"]
```

## Data Flow

### Standard Execution Flow

```
1. main.py starts
   ↓
2. Load configuration (ConfigManager)
   ↓
3. Connect to qBittorrent (QBitClient)
   ↓
4. Load enabled modules (ModuleManager)
   ↓
5. For each module:
   a. Get torrents from qBittorrent
   b. Process torrents according to module logic
   c. Perform actions (tag, modify, etc.)
   d. Log results
   ↓
6. Disconnect and exit
```

### Module Execution Flow

```
ModuleManager.run_modules()
   ↓
For each enabled module:
   ↓
1. module.run() is called
   ↓
2. Module gets torrents via self.qbit_client.get_torrents()
   ↓
3. Module processes each torrent
   ↓
4. Module performs actions (tag, modify, etc.)
   ↓
5. Module logs results
   ↓
Continue to next module (even if one fails)
```

## Module Development Guide

### Creating a New Module

1. **Create module file**: `src/my_qbit_manager/modules/my_module.py`

2. **Inherit from BaseModule**:
```python
from my_qbit_manager.modules.base_module import BaseModule

class MyModule(BaseModule):
    def __init__(self, qbit_client, config):
        super().__init__(qbit_client, config)
        # Initialize module-specific settings
    
    def run(self):
        # Implement module logic
        torrents = self.qbit_client.get_torrents()
        # Process torrents...
```

3. **Add configuration**:
```yaml
modules:
  my_module:
    enabled: true
    setting1: value1
    setting2: value2
```

4. **Module is automatically loaded** when enabled!

### Module Best Practices

1. **Error Handling**: Always wrap main logic in try-except
2. **Logging**: Use `self.logger` for all logging
3. **Configuration**: Use `self.get_config()` with defaults
4. **Validation**: Validate critical configuration on init
5. **Documentation**: Document what the module does and its config options

## File Structure

```
my_qbit_manager/
├── src/my_qbit_manager/        # Application source code
│   ├── __init__.py
│   ├── main.py                 # Entry point
│   ├── config_manager.py       # Configuration handling
│   ├── qbit_client.py          # qBittorrent API wrapper
│   ├── module_manager.py       # Module orchestration
│   ├── modules/                # All modules
│   │   ├── __init__.py
│   │   ├── base_module.py      # Base class for modules
│   │   ├── tracker_checker.py  # Tracker health module
│   │   └── _module_template.py # Template for new modules
│   └── utils/                  # Utility functions
│       └── __init__.py
├── config/
│   └── config.yaml             # Main configuration
├── tests/                      # Unit tests
│   ├── __init__.py
│   └── test_*.py
├── docker/                     # Docker-specific files
│   ├── Dockerfile.cron
│   └── entrypoint-cron.sh
├── logs/                       # Application logs
│   ├── .gitkeep
│   └── *.log
├── Dockerfile                  # Main Docker image
├── docker-compose.yml          # Docker Compose config
├── pyproject.toml              # Project metadata
├── requirements.txt            # Dependencies
└── README.md                   # Documentation
```

## Configuration System

### Configuration Layers

1. **config.yaml**: Base configuration
2. **Environment variables**: Override config.yaml
3. **Command-line arguments**: Override everything

### Environment Variable Mapping

```
QBIT_HOST      → qbittorrent.host
QBIT_PORT      → qbittorrent.port
QBIT_USERNAME  → qbittorrent.username
QBIT_PASSWORD  → qbittorrent.password
QBIT_USE_SSL   → qbittorrent.use_ssl
```

### Module Configuration Structure

```yaml
modules:
  module_name:
    enabled: true/false
    # module-specific settings
```

## Docker Architecture

### Multi-stage Build

1. **Builder stage**: Install build dependencies and Python packages
2. **Runtime stage**: Copy only necessary files for minimal image size

### Volume Mounts

- `config/config.yaml`: Configuration (read-only)
- `logs/`: Log output (read-write)
- `modules/`: Optional for development (read-only)

### Deployment Options

1. **One-shot execution**: Run once and exit
2. **Cron-based**: Run on schedule
3. **External scheduler**: Triggered by external system

## Logging Architecture

### Log Levels

- **DEBUG**: Detailed diagnostic information
- **INFO**: General informational messages
- **WARNING**: Warning messages
- **ERROR**: Error messages
- **CRITICAL**: Critical errors

### Log Destinations

1. **Console**: stdout for Docker logs
2. **File**: `logs/qbit_manager.log` for persistent logging

### Log Format

```
%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

Example:
```
2025-01-15 10:30:45 - my_qbit_manager.modules.tracker_checker - INFO - Starting tracker checker module
```

## Extension Points

### Easy to Extend

1. **New modules**: Just create a new file in `modules/`
2. **New utilities**: Add to `utils/`
3. **Custom clients**: Extend or replace `QBitClient`
4. **Additional config sources**: Extend `ConfigManager`

### Future Enhancements

- Web UI for management
- REST API for remote control
- Webhook notifications
- Database for tracking history
- Metrics and monitoring
- Plugin system for third-party modules

## Dependencies

### Core Dependencies

- **qbittorrent-api**: qBittorrent API client library
- **pyyaml**: YAML configuration parsing
- **python-dotenv**: Environment variable loading

### Development Dependencies

- **pytest**: Testing framework
- **black**: Code formatter
- **flake8/pylint**: Linters
- **mypy**: Type checking

## Testing Strategy

### Test Structure

```
tests/
├── __init__.py
├── test_config_manager.py
├── test_qbit_client.py
├── test_module_manager.py
└── test_modules/
    └── test_tracker_checker.py
```

### Testing Approach

1. **Unit tests**: Test individual components
2. **Integration tests**: Test component interactions
3. **Mock external dependencies**: Use mocks for qBittorrent API

## Performance Considerations

1. **Connection reuse**: Single qBittorrent connection for all modules
2. **Efficient queries**: Filter torrents at API level when possible
3. **Batch operations**: Tag multiple torrents at once
4. **Minimal memory footprint**: Process torrents iteratively
5. **Docker optimization**: Multi-stage builds for small images

## Security Considerations

1. **Credentials**: Never log passwords
2. **Environment variables**: Use for sensitive data
3. **Docker user**: Run as non-root user in container
4. **Read-only mounts**: Configuration files mounted read-only
5. **Input validation**: Validate all configuration

## Monitoring and Observability

1. **Logs**: Comprehensive logging at all levels
2. **Health checks**: Docker health check configured
3. **Exit codes**: Proper exit codes for automation
4. **Metrics**: Easy to add Prometheus metrics
5. **Structured logging**: JSON format available

---

This architecture is designed to be maintainable, extensible, and production-ready while remaining simple to understand and use.
