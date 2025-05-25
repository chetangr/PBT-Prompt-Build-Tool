"""Unit tests for the pbt convert command"""

import pytest
from pathlib import Path
import yaml
import os
from unittest.mock import patch, Mock
from typer.testing import CliRunner

from pbt.cli.main import app
from pbt.core.converter import convert_agent_file, PromptExtractor


class TestConvertCommand:
    """Test the convert command functionality"""
    
    def test_convert_single_file(self, cli_runner, sample_python_agent, temp_dir):
        """Test converting a single Python agent file"""
        # Change to temp directory
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            result = cli_runner.invoke(app, ["convert", str(sample_python_agent)])
            
            assert result.exit_code == 0
            assert "Successfully converted" in result.output
            assert "Prompts extracted: 2" in result.output
            
            # Check that YAML files were created
            agents_dir = temp_dir / "agents"
            assert agents_dir.exists()
            
            yaml_files = list(agents_dir.glob("*.yaml"))
            assert len(yaml_files) == 2
            
            # Check converted Python file
            converted_files = list(temp_dir.glob("*_converted.py"))
            assert len(converted_files) == 1
            
        finally:
            os.chdir(original_cwd)
    
    def test_convert_with_output_dir(self, cli_runner, sample_python_agent, temp_dir):
        """Test converting with custom output directory"""
        output_dir = temp_dir / "custom_output"
        
        result = cli_runner.invoke(app, [
            "convert", 
            str(sample_python_agent),
            "--output", str(output_dir)
        ])
        
        assert result.exit_code == 0
        assert output_dir.exists()
        
        yaml_files = list(output_dir.glob("*.yaml"))
        assert len(yaml_files) == 2
    
    def test_convert_batch_mode(self, cli_runner, temp_dir):
        """Test batch conversion of multiple files"""
        # Create multiple agent files
        for i in range(3):
            agent_code = f'''
def agent_{i}(text):
    """Agent {i}"""
    prompt = f"Process: {{text}}"
    return prompt
'''
            agent_file = temp_dir / f"agent_{i}.py"
            with open(agent_file, 'w') as f:
                f.write(agent_code)
        
        result = cli_runner.invoke(app, [
            "convert",
            str(temp_dir),
            "--batch",
            "--pattern", "agent_*.py"
        ])
        
        assert result.exit_code == 0
        assert "Files converted: 3" in result.output
        assert "Total prompts extracted: 3" in result.output
    
    def test_convert_no_agents_found(self, cli_runner, temp_dir):
        """Test converting file with no agents"""
        no_agent_file = temp_dir / "no_agents.py"
        with open(no_agent_file, 'w') as f:
            f.write("# Just a regular Python file\nprint('Hello')")
        
        result = cli_runner.invoke(app, ["convert", str(no_agent_file)])
        
        assert result.exit_code == 0
        assert "Prompts extracted: 0" in result.output
    
    def test_convert_file_not_found(self, cli_runner):
        """Test converting non-existent file"""
        result = cli_runner.invoke(app, ["convert", "nonexistent.py"])
        
        assert result.exit_code == 1
        assert "File not found" in result.output


