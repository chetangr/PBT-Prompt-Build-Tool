"""Unit tests for the pbt test command"""

import pytest
from pathlib import Path
import yaml
import json
import os
from unittest.mock import patch, Mock, MagicMock
from typer.testing import CliRunner

from pbt.cli.main import app


class TestTestCommand:
    """Test the test command functionality"""
    
    @patch('pbt.cli.main.PromptEvaluator')
    def test_run_test_file(self, mock_evaluator_class, cli_runner, sample_prompt_yaml, sample_test_yaml, temp_dir):
        """Test running a specific test file"""
        # Set up mock
        mock_evaluator = Mock()
        mock_evaluator_class.return_value = mock_evaluator
        mock_evaluator.test_agent_with_file.return_value = {
            'summary': {
                'total': 2,
                'passed': 2,
                'failed': 0,
                'pass_rate': 1.0
            },
            'results': [
                {'test_name': 'test1', 'passed': True, 'score': 8},
                {'test_name': 'test2', 'passed': True, 'score': 9}
            ]
        }
        
        result = cli_runner.invoke(app, ["test", str(sample_test_yaml)])
        
        assert result.exit_code == 0
        assert "Running test file" in result.output
        assert "Test Results" in result.output
        assert "2/2" in result.output  # All tests passed
        assert "100.0%" in result.output  # Pass rate
    
    @patch('pbt.cli.main.PromptEvaluator')
    def test_auto_generate_tests(self, mock_evaluator_class, cli_runner, sample_prompt_yaml):
        """Test auto-generating tests for a prompt file"""
        # Set up mock
        mock_evaluator = Mock()
        mock_evaluator_class.return_value = mock_evaluator
        
        mock_evaluator.generate_tests.return_value = {
            'success': True,
            'tests': [
                {'name': 'auto_test_1', 'inputs': {'text': 'test'}, 'expected': 'summary'},
                {'name': 'auto_test_2', 'inputs': {'text': 'another'}, 'expected': 'summary'}
            ]
        }
        
        mock_evaluator.run_tests.return_value = {
            'summary': {
                'total': 2,
                'passed': 1,
                'failed': 1,
                'pass_rate': 0.5
            },
            'results': [
                {'test_name': 'auto_test_1', 'passed': True, 'score': 8},
                {'test_name': 'auto_test_2', 'passed': False, 'score': 3}
            ]
        }
        
        result = cli_runner.invoke(app, [
            "test", 
            str(sample_prompt_yaml),
            "--num-tests", "2"
        ])
        
        assert result.exit_code == 0
        assert "Auto-generating" in result.output
        assert "Test Results" in result.output
        assert "1/2" in result.output  # 1 passed
        assert "50.0%" in result.output  # Pass rate
    
    @patch('pbt.cli.main.find_prompt_file')
    @patch('pbt.cli.main.PromptEvaluator')
    def test_auto_locate_file(self, mock_evaluator_class, mock_find_file, cli_runner, sample_prompt_yaml):
        """Test auto-locating prompt files"""
        # Set up mocks
        mock_find_file.return_value = sample_prompt_yaml
        
        mock_evaluator = Mock()
        mock_evaluator_class.return_value = mock_evaluator
        mock_evaluator.generate_tests.return_value = {
            'success': True,
            'tests': []
        }
        mock_evaluator.run_tests.return_value = {
            'summary': {'total': 0, 'passed': 0, 'failed': 0, 'pass_rate': 0},
            'results': []
        }
        
        result = cli_runner.invoke(app, ["test", "nonexistent.yaml"])
        
        assert result.exit_code == 0
        assert "Searching for file" in result.output
        assert "Found file at" in result.output
    
    def test_file_not_found(self, cli_runner):
        """Test handling of missing files"""
        result = cli_runner.invoke(app, ["test", "definitely_not_exists.yaml"])
        
        assert result.exit_code == 1
        assert "Could not locate file" in result.output
    
    @patch('pbt.cli.main.PromptEvaluator')
    def test_performance_tests(self, mock_evaluator_class, cli_runner, temp_dir):
        """Test running performance tests"""
        # Create test file with performance tests
        test_data = {
            'prompt_file': 'test.yaml',
            'tests': [{'name': 'basic', 'inputs': {}, 'expected': 'result'}],
            'performance_tests': [
                {
                    'name': 'consistency_test',
                    'runs': 5,
                    'inputs': {'text': 'test'}
                }
            ]
        }
        
        test_file = temp_dir / "perf_test.yaml"
        with open(test_file, 'w') as f:
            yaml.dump(test_data, f)
        
        # Create dummy prompt file
        prompt_file = temp_dir / "test.yaml"
        with open(prompt_file, 'w') as f:
            yaml.dump({'name': 'test', 'template': 'test'}, f)
        
        # Set up mock
        mock_evaluator = Mock()
        mock_evaluator_class.return_value = mock_evaluator
        mock_evaluator.test_agent_with_file.return_value = {
            'summary': {'total': 1, 'passed': 1, 'failed': 0, 'pass_rate': 1.0},
            'results': [{'test_name': 'basic', 'passed': True}],
            'performance_results': {
                'performance_tests': [
                    {
                        'test_name': 'consistency_test',
                        'runs': 5,
                        'consistency_score': 0.85
                    }
                ]
            }
        }
        
        result = cli_runner.invoke(app, ["test", str(test_file)])
        
        assert result.exit_code == 0
        assert "Performance Test Results" in result.output
        assert "consistency_test" in result.output
        assert "0.85" in result.output
    
    @patch('pbt.cli.main.PromptEvaluator')
    def test_save_results(self, mock_evaluator_class, cli_runner, sample_prompt_yaml, temp_dir):
        """Test saving test results"""
        # Set up mock
        mock_evaluator = Mock()
        mock_evaluator_class.return_value = mock_evaluator
        mock_evaluator.generate_tests.return_value = {
            'success': True,
            'tests': [{'name': 'test1'}]
        }
        mock_evaluator.run_tests.return_value = {
            'summary': {'total': 1, 'passed': 1, 'failed': 0, 'pass_rate': 1.0},
            'results': [{'test_name': 'test1', 'passed': True}]
        }
        
        # Change to temp dir to ensure evaluations folder is created there
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            result = cli_runner.invoke(app, [
                "test",
                str(sample_prompt_yaml),
                "--save"
            ])
            
            assert result.exit_code == 0
            assert "Results saved to" in result.output
            
            # Check that results file was created
            eval_dir = temp_dir / "evaluations"
            assert eval_dir.exists()
            
            result_files = list(eval_dir.glob("test_results_*.json"))
            assert len(result_files) == 1
            
            # Verify content
            with open(result_files[0], 'r') as f:
                saved_data = json.load(f)
                assert saved_data['summary']['total'] == 1
                assert saved_data['summary']['passed'] == 1
        
        finally:
            os.chdir(original_cwd)


