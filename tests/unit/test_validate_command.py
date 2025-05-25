"""Unit tests for the pbt validate command"""

import pytest
from pathlib import Path
import yaml
import json
import os
from unittest.mock import patch, Mock
from typer.testing import CliRunner

from pbt.cli.main import app


class TestValidateCommand:
    """Test the validate command functionality"""
    
    @patch('pbt.cli.main.PromptEvaluator')
    def test_validate_all_agents(self, mock_evaluator_class, cli_runner, temp_dir):
        """Test validating all agents with JSONL tests"""
        # Set up directory structure
        agents_dir = temp_dir / "agents"
        tests_dir = temp_dir / "tests"
        agents_dir.mkdir()
        tests_dir.mkdir()
        
        # Create agent files
        for i in range(3):
            agent_data = {
                'name': f'Agent {i}',
                'template': f'Process: {{input}}',
                'variables': {'input': {'type': 'string'}}
            }
            with open(agents_dir / f"agent_{i}.prompt.yaml", 'w') as f:
                yaml.dump(agent_data, f)
        
        # Create test files
        for i in range(3):
            test_data = [
                {'test_name': f'test_{i}_1', 'inputs': {'input': 'test'}, 'expected_keywords': ['result']},
                {'test_name': f'test_{i}_2', 'inputs': {'input': 'another'}, 'expected_keywords': ['output']}
            ]
            with open(tests_dir / f"agent_{i}.test.jsonl", 'w') as f:
                for test in test_data:
                    f.write(json.dumps(test) + '\n')
        
        # Set up mock
        mock_evaluator = Mock()
        mock_evaluator_class.return_value = mock_evaluator
        mock_evaluator.validate_all_agents.return_value = {
            'overall_summary': {
                'total_agents': 3,
                'passed_agents': 2,
                'total_tests': 6,
                'passed_tests': 5,
                'agent_pass_rate': 0.67,
                'test_pass_rate': 0.83
            },
            'validation_results': {
                'agent_0': {
                    'summary': {'total': 2, 'passed': 2, 'failed': 0, 'pass_rate': 1.0}
                },
                'agent_1': {
                    'summary': {'total': 2, 'passed': 2, 'failed': 0, 'pass_rate': 1.0}
                },
                'agent_2': {
                    'summary': {'total': 2, 'passed': 1, 'failed': 1, 'pass_rate': 0.5}
                }
            }
        }
        
        result = cli_runner.invoke(app, [
            "validate",
            "--agents-dir", str(agents_dir),
            "--tests-dir", str(tests_dir)
        ])
        
        assert result.exit_code == 0
        assert "Running batch validation" in result.output
        assert "NEEDS REVIEW" in result.output  # 67% pass rate
        assert "Total Agents: 3" in result.output
        assert "Passed Agents: 2" in result.output
        assert "67.0%" in result.output
    
    @patch('pbt.cli.main.PromptEvaluator')
    def test_validate_ready_for_deployment(self, mock_evaluator_class, cli_runner):
        """Test validation showing ready for deployment"""
        # Set up mock
        mock_evaluator = Mock()
        mock_evaluator_class.return_value = mock_evaluator
        mock_evaluator.validate_all_agents.return_value = {
            'overall_summary': {
                'total_agents': 5,
                'passed_agents': 5,
                'total_tests': 20,
                'passed_tests': 19,
                'agent_pass_rate': 1.0,
                'test_pass_rate': 0.95
            },
            'validation_results': {}
        }
        
        result = cli_runner.invoke(app, ["validate"])
        
        assert result.exit_code == 0
        assert "READY FOR DEPLOYMENT" in result.output
        assert "100.0%" in result.output
        assert "Safe to deploy to production" in result.output
    
    @patch('pbt.cli.main.PromptEvaluator')
    def test_validate_not_ready(self, mock_evaluator_class, cli_runner):
        """Test validation showing not ready for deployment"""
        # Set up mock
        mock_evaluator = Mock()
        mock_evaluator_class.return_value = mock_evaluator
        mock_evaluator.validate_all_agents.return_value = {
            'overall_summary': {
                'total_agents': 5,
                'passed_agents': 2,
                'total_tests': 20,
                'passed_tests': 8,
                'agent_pass_rate': 0.4,
                'test_pass_rate': 0.4
            },
            'validation_results': {}
        }
        
        result = cli_runner.invoke(app, ["validate"])
        
        assert result.exit_code == 0
        assert "NOT READY" in result.output
        assert "40.0%" in result.output
        assert "Do not deploy" in result.output
    
    @patch('pbt.cli.main.PromptEvaluator')
    def test_validate_with_individual_reports(self, mock_evaluator_class, cli_runner):
        """Test validation with individual agent reports"""
        # Set up mock
        mock_evaluator = Mock()
        mock_evaluator_class.return_value = mock_evaluator
        mock_evaluator.validate_all_agents.return_value = {
            'overall_summary': {
                'total_agents': 3,
                'passed_agents': 2,
                'total_tests': 9,
                'passed_tests': 7,
                'agent_pass_rate': 0.67,
                'test_pass_rate': 0.78
            },
            'validation_results': {
                'summarizer': {
                    'summary': {'total': 3, 'passed': 3, 'failed': 0, 'pass_rate': 1.0}
                },
                'translator': {
                    'summary': {'total': 3, 'passed': 2, 'failed': 1, 'pass_rate': 0.67}
                },
                'analyzer': {
                    'error': 'Failed to load test file'
                }
            }
        }
        
        result = cli_runner.invoke(app, ["validate", "--individual"])
        
        assert result.exit_code == 0
        assert "Individual Agent Results" in result.output
        assert "summarizer" in result.output
        assert "✅ PASS" in result.output
        assert "translator" in result.output
        assert "⚠️ WARN" in result.output
        assert "analyzer" in result.output
        assert "❌ ERROR" in result.output
    
    @patch('pbt.cli.main.PromptEvaluator')
    def test_validate_save_report(self, mock_evaluator_class, cli_runner, temp_dir):
        """Test saving validation report"""
        # Set up mock
        mock_evaluator = Mock()
        mock_evaluator_class.return_value = mock_evaluator
        mock_evaluator.validate_all_agents.return_value = {
            'overall_summary': {
                'total_agents': 1,
                'passed_agents': 1,
                'total_tests': 2,
                'passed_tests': 2,
                'agent_pass_rate': 1.0,
                'test_pass_rate': 1.0
            },
            'validation_results': {}
        }
        
        # Change to temp dir
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            result = cli_runner.invoke(app, ["validate", "--save"])
            
            assert result.exit_code == 0
            assert "Report saved" in result.output
            
            # Check report file
            eval_dir = temp_dir / "evaluations"
            assert eval_dir.exists()
            
            report_files = list(eval_dir.glob("validation_report_*.json"))
            assert len(report_files) == 1
            
            # Verify content
            with open(report_files[0], 'r') as f:
                report_data = json.load(f)
                assert report_data['overall_summary']['total_agents'] == 1
        
        finally:
            os.chdir(original_cwd)
    
    @patch('pbt.cli.main.PromptEvaluator')
    def test_validate_custom_model(self, mock_evaluator_class, cli_runner):
        """Test validation with custom model"""
        # Set up mock
        mock_evaluator = Mock()
        mock_evaluator_class.return_value = mock_evaluator
        mock_evaluator.validate_all_agents.return_value = {
            'overall_summary': {
                'total_agents': 1,
                'passed_agents': 1,
                'total_tests': 1,
                'passed_tests': 1,
                'agent_pass_rate': 1.0,
                'test_pass_rate': 1.0
            },
            'validation_results': {}
        }
        
        result = cli_runner.invoke(app, [
            "validate",
            "--model", "gpt-4"
        ])
        
        assert result.exit_code == 0
        
        # Verify model was passed to evaluator
        mock_evaluator.validate_all_agents.assert_called_once()
        call_args = mock_evaluator.validate_all_agents.call_args
        assert call_args[0][2] == "gpt-4"  # Third argument is model
    
    @patch('pbt.cli.main.PromptEvaluator') 
    def test_validate_error_handling(self, mock_evaluator_class, cli_runner):
        """Test validation error handling"""
        # Set up mock to raise exception
        mock_evaluator = Mock()
        mock_evaluator_class.return_value = mock_evaluator
        mock_evaluator.validate_all_agents.side_effect = Exception("Validation failed")
        
        result = cli_runner.invoke(app, ["validate"])
        
        assert result.exit_code == 1
        assert "Error running validation" in result.output
        assert "Validation failed" in result.output