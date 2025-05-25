"""Unit tests for the pbt generate command"""

import pytest
from pathlib import Path
import yaml
import json
import os
from unittest.mock import patch, Mock
from typer.testing import CliRunner

from pbt.cli.main import app


class TestGenerateCommand:
    """Test the generate command functionality"""
    
    @patch('pbt.cli.main.PromptGenerator')
    def test_generate_basic_prompt(self, mock_generator_class, cli_runner, temp_dir):
        """Test basic prompt generation"""
        # Set up mock
        mock_generator = Mock()
        mock_generator_class.return_value = mock_generator
        
        mock_generator.generate.return_value = {
            'success': True,
            'prompt_yaml': {
                'name': 'customer-feedback-summarizer',
                'version': '1.0',
                'model': 'claude',
                'template': 'Summarize this feedback: {feedback_text}',
                'variables': {
                    'feedback_text': {'type': 'string'}
                }
            }
        }
        
        mock_generator.generate_jsonl_tests.return_value = {
            'success': True,
            'test_cases': [
                {'test_name': 'test1', 'inputs': {'feedback_text': 'Great product!'}}
            ]
        }
        
        mock_generator.save_jsonl_tests.return_value = True
        
        # Change to temp dir
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            result = cli_runner.invoke(app, [
                "generate",
                "--goal", "Summarize customer feedback"
            ])
            
            assert result.exit_code == 0
            assert "Generating prompt for: Summarize customer feedback" in result.output
            assert "Generated prompt saved to" in result.output
            assert "Generated 1 test cases" in result.output
            
            # Check files created
            yaml_files = list(temp_dir.glob("*.yaml"))
            assert len(yaml_files) == 1
            
            test_files = list((temp_dir / "tests").glob("*.jsonl"))
            assert len(test_files) == 1
        
        finally:
            os.chdir(original_cwd)
    
    @patch('pbt.cli.main.PromptGenerator')
    def test_generate_with_options(self, mock_generator_class, cli_runner, temp_dir):
        """Test generation with various options"""
        # Set up mock
        mock_generator = Mock()
        mock_generator_class.return_value = mock_generator
        
        mock_generator.generate.return_value = {
            'success': True,
            'prompt_yaml': {
                'name': 'translator',
                'version': '1.0',
                'model': 'gpt-4',
                'template': 'Translate {text} to {language}',
                'variables': {
                    'text': {'type': 'string'},
                    'language': {'type': 'string'}
                }
            }
        }
        
        result = cli_runner.invoke(app, [
            "generate",
            "--goal", "Translate text",
            "--model", "gpt-4",
            "--style", "concise",
            "--variables", "text,language",
            "--output", str(temp_dir / "translator.yaml"),
            "--no-tests"
        ])
        
        assert result.exit_code == 0
        
        # Verify generator was called with correct params
        mock_generator.generate.assert_called_once()
        call_args = mock_generator.generate.call_args[1]
        assert call_args['goal'] == "Translate text"
        assert call_args['model'] == "gpt-4"
        assert call_args['style'] == "concise"
        assert call_args['variables'] == ['text', 'language']
        
        # Verify no test generation
        mock_generator.generate_jsonl_tests.assert_not_called()
    
    @patch('pbt.cli.main.PromptGenerator')
    def test_generate_failed(self, mock_generator_class, cli_runner):
        """Test handling generation failure"""
        # Set up mock
        mock_generator = Mock()
        mock_generator_class.return_value = mock_generator
        
        mock_generator.generate.return_value = {
            'success': False,
            'raw_content': 'Error: API key invalid'
        }
        
        result = cli_runner.invoke(app, [
            "generate",
            "--goal", "Test goal"
        ])
        
        assert result.exit_code == 1
        assert "Generated raw content:" in result.output
        assert "Error: API key invalid" in result.output
    
    @patch('pbt.cli.main.PromptGenerator')
    def test_generate_with_num_tests(self, mock_generator_class, cli_runner, temp_dir):
        """Test generating specific number of tests"""
        # Set up mock
        mock_generator = Mock()
        mock_generator_class.return_value = mock_generator
        
        mock_generator.generate.return_value = {
            'success': True,
            'prompt_yaml': {
                'name': 'test-prompt',
                'template': 'Test {input}'
            }
        }
        
        test_cases = [
            {'test_name': f'test{i}', 'inputs': {'input': f'value{i}'}}
            for i in range(10)
        ]
        
        mock_generator.generate_jsonl_tests.return_value = {
            'success': True,
            'test_cases': test_cases
        }
        
        mock_generator.save_jsonl_tests.return_value = True
        
        # Change to temp dir
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            result = cli_runner.invoke(app, [
                "generate",
                "--goal", "Test",
                "--num-tests", "10"
            ])
            
            assert result.exit_code == 0
            assert "Generated 10 test cases" in result.output
            
            # Verify correct number of tests requested
            mock_generator.generate_jsonl_tests.assert_called_once()
            call_args = mock_generator.generate_jsonl_tests.call_args[0]
            assert call_args[1] == 10  # num_tests argument
        
        finally:
            os.chdir(original_cwd)


