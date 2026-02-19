# Contributing to MR.VERMA

First off, thank you for considering contributing to MR.VERMA! It's people like you that make this project a great tool for the community.

## 🎯 Ways to Contribute

- 🐛 **Report bugs** - Open an issue with the bug label
- 💡 **Suggest features** - Open an issue with the enhancement label  
- 📝 **Improve documentation** - Fix typos, add examples, clarify instructions
- 🔧 **Submit code** - Fix bugs or implement new features
- 🧪 **Add tests** - Improve test coverage
- 🎨 **Create visuals** - Diagrams, infographics, logos

## 🚀 Getting Started

### Setting Up Development Environment

1. **Fork and clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/AI-MR.VERMA.git
cd AI-MR.VERMA
```

2. **Create a virtual environment**
```bash
python -m venv venv

# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate
```

3. **Install development dependencies**
```bash
pip install -r requirements.unified.txt
pip install -e .[dev]  # Install in editable mode with dev extras
```

4. **Set up pre-commit hooks**
```bash
pre-commit install
```

5. **Run tests to ensure everything works**
```bash
pytest tests/
```

## 📝 Development Guidelines

### Code Style

We follow PEP 8 with some modifications:
- Line length: 88 characters (Black default)
- Use type hints where possible
- Docstrings for all public functions/classes

```python
# Example function
def process_data(input_data: str, threshold: float = 0.5) -> dict:
    """
    Process input data with given threshold.
    
    Args:
        input_data: Raw input string to process
        threshold: Minimum confidence threshold (default: 0.5)
        
    Returns:
        Dictionary containing processed results
        
    Raises:
        ValueError: If input_data is empty
    """
    if not input_data:
        raise ValueError("Input data cannot be empty")
    
    # Process logic here
    return {"result": "processed", "confidence": threshold}
```

### Commit Message Format

We use conventional commits:

```
type(scope): subject

body (optional)

footer (optional)
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style (formatting, semicolons, etc)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Build process or auxiliary tool changes

**Examples:**
```
feat(agents): add new security scanning agent

fix(core): resolve memory leak in orchestrator
docs(readme): update installation instructions
```

### Branch Naming

- `feature/description` - New features
- `bugfix/description` - Bug fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=core --cov=agents --cov-report=html

# Run specific test file
pytest tests/test_orchestrator.py -v

# Run with specific marker
pytest -m "integration"
```

### Writing Tests

```python
# Example test
import pytest
from core.orchestrator import SupremeOrchestrator

class TestOrchestrator:
    """Test suite for SupremeOrchestrator."""
    
    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator instance for testing."""
        return SupremeOrchestrator()
    
    def test_orchestrator_initialization(self, orchestrator):
        """Test that orchestrator initializes correctly."""
        assert orchestrator is not None
        assert orchestrator.agents == {}
    
    @pytest.mark.asyncio
    async def test_agent_registration(self, orchestrator):
        """Test agent registration."""
        agent = MockAgent("test_agent")
        await orchestrator.register_agent(agent)
        assert "test_agent" in orchestrator.agents
```

## 📊 Code Quality

We use several tools to maintain code quality:

### Linting and Formatting

```bash
# Run all quality checks
make check

# Or individually:
black .                    # Format code
isort .                    # Sort imports
ruff check .               # Lint code
mypy core/ agents/         # Type checking
```

### Pre-commit Hooks

The following checks run automatically on commit:
- Trailing whitespace removal
- End-of-file fixer
- YAML/JSON validation
- Black formatting
- Ruff linting

## 🎨 Adding Visuals

When contributing visual content:

### Diagrams
- Use Mermaid for flowcharts in markdown
- Use ASCII art for simple diagrams
- Use SVG for complex diagrams
- Keep diagrams in `docs/diagrams/`

### Images
- Optimize images before committing
- Use WebP or optimized PNG/JPEG
- Place in `docs/assets/images/`
- Include alt text for accessibility

## 🔒 Security

- Never commit API keys or secrets
- Use environment variables for sensitive data
- Report security vulnerabilities privately
- Follow security best practices in code

## 📝 Documentation

- Update README.md if adding major features
- Add docstrings to all public APIs
- Update CHANGELOG.md with your changes
- Include examples for new features

## 🐛 Reporting Bugs

When reporting bugs, please include:

1. **Clear description** - What happened vs what you expected
2. **Steps to reproduce** - Minimal steps to trigger the bug
3. **Environment** - OS, Python version, dependencies
4. **Logs** - Relevant error messages or stack traces
5. **Screenshots** - If applicable

Template:
```markdown
**Description**
Brief description of the bug

**To Reproduce**
1. Go to '...'
2. Click on '...'
3. See error

**Expected Behavior**
What you expected to happen

**Environment:**
- OS: [e.g., Windows 10]
- Python: [e.g., 3.11.0]
- Version: [e.g., 6.0]

**Logs**
```
Paste error logs here
```
```

## 💡 Suggesting Features

When suggesting features:

1. Check if already requested in issues
2. Describe the use case clearly
3. Explain why it would be useful
4. Consider implementation approach
5. Be open to discussion

## 🏆 Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in documentation

## 📜 Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to:

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Respect different viewpoints
- Prioritize community welfare

## ❓ Questions?

- 💬 [GitHub Discussions](https://github.com/abhikkv92-create/AI-MR.VERMA/discussions)
- 🐛 [GitHub Issues](https://github.com/abhikkv92-create/AI-MR.VERMA/issues)
- 📧 Contact maintainers through GitHub

---

Thank you for contributing to MR.VERMA! 🚀
