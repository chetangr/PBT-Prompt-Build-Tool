# Contributing to PBT (Prompt Build Tool)

Thank you for your interest in contributing to PBT! This guide will help you get started.

## 🚀 Quick Start

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/PBT-Prompt-Build-Tool.git
   cd PBT-Prompt-Build-Tool
   ```
3. **Install in development mode**:
   ```bash
   pip install -e .
   ```
4. **Set up API keys**:
   ```bash
   cp .env.example .env
   # Add your API keys to .env
   ```

## 🛠️ Development Setup

### Prerequisites
- Python 3.8+
- Git
- API keys for LLM providers (optional for some contributions)

### Installation
```bash
# Clone the repo
git clone https://github.com/saicgr/PBT-Prompt-Build-Tool.git
cd PBT-Prompt-Build-Tool

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Run tests
python -m pytest tests/
```

## 📝 How to Contribute

### 1. **Bug Reports**
- Use GitHub Issues
- Include steps to reproduce
- Provide error messages and logs
- Mention your Python version and OS

### 2. **Feature Requests**
- Open an issue first to discuss
- Describe the use case
- Provide examples if possible

### 3. **Code Contributions**

#### Pull Request Process
1. **Create a branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**:
   - Follow the coding style
   - Add tests for new features
   - Update documentation

3. **Test your changes**:
   ```bash
   # Run tests
   python -m pytest tests/

   # Run linting
   black pbt/
   isort pbt/

   # Test CLI commands
   pbt --help
   ```

4. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Add: your feature description"
   ```

5. **Push and create PR**:
   ```bash
   git push origin feature/your-feature-name
   ```
   Then open a PR on GitHub.

## 🧪 Testing

### Running Tests
```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_example.py

# Run with coverage
python -m pytest --cov=pbt tests/
```

### Adding Tests
- Place tests in the `tests/` directory
- Use descriptive test names
- Include both positive and negative test cases
- Mock external API calls

### Test Structure
```python
def test_feature_name():
    """Test description"""
    # Arrange
    input_data = "test input"
    
    # Act
    result = your_function(input_data)
    
    # Assert
    assert result == expected_output
```

## 📚 Documentation

### Code Documentation
- Use docstrings for all functions and classes
- Follow Google/NumPy docstring format
- Include examples in docstrings

### User Documentation
- Update README.md for user-facing changes
- Add examples for new features
- Update command help text

## 🎨 Code Style

### Python Style
- Follow PEP 8
- Use Black for formatting: `black pbt/`
- Use isort for imports: `isort pbt/`
- Line length: 100 characters

### Naming Conventions
- Functions: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Files: `snake_case.py`

### Example
```python
class PromptGenerator:
    """Generates prompts using AI models."""
    
    def generate_prompt(self, goal: str, variables: List[str]) -> Dict[str, Any]:
        """Generate a prompt from a goal.
        
        Args:
            goal: The goal or purpose of the prompt
            variables: List of variables the prompt should accept
            
        Returns:
            Dictionary containing the generated prompt
            
        Example:
            >>> generator = PromptGenerator()
            >>> result = generator.generate_prompt("Summarize text", ["text"])
            >>> result['success']
            True
        """
        # Implementation here
        pass
```

## 🚀 Project Structure

```
pbt/
├── cli/                 # CLI commands
│   ├── main.py         # Main CLI entry point
│   ├── commands/       # Command modules
│   └── utils.py        # CLI utilities
├── core/               # Core functionality
│   ├── project.py      # Project management
│   ├── prompt_*.py     # Prompt operations
│   └── converter.py    # Code conversion
├── integrations/       # External integrations
│   ├── llm/           # LLM providers
│   ├── database/      # Database connections
│   └── deployment/    # Deployment targets
└── web/               # Web UI
    ├── app.py         # FastAPI application
    └── static/        # Static assets
```

## 🎯 Contribution Ideas

### Good First Issues
- Add new CLI command aliases
- Improve error messages
- Add more test cases
- Update documentation
- Fix typos

### Medium Complexity
- Add new LLM provider integration
- Implement new optimization strategies
- Add export formats
- Improve web UI

### Advanced
- Add new evaluation metrics
- Implement caching layer
- Add deployment integrations
- Performance optimizations

## 🤝 Community Guidelines

### Be Respectful
- Use inclusive language
- Be patient with newcomers
- Provide constructive feedback
- Help others learn

### Communication
- GitHub Issues for bugs and features
- Discussions for questions and ideas
- Keep conversations on-topic

## 📋 Checklist for Contributors

Before submitting a PR:

- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] Commit messages are clear
- [ ] PR description explains the changes
- [ ] No merge conflicts

## 🏷️ Release Process

1. Version bump in `pbt/__version__.py`
2. Update CHANGELOG.md
3. Create release PR
4. Tag release after merge
5. Upload to PyPI

## 📞 Getting Help

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: Questions and general discussion
- **Email**: For private matters

## 🙏 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Special mentions for significant contributions

Thank you for contributing to PBT! 🚀