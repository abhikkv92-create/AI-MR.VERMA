# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [6.0.0] - 2026-02-19

### 🎉 Major Release - Repository Cleanup & Optimization

### 🗑️ Removed
- **BREAKING**: Removed 64+ redundant and unused files
  - 16 documentation files consolidated to 4
  - 12 redundant batch scripts consolidated to 4
  - 8 duplicate agent scripts
  - 16+ orphaned Python files
  - 4 legacy Docker files
  - 11 __pycache__ directories from git tracking
  - 244 runtime data files (67MB) from git tracking

### 🔧 Fixed
- **CRITICAL**: Fixed exposed NVIDIA API key in test file
- **CRITICAL**: Fixed missing `milvus_svc` instantiation causing NameError
- Fixed missing `typing.Any` import in core/memory_service.py
- Fixed hardcoded Docker paths - now use environment variables
- Fixed Docker compose hard dependencies on Milvus (now optional)
- Fixed pymilvus version inconsistency across requirements files

### ✨ Added
- Added comprehensive `.gitignore` with 165+ patterns
- Added `.gitattributes` for consistent line endings
- Added `.gitkeep` files for data directory structure
- Added environment variable support for all paths
- Added graceful fallback when Milvus is unavailable

### 🏗️ Changed
- Consolidated entry scripts with `--mode` parameter
- Moved Docker files to `docker/` subdirectory
- Updated docker-compose.yml build contexts
- Consolidated requirements (removed requirements.txt)
- Updated pyproject.toml dependencies
- Removed torch, transformers, peft, datasets (unused)

### 📊 Stats
- Repository size reduced from **114MB to ~47MB** (59% reduction)
- Total lines removed: **20,000+**
- Security vulnerabilities fixed: **1**
- Critical bugs fixed: **3**

### 🎯 Agent Lightning Integration
- **VERDICT**: Keep and upgrade (actively used by mr.verma)
- Made fully autonomous (no user intervention required)
- Fixed all integration gaps with mr.verma core
- Milvus now optional with graceful fallback
- All hardcoded paths now configurable via environment variables

### 🐳 Docker Improvements
- Reorganized Docker files into `docker/` directory
- Made Milvus dependencies optional with `required: false`
- Updated build contexts for proper path resolution
- Added comprehensive Docker documentation

### 🔒 Security
- Removed exposed API key from git history
- Updated security best practices in documentation
- Added proper .gitignore for sensitive files

## [5.0.0] - 2026-02-16

### 🎉 Major Release - Agent Lightning Integration

### ✨ Added
- Agent Lightning Local subsystem for autonomous operation
- Milvus vector database integration
- Docker Compose configuration for full stack
- Training loop for continuous learning
- Reward engine for feedback processing
- SFT trainer for model fine-tuning
- Vector services for embeddings

### 🏗️ Changed
- Refactored unified interface with mode support
- Enhanced agent orchestration system
- Improved memory service with vector storage
- Updated requirements with new dependencies

## [4.0.0] - 2026-02-14

### ✨ Added
- Enhanced agent system with 27 agents
- Ultimate mode with 82 system prompts
- Plugin orchestrator system
- MCP hub integration
- Thermal governor for resource management

## [3.0.0] - 2026-02-12

### ✨ Added
- Multi-agent orchestration
- Workflow automation
- Document generation capabilities
- Code generation improvements

## [2.0.0] - 2026-02-10

### ✨ Added
- Docker support
- NVIDIA API integration
- Secondary AI engine
- Vision capabilities

## [1.0.0] - 2026-02-08

### 🎉 Initial Release

### ✨ Features
- Basic chat interface
- Code analysis
- Simple agent system
- File processing
- CLI interface

---

## Release Notes Format

### Categories
- 🎉 Major release
- ✨ Added - New features
- 🐛 Fixed - Bug fixes
- 🏗️ Changed - Changes in existing functionality
- 🗑️ Removed - Removed features
- 🔒 Security - Security improvements
- 📚 Documentation - Documentation updates
- 🧪 Tests - Test-related changes

### Version Numbering
- **MAJOR**: Incompatible API changes
- **MINOR**: Added functionality (backward compatible)
- **PATCH**: Bug fixes (backward compatible)
