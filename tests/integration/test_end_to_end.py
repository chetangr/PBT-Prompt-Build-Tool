"""End-to-end integration tests for PBT commands"""

import pytest
from pathlib import Path
import yaml
import json
import os
import tempfile
import shutil
from unittest.mock import patch, Mock
from typer.testing import CliRunner

from pbt.cli.main import app


class TestEndToEndWorkflow:
    """Test complete workflows across multiple commands"""
    
    @patch('pbt.cli.main.PromptGenerator')
    @patch('pbt.cli.main.PromptEvaluator')
    def test_generate_and_test_workflow(self, mock_evaluator_class, mock_generator_class, cli_runner):
        """Test generating a prompt and then testing it"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            original_cwd = os.getcwd()
            os.chdir(temp_path)
            
            try:
                # Set up mocks
                mock_generator = Mock()
                mock_generator_class.return_value = mock_generator
                
                mock_generator.generate.return_value = {
                    'success': True,
                    'prompt_yaml': {
                        'name': 'test-prompt',
                        'template': 'Process: {input}',
                        'variables': {'input': {'type': 'string'}}
                    }
                }
                
                mock_generator.generate_jsonl_tests.return_value = {
                    'success': True,
                    'test_cases': [
                        {'test_name': 'test1', 'inputs': {'input': 'data'}}
                    ]
                }
                mock_generator.save_jsonl_tests.return_value = True
                
                mock_evaluator = Mock()
                mock_evaluator_class.return_value = mock_evaluator
                
                mock_evaluator.run_jsonl_tests.return_value = {
                    'summary': {
                        'total': 1,
                        'passed': 1,
                        'failed': 0,
                        'pass_rate': 1.0
                    },
                    'results': [
                        {'test_name': 'test1', 'passed': True, 'score': 9.0}
                    ]
                }
                
                # Step 1: Generate prompt
                result = cli_runner.invoke(app, [
                    "generate",
                    "--goal", "Process data",
                    "--num-tests", "1"
                ])
                
                assert result.exit_code == 0
                assert "Generated prompt saved to" in result.output
                assert "Generated 1 test cases" in result.output
                
                # Verify files created
                yaml_files = list(temp_path.glob("*.yaml"))
                assert len(yaml_files) == 1
                
                test_files = list((temp_path / "tests").glob("*.jsonl"))
                assert len(test_files) == 1
                
                # Step 2: Test the generated prompt
                result = cli_runner.invoke(app, [
                    "testjsonl",
                    str(yaml_files[0]),
                    str(test_files[0])
                ])
                
                assert result.exit_code == 0
                assert "JSONL Test Results" in result.output
                assert "100.0%" in result.output
                assert "✅ PASS" in result.output
            
            finally:
                os.chdir(original_cwd)
    
    def test_convert_and_validate_workflow(self, cli_runner):
        """Test converting Python agents and validating them"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            original_cwd = os.getcwd()
            os.chdir(temp_path)
            
            try:
                # Create Python agent file
                agent_code = '''
def analyzer_agent(data):
    """Analyze data"""
    prompt = f"Analyze this data: {data}"
    return call_llm(prompt)
'''
                
                agent_file = temp_path / "analyzer.py"
                with open(agent_file, 'w') as f:
                    f.write(agent_code)
                
                # Step 1: Convert Python to YAML
                result = cli_runner.invoke(app, ["convert", str(agent_file)])
                
                assert result.exit_code == 0
                assert "Successfully converted" in result.output
                assert "Prompts extracted: 1" in result.output
                
                # Check converted files
                agents_dir = temp_path / "agents"
                assert agents_dir.exists()
                
                yaml_files = list(agents_dir.glob("*.yaml"))
                assert len(yaml_files) == 1
                
                # Step 2: Generate tests for converted prompt
                with patch('pbt.cli.main.PromptGenerator') as mock_gen_class:
                    mock_generator = Mock()
                    mock_gen_class.return_value = mock_generator
                    
                    mock_generator.generate_jsonl_tests.return_value = {
                        'success': True,
                        'test_cases': [
                            {'test_name': 'test1', 'inputs': {'data': 'sample'}}
                        ]
                    }
                    mock_generator.save_jsonl_tests.return_value = True
                    
                    result = cli_runner.invoke(app, [
                        "gentests",
                        str(yaml_files[0])
                    ])
                    
                    assert result.exit_code == 0
                    assert "Generated 1 test cases" in result.output
                
                # Step 3: Validate
                with patch('pbt.cli.main.PromptEvaluator') as mock_eval_class:
                    mock_evaluator = Mock()
                    mock_eval_class.return_value = mock_evaluator
                    
                    mock_evaluator.validate_all_agents.return_value = {
                        'overall_summary': {
                            'total_agents': 1,
                            'passed_agents': 1,
                            'total_tests': 1,
                            'passed_tests': 1,
                            'agent_pass_rate': 1.0,
                            'test_pass_rate': 1.0
                        },
                        'validation_results': {
                            'analyzer': {
                                'summary': {
                                    'total': 1,
                                    'passed': 1,
                                    'failed': 0,
                                    'pass_rate': 1.0
                                }
                            }
                        }
                    }
                    
                    result = cli_runner.invoke(app, ["validate"])
                    
                    assert result.exit_code == 0
                    assert "READY FOR DEPLOYMENT" in result.output
                    assert "100.0%" in result.output
            
            finally:
                os.chdir(original_cwd)
    
    @patch('pbt.cli.main.PromptEvaluator')
    def test_compare_and_regression_workflow(self, mock_evaluator_class, cli_runner):
        """Test comparing versions and checking for regressions"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test files
            v1_file = temp_path / "v1.yaml"
            v2_file = temp_path / "v2.yaml"
            test_file = temp_path / "test.yaml"
            
            for f in [v1_file, v2_file, test_file]:
                with open(f, 'w') as file:
                    yaml.dump({'name': 'test', 'template': 'test'}, file)
            
            # Set up mock
            mock_evaluator = Mock()
            mock_evaluator_class.return_value = mock_evaluator
            
            # Step 1: Compare versions
            mock_evaluator.compare_prompt_versions.return_value = {
                'ranked_versions': [
                    {'version': 'v2', 'pass_rate': 0.90, 'avg_score': 8.0},
                    {'version': 'v1', 'pass_rate': 0.95, 'avg_score': 8.5}
                ],
                'best_version': {'version': 'v1', 'pass_rate': 0.95}
            }
            
            result = cli_runner.invoke(app, [
                "compare",
                str(test_file),
                "--mode", "versions",
                "--version", str(v1_file),
                "--version", str(v2_file)
            ])
            
            assert result.exit_code == 0
            assert "Best Version: v1" in result.output
            
            # Step 2: Run regression test
            mock_evaluator.regression_test.return_value = {
                'regression_detected': True,
                'performance_delta': {
                    'pass_rate_change': -0.05,
                    'score_change': -0.5
                },
                'test_regressions': [
                    {'test_name': 'test1', 'score_difference': -1.0}
                ],
                'recommendation': 'V2 shows regression compared to V1.'
            }
            
            result = cli_runner.invoke(app, [
                "regression",
                str(v2_file),  # current
                str(v1_file),  # baseline
                str(test_file)
            ])
            
            assert result.exit_code == 0
            assert "REGRESSION DETECTED" in result.output
            assert "V2 shows regression" in result.output


class TestInitAndProjectSetup:
    """Test project initialization and setup"""
    
    @patch('pbt.cli.main.PBTProject')
    def test_init_and_generate_workflow(self, mock_project_class, cli_runner):
        """Test initializing project and generating first prompt"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            project_dir = temp_path / "my-project"
            
            # Mock project initialization
            mock_project = Mock()
            mock_project_class.init.return_value = mock_project
            
            # Step 1: Initialize project
            result = cli_runner.invoke(app, [
                "init",
                "--name", "my-project",
                "--directory", str(project_dir)
            ])
            
            assert result.exit_code == 0
            assert "Initializing PBT project: my-project" in result.output
            assert "Project initialized" in result.output
            assert "Next steps:" in result.output
            
            # Verify init was called correctly
            mock_project_class.init.assert_called_once()
            call_args = mock_project_class.init.call_args[0]
            assert call_args[0] == project_dir
            assert call_args[1] == "my-project"
            assert call_args[2] == "default"  # template


