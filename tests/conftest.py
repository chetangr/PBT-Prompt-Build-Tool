"""Pytest configuration and shared fixtures for PBT tests"""

import pytest
import tempfile
import shutil
from pathlib import Path
import yaml
import json
import os
import sys
from unittest.mock import Mock, patch

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import mocks
from tests.mocks import (
    MockPromptGenerator, MockPromptEvaluator, MockPBTProject,
    MockPromptDAG, MockSnapshotManager, MockProfileManager,
    MockRunResultsManager, MockManifest, RunStatus,
    MockComprehensiveEvaluator, EvaluationAspect, AspectScore, TestResult
)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files"""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path)


@pytest.fixture
def sample_prompt_yaml(temp_dir):
    """Create a sample prompt YAML file"""
    prompt_data = {
        'name': 'Test Summarizer',
        'version': '1.0',
        'model': 'gpt-4',
        'template': 'Summarize the following text: {text}',
        'variables': {
            'text': {
                'type': 'string',
                'description': 'Text to summarize'
            }
        }
    }
    
    prompt_file = temp_dir / "test_summarizer.prompt.yaml"
    with open(prompt_file, 'w') as f:
        yaml.dump(prompt_data, f)
    
    return prompt_file


@pytest.fixture
def sample_test_yaml(temp_dir):
    """Create a sample test YAML file"""
    test_data = {
        'prompt_file': 'test_summarizer.prompt.yaml',
        'tests': [
            {
                'name': 'test_short_summary',
                'inputs': {
                    'text': 'This is a long text that needs to be summarized.'
                },
                'expected_keywords': ['summary', 'text'],
                'min_score': 7
            },
            {
                'name': 'test_empty_input',
                'inputs': {
                    'text': ''
                },
                'expected_keywords': [],
                'min_score': 5
            }
        ]
    }
    
    test_file = temp_dir / "test_summarizer.test.yaml"
    with open(test_file, 'w') as f:
        yaml.dump(test_data, f)
    
    return test_file


@pytest.fixture
def sample_jsonl_tests(temp_dir):
    """Create a sample JSONL test file"""
    tests = [
        {
            "test_name": "basic_summary",
            "inputs": {"text": "This is a test"},
            "expected_keywords": ["test"],
            "quality_criteria": "Should provide a concise summary"
        },
        {
            "test_name": "long_text",
            "inputs": {"text": "This is a much longer text with multiple sentences. It contains various topics and ideas."},
            "expected_keywords": ["longer", "multiple"],
            "quality_criteria": "Should capture main points"
        }
    ]
    
    jsonl_file = temp_dir / "test_cases.jsonl"
    with open(jsonl_file, 'w') as f:
        for test in tests:
            f.write(json.dumps(test) + '\n')
    
    return jsonl_file


@pytest.fixture
def sample_python_agent(temp_dir):
    """Create a sample Python agent file"""
    agent_code = '''
import openai

def summarizer_agent(text, model="gpt-4"):
    """Summarize text using GPT-4"""
    prompt = f"Summarize the following text: {text}"
    
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.choices[0].message['content']

def critic_agent(content):
    """Critique content"""
    prompt = f"Provide constructive criticism for: {content}"
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful critic"},
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.choices[0].message['content']
'''
    
    agent_file = temp_dir / "test_agents.py"
    with open(agent_file, 'w') as f:
        f.write(agent_code)
    
    return agent_file


@pytest.fixture
def mock_llm_response():
    """Mock LLM API responses"""
    def _mock_response(content="This is a mock response"):
        return {
            "choices": [{
                "message": {
                    "content": content
                }
            }]
        }
    return _mock_response


@pytest.fixture
def mock_anthropic_client():
    """Mock Anthropic client"""
    mock_client = Mock()
    mock_client.messages.create.return_value = Mock(
        content=[Mock(text="Mock Claude response")]
    )
    return mock_client


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client"""
    mock_client = Mock()
    mock_client.chat.completions.create.return_value = Mock(
        choices=[Mock(message=Mock(content="Mock GPT response"))]
    )
    return mock_client


@pytest.fixture(autouse=True)
def setup_env(monkeypatch):
    """Set up test environment variables"""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-anthropic-key")
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
    monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
    monkeypatch.setenv("SUPABASE_ANON_KEY", "test-supabase-key")


@pytest.fixture
def cli_runner():
    """Create a CLI test runner"""
    from typer.testing import CliRunner
    return CliRunner()


@pytest.fixture(autouse=True)
def mock_missing_imports(monkeypatch):
    """Mock missing import dependencies"""
    # Mock PromptGenerator
    monkeypatch.setattr('pbt.cli.main.PromptGenerator', MockPromptGenerator)
    
    # Mock PromptEvaluator
    monkeypatch.setattr('pbt.cli.main.PromptEvaluator', MockPromptEvaluator)
    
    # Mock PBTProject
    monkeypatch.setattr('pbt.cli.main.PBTProject', MockPBTProject)
    
    # Mock other classes
    monkeypatch.setattr('pbt.cli.main.PromptDAG', MockPromptDAG)
    monkeypatch.setattr('pbt.cli.main.SnapshotManager', MockSnapshotManager)
    monkeypatch.setattr('pbt.cli.main.ProfileManager', MockProfileManager)
    monkeypatch.setattr('pbt.cli.main.RunResultsManager', MockRunResultsManager)
    monkeypatch.setattr('pbt.cli.main.Manifest', MockManifest)
    monkeypatch.setattr('pbt.cli.main.RunStatus', RunStatus)
    
    # Mock comprehensive evaluator
    monkeypatch.setattr('pbt.cli.main.ComprehensiveEvaluator', MockComprehensiveEvaluator)
    monkeypatch.setattr('pbt.cli.main.EvaluationAspect', EvaluationAspect)


@pytest.fixture
def project_structure(temp_dir):
    """Create a complete project structure"""
    # Create directories
    (temp_dir / "agents").mkdir()
    (temp_dir / "tests").mkdir()
    (temp_dir / "prompts").mkdir()
    (temp_dir / "evaluations").mkdir()
    
    # Create pbt.yaml
    config = {
        'name': 'test-project',
        'version': '1.0.0',
        'prompts_dir': 'prompts',
        'tests_dir': 'tests',
        'models': {
            'default': 'gpt-4',
            'available': ['gpt-4', 'claude-3', 'gpt-3.5-turbo']
        }
    }
    
    with open(temp_dir / "pbt.yaml", 'w') as f:
        yaml.dump(config, f)
    
    # Create .env.example
    with open(temp_dir / ".env.example", 'w') as f:
        f.write("ANTHROPIC_API_KEY=your-key-here\n")
        f.write("OPENAI_API_KEY=your-key-here\n")
    
    return temp_dir