class TestPromptExtractor:
    """Test the PromptExtractor class"""
    
    def test_extract_simple_prompt(self, temp_dir):
        """Test extracting a simple prompt"""
        code = '''
def simple_agent(text):
    prompt = f"Process this: {text}"
    return call_llm(prompt)
'''
        
        file_path = temp_dir / "simple.py"
        with open(file_path, 'w') as f:
            f.write(code)
        
        extractor = PromptExtractor(str(file_path))
        prompts = extractor.extract()
        
        assert len(prompts) == 1
        assert prompts[0]['name'] == 'Simple'
        assert prompts[0]['template'] == 'Process this: {text}'
        assert prompts[0]['variables'] == ['text']
    
    def test_extract_multiple_prompts(self, temp_dir):
        """Test extracting multiple prompts from one file"""
        code = '''
def summarizer_agent(content):
    prompt = f"Summarize: {content}"
    return llm(prompt)

def translator_agent(text, language):
    prompt = f"Translate {text} to {language}"
    return llm(prompt)
'''
        
        file_path = temp_dir / "multi.py"
        with open(file_path, 'w') as f:
            f.write(code)
        
        extractor = PromptExtractor(str(file_path))
        prompts = extractor.extract()
        
        assert len(prompts) == 2
        assert prompts[0]['name'] == 'Summarizer'
        assert prompts[1]['name'] == 'Translator'
        assert prompts[1]['variables'] == ['text', 'language']
    
    def test_extract_with_model_detection(self, temp_dir):
        """Test model detection in prompts"""
        code = '''
def gpt_agent(text):
    prompt = f"Process: {text}"
    model = "gpt-4"
    return openai.chat(model=model, prompt=prompt)

def claude_agent(text):
    prompt = f"Process: {text}"
    return anthropic.claude.complete(prompt)
'''
        
        file_path = temp_dir / "models.py"
        with open(file_path, 'w') as f:
            f.write(code)
        
        extractor = PromptExtractor(str(file_path))
        prompts = extractor.extract()
        
        assert len(prompts) == 2
        assert prompts[0]['model'] == 'gpt-4'
        assert prompts[1]['model'] == 'claude-3'
    
    def test_extract_complex_prompt_patterns(self, temp_dir):
        """Test extracting various prompt patterns"""
        code = '''
def agent1(data):
    message = f"Analyze this data: {data}"
    return llm(message)

def agent2(content):
    messages = [
        {"role": "user", "content": f"Review: {content}"}
    ]
    return llm(messages)

def agent3(text):
    content = f"""
    Please process the following:
    {text}
    
    Provide detailed analysis.
    """
    return llm(content)
'''
        
        file_path = temp_dir / "patterns.py"
        with open(file_path, 'w') as f:
            f.write(code)
        
        extractor = PromptExtractor(str(file_path))
        prompts = extractor.extract()
        
        assert len(prompts) == 3
        assert all(p['template'] for p in prompts)
        assert all(p['variables'] for p in prompts)


class TestConvertAgentFile:
    """Test the convert_agent_file function"""
    
    def test_convert_creates_yaml_files(self, sample_python_agent, temp_dir):
        """Test that conversion creates proper YAML files"""
        result = convert_agent_file(str(sample_python_agent), str(temp_dir / "output"))
        
        assert result['prompts_extracted'] == 2
        assert len(result['yaml_files']) == 2
        assert result['python_file'] is not None
        
        # Check YAML content
        for yaml_file in result['yaml_files']:
            assert Path(yaml_file).exists()
            with open(yaml_file, 'r') as f:
                data = yaml.safe_load(f)
                assert 'name' in data
                assert 'version' in data
                assert 'model' in data
                assert 'template' in data
    
    def test_convert_creates_runtime_file(self, sample_python_agent, temp_dir):
        """Test that conversion creates proper runtime Python file"""
        result = convert_agent_file(str(sample_python_agent), str(temp_dir / "output"))
        
        python_file = Path(result['python_file'])
        assert python_file.exists()
        
        with open(python_file, 'r') as f:
            content = f.read()
            assert 'from pbt.runtime import PromptRunner' in content
            assert 'PromptRunner(' in content
            assert 'def summarizer_agent(' in content
            assert 'def critic_agent(' in content
    
    def test_convert_preserves_function_signatures(self, temp_dir):
        """Test that converted functions preserve original signatures"""
        code = '''
def complex_agent(text, max_length=100, temperature=0.7, **kwargs):
    """Complex agent with multiple parameters"""
    prompt = f"Process {text} with length {max_length}"
    return llm(prompt)
'''
        
        file_path = temp_dir / "complex.py"
        with open(file_path, 'w') as f:
            f.write(code)
        
        result = convert_agent_file(str(file_path), str(temp_dir / "output"))
        
        with open(result['python_file'], 'r') as f:
            content = f.read()
            assert 'def complex_agent(text, max_length=100, temperature=0.7, **kwargs):' in content