class TestGenTestsCommand:
    """Test the gentests command functionality"""
    
    @patch('pbt.cli.main.PromptGenerator')
    def test_gentests_basic(self, mock_generator_class, cli_runner, sample_prompt_yaml, temp_dir):
        """Test basic test generation for existing prompt"""
        # Set up mock
        mock_generator = Mock()
        mock_generator_class.return_value = mock_generator
        
        mock_generator.generate_jsonl_tests.return_value = {
            'success': True,
            'test_cases': [
                {'test_name': 'test1', 'inputs': {'text': 'test'}},
                {'test_name': 'test2', 'inputs': {'text': 'another test'}}
            ]
        }
        
        mock_generator.save_jsonl_tests.return_value = True
        
        # Change to temp dir
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            result = cli_runner.invoke(app, [
                "gentests",
                str(sample_prompt_yaml)
            ])
            
            assert result.exit_code == 0
            assert "Generating test cases for" in result.output
            assert "Generated 2 test cases" in result.output
            assert "tests/test_summarizer.test.jsonl" in result.output
        
        finally:
            os.chdir(original_cwd)
    
    @patch('pbt.cli.main.PromptGenerator')
    def test_gentests_custom_output(self, mock_generator_class, cli_runner, sample_prompt_yaml, temp_dir):
        """Test test generation with custom output path"""
        # Set up mock
        mock_generator = Mock()
        mock_generator_class.return_value = mock_generator
        
        mock_generator.generate_jsonl_tests.return_value = {
            'success': True,
            'test_cases': [{'test_name': 'test1'}]
        }
        
        mock_generator.save_jsonl_tests.return_value = True
        
        custom_output = temp_dir / "custom_tests.jsonl"
        
        result = cli_runner.invoke(app, [
            "gentests",
            str(sample_prompt_yaml),
            "--output", str(custom_output),
            "--num-tests", "3"
        ])
        
        assert result.exit_code == 0
        
        # Verify save was called with custom path
        mock_generator.save_jsonl_tests.assert_called_once()
        call_args = mock_generator.save_jsonl_tests.call_args[0]
        assert call_args[1] == str(custom_output)
    
    def test_gentests_file_not_found(self, cli_runner):
        """Test handling missing prompt file"""
        result = cli_runner.invoke(app, [
            "gentests",
            "nonexistent.yaml"
        ])
        
        assert result.exit_code == 1
        assert "Prompt file not found" in result.output
    
    @patch('pbt.cli.main.PromptGenerator')
    def test_gentests_overwrite_protection(self, mock_generator_class, cli_runner, sample_prompt_yaml, temp_dir):
        """Test overwrite protection for existing test files"""
        # Create existing test file
        (temp_dir / "tests").mkdir()
        existing_test = temp_dir / "tests" / "test_summarizer.test.jsonl"
        existing_test.write_text('{"existing": "test"}')
        
        # Change to temp dir
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            result = cli_runner.invoke(app, [
                "gentests",
                str(sample_prompt_yaml)
            ])
            
            assert result.exit_code == 1
            assert "Test file already exists" in result.output
            assert "Use --overwrite" in result.output
        
        finally:
            os.chdir(original_cwd)
    
    @patch('pbt.cli.main.PromptGenerator')
    def test_gentests_generation_failure(self, mock_generator_class, cli_runner, sample_prompt_yaml):
        """Test handling test generation failure"""
        # Set up mock
        mock_generator = Mock()
        mock_generator_class.return_value = mock_generator
        
        mock_generator.generate_jsonl_tests.return_value = {
            'success': False,
            'error': 'API rate limit exceeded',
            'raw_content': 'Rate limit error details'
        }
        
        result = cli_runner.invoke(app, [
            "gentests",
            str(sample_prompt_yaml)
        ])
        
        assert result.exit_code == 1
        assert "Failed to generate test cases" in result.output
        assert "API rate limit exceeded" in result.output