class TestBatchOperations:
    """Test batch operations across multiple files"""
    
    @patch('pbt.cli.main.PromptEvaluator')
    def test_batch_validation(self, mock_evaluator_class, cli_runner):
        """Test validating multiple agents in batch"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create multiple agent and test files
            agents_dir = temp_path / "agents"
            tests_dir = temp_path / "tests"
            agents_dir.mkdir()
            tests_dir.mkdir()
            
            # Create 5 agents with tests
            for i in range(5):
                # Agent file
                agent_data = {
                    'name': f'Agent{i}',
                    'template': f'Process {{input}} for agent {i}'
                }
                with open(agents_dir / f"agent{i}.yaml", 'w') as f:
                    yaml.dump(agent_data, f)
                
                # Test file
                test_data = [
                    {'test_name': f'test{i}', 'inputs': {'input': 'data'}}
                ]
                with open(tests_dir / f"agent{i}.test.jsonl", 'w') as f:
                    for test in test_data:
                        f.write(json.dumps(test) + '\n')
            
            # Set up mock
            mock_evaluator = Mock()
            mock_evaluator_class.return_value = mock_evaluator
            
            # Simulate mixed results
            mock_evaluator.validate_all_agents.return_value = {
                'overall_summary': {
                    'total_agents': 5,
                    'passed_agents': 4,
                    'total_tests': 5,
                    'passed_tests': 4,
                    'agent_pass_rate': 0.8,
                    'test_pass_rate': 0.8
                },
                'validation_results': {
                    f'agent{i}': {
                        'summary': {
                            'total': 1,
                            'passed': 1 if i < 4 else 0,
                            'failed': 0 if i < 4 else 1,
                            'pass_rate': 1.0 if i < 4 else 0.0
                        }
                    } for i in range(5)
                }
            }
            
            result = cli_runner.invoke(app, [
                "validate",
                "--agents-dir", str(agents_dir),
                "--tests-dir", str(tests_dir),
                "--individual"
            ])
            
            assert result.exit_code == 0
            assert "Total Agents: 5" in result.output
            assert "Passed Agents: 4" in result.output
            assert "80.0%" in result.output
            assert "READY FOR DEPLOYMENT" in result.output
            assert "Individual Agent Results" in result.output