# PBT Test Suite

Comprehensive test suite for the Prompt Build Tool (PBT) CLI.

## Test Structure

```
tests/
├── unit/                      # Unit tests for individual components
│   ├── test_convert_command.py    # Tests for pbt convert
│   ├── test_test_command.py       # Tests for pbt test
│   ├── test_validate_command.py   # Tests for pbt validate
│   ├── test_generate_command.py   # Tests for pbt generate
│   └── test_compare_command.py    # Tests for pbt compare
├── integration/               # Integration tests
│   └── test_end_to_end.py        # End-to-end workflows
├── fixtures/                  # Test data and fixtures
├── conftest.py               # Pytest configuration and shared fixtures
├── mocks.py                  # Mock classes for testing
└── test_example.py           # Example tests to verify setup

```

## Running Tests

### Install Test Dependencies

```bash
pip install -r requirements-test.txt
```

### Run All Tests

```bash
# Simple run
pytest

# With coverage
pytest --cov=pbt --cov-report=html

# Using the test runner script
python run_tests.py
```

### Run Specific Test Categories

```bash
# Unit tests only
pytest tests/unit/
# or
python run_tests.py --unit

# Integration tests only
pytest tests/integration/
# or
python run_tests.py --integration

# Specific test file
pytest tests/unit/test_convert_command.py

# Specific test by name pattern
pytest -k "test_convert"
# or
python run_tests.py --specific test_convert
```

### Test Options

```bash
# Verbose output
pytest -v

# Stop on first failure
pytest -x

# Run tests in parallel
pytest -n auto

# Generate coverage report
pytest --cov=pbt --cov-report=html --cov-report=term
```

## Test Coverage

The test suite aims for >80% code coverage. After running tests with coverage:

- Terminal report: Shows coverage summary in console
- HTML report: Open `htmlcov/index.html` in browser
- XML report: `coverage.xml` for CI/CD integration

## Writing Tests

### Unit Tests

Unit tests focus on individual functions and classes:

```python
def test_convert_single_file(cli_runner, sample_python_agent, temp_dir):
    """Test converting a single Python agent file"""
    result = cli_runner.invoke(app, ["convert", str(sample_python_agent)])
    
    assert result.exit_code == 0
    assert "Successfully converted" in result.output
```

### Integration Tests

Integration tests verify complete workflows:

```python
def test_generate_and_test_workflow(cli_runner):
    """Test generating a prompt and then testing it"""
    # Generate prompt
    result = cli_runner.invoke(app, ["generate", "--goal", "Test"])
    assert result.exit_code == 0
    
    # Test the generated prompt
    result = cli_runner.invoke(app, ["test", "test.yaml"])
    assert result.exit_code == 0
```

### Using Fixtures

Common fixtures are available in `conftest.py`:

- `temp_dir`: Temporary directory for test files
- `sample_prompt_yaml`: Sample prompt YAML file
- `sample_test_yaml`: Sample test YAML file
- `sample_jsonl_tests`: Sample JSONL test file
- `sample_python_agent`: Sample Python agent file
- `cli_runner`: Typer CLI test runner

### Mocking

The test suite uses mocks for external dependencies:

```python
@patch('pbt.cli.main.PromptGenerator')
def test_generate_command(mock_generator_class):
    mock_generator = Mock()
    mock_generator_class.return_value = mock_generator
    mock_generator.generate.return_value = {...}
```

## Test Categories

Tests are marked with pytest markers:

- `@pytest.mark.unit`: Unit tests
- `@pytest.mark.integration`: Integration tests
- `@pytest.mark.slow`: Slow running tests
- `@pytest.mark.requires_api`: Tests requiring API keys
- `@pytest.mark.cli`: CLI command tests

## Continuous Integration

The test suite is designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Run tests
  run: |
    pip install -r requirements-test.txt
    pytest --cov=pbt --cov-report=xml
    
- name: Upload coverage
  uses: codecov/codecov-action@v3
```

## Troubleshooting

### Import Errors

If you get import errors, ensure:
1. PBT is installed: `pip install -e .`
2. Test dependencies installed: `pip install -r requirements-test.txt`
3. Running from project root directory

### Mock Issues

The test suite automatically mocks missing dependencies. If a test fails due to missing imports, check `tests/mocks.py` and `conftest.py`.

### Fixture Issues

If fixtures aren't found, ensure you're using pytest (not unittest) and that conftest.py is in the tests directory.