class TestTestJSONLCommand:
    """Test the testjsonl command functionality"""
    
    @patch('pbt.cli.main.PromptEvaluator')
    def test_run_jsonl_tests(self, mock_evaluator_class, cli_runner, sample_prompt_yaml, sample_jsonl_tests):
        """Test running JSONL test file"""
        # Set up mock
        mock_evaluator = Mock()
        mock_evaluator_class.return_value = mock_evaluator
        mock_evaluator.run_jsonl_tests.return_value = {
            'summary': {
                'total': 2,
                'passed': 2,
                'failed': 0,
                'pass_rate': 1.0
            },
            'results': [
                {
                    'test_name': 'basic_summary',
                    'passed': True,
                    'score': 8.5,
                    'keyword_matches': ['test'],
                    'expected_keywords': ['test']
                },
                {
                    'test_name': 'long_text',
                    'passed': True,
                    'score': 9.0,
                    'keyword_matches': ['longer', 'multiple'],
                    'expected_keywords': ['longer', 'multiple']
                }
            ]
        }
        
        result = cli_runner.invoke(app, [
            "testjsonl",
            str(sample_prompt_yaml),
            str(sample_jsonl_tests)
        ])
        
        assert result.exit_code == 0
        assert "JSONL Test Results" in result.output
        assert "basic_summary" in result.output
        assert "long_text" in result.output
        assert "2/2" in result.output  # All keywords matched
        assert "100.0%" in result.output
    
    @patch('pbt.cli.main.PromptEvaluator')
    def test_jsonl_with_errors(self, mock_evaluator_class, cli_runner, sample_prompt_yaml, sample_jsonl_tests):
        """Test JSONL tests with errors"""
        # Set up mock
        mock_evaluator = Mock()
        mock_evaluator_class.return_value = mock_evaluator
        mock_evaluator.run_jsonl_tests.return_value = {
            'summary': {
                'total': 2,
                'passed': 0,
                'failed': 2,
                'pass_rate': 0.0
            },
            'results': [
                {
                    'test_name': 'test1',
                    'error': 'Failed to process'
                },
                {
                    'test_name': 'test2',
                    'passed': False,
                    'score': 3.0,
                    'keyword_matches': [],
                    'expected_keywords': ['missing']
                }
            ]
        }
        
        result = cli_runner.invoke(app, [
            "testjsonl",
            str(sample_prompt_yaml),
            str(sample_jsonl_tests),
            "--no-save"
        ])
        
        assert result.exit_code == 0
        assert "ERROR" in result.output
        assert "0.0%" in result.output


class TestReadyCommand:
    """Test the ready command functionality"""
    
    @patch('pbt.cli.main.PromptEvaluator')
    def test_ready_for_production(self, mock_evaluator_class, cli_runner):
        """Test assessing production readiness - ready"""
        # Set up mock
        mock_evaluator = Mock()
        mock_evaluator_class.return_value = mock_evaluator
        mock_evaluator.assess_production_readiness.return_value = {
            'ready_for_production': True,
            'production_score': 0.95,
            'pass_rate': 0.95,
            'avg_score': 8.5,
            'recommendation': 'Prompt is performing well and ready for production deployment.'
        }
        
        result = cli_runner.invoke(app, [
            "ready",
            "prompt.yaml",
            "test.yaml",
            "--threshold", "0.8"
        ])
        
        assert result.exit_code == 0
        assert "READY FOR PRODUCTION" in result.output
        assert "0.95/1.0" in result.output
        assert "95.0%" in result.output
    
    @patch('pbt.cli.main.PromptEvaluator')
    def test_not_ready_for_production(self, mock_evaluator_class, cli_runner):
        """Test assessing production readiness - not ready"""
        # Set up mock
        mock_evaluator = Mock()
        mock_evaluator_class.return_value = mock_evaluator
        mock_evaluator.assess_production_readiness.return_value = {
            'ready_for_production': False,
            'production_score': 0.65,
            'pass_rate': 0.65,
            'avg_score': 6.5,
            'recommendation': 'Prompt needs improvement. Focus on failing test cases.'
        }
        
        result = cli_runner.invoke(app, [
            "ready",
            "prompt.yaml",
            "test.yaml",
            "--no-save"
        ])
        
        assert result.exit_code == 0
        assert "NOT READY" in result.output
        assert "0.65/1.0" in result.output
        assert "needs improvement" in result.output