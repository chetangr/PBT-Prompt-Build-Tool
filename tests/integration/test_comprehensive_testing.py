"""Integration tests for comprehensive testing workflow"""

import pytest
from pathlib import Path
import yaml
import json
import tempfile
import os
from unittest.mock import patch
from typer.testing import CliRunner

from pbt.cli.main import app


class TestComprehensiveTestingWorkflow:
    """Test complete comprehensive testing workflows"""
    
    @patch('pbt.cli.main.ComprehensiveEvaluator')
    def test_full_comprehensive_workflow(self, mock_evaluator_class, cli_runner):
        """Test a complete comprehensive testing workflow"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            original_cwd = os.getcwd()
            os.chdir(temp_path)
            
            try:
                # Step 1: Create prompt file
                prompt_file = temp_path / "summarizer.prompt.yaml"
                prompt_data = {
                    'name': 'summarizer',
                    'model': 'gpt-4',
                    'inputs': {
                        'text': {'type': 'string'}
                    },
                    'template': 'Summarize this clearly:\n"{{ text }}"'
                }
                with open(prompt_file, 'w') as f:
                    yaml.dump(prompt_data, f)
                
                # Step 2: Create comprehensive test file
                test_file = temp_path / "comprehensive_tests.yaml"
                test_data = {
                    'tests': [
                        {
                            'name': 'basic_summary',
                            'inputs': {'text': 'Cats are curious creatures.'},
                            'expected': 'Cats are curious.',
                            'style_expectation': 'concise',
                            'evaluate': {
                                'correctness': True,
                                'faithfulness': True,
                                'style_tone': True,
                                'safety': True
                            }
                        },
                        {
                            'name': 'stability_test',
                            'inputs': {'text': 'Test consistency'},
                            'stability_runs': 5,
                            'evaluate': {
                                'stability': True
                            }
                        },
                        {
                            'name': 'model_comparison',
                            'inputs': {'text': 'Compare models'},
                            'compare_models': ['gpt-4', 'claude'],
                            'evaluate': {
                                'model_quality': True
                            }
                        }
                    ]
                }
                with open(test_file, 'w') as f:
                    yaml.dump(test_data, f)
                
                # Mock evaluator
                mock_evaluator = mock_evaluator_class.return_value
                
                # Create mock results
                from pbt.core.comprehensive_evaluator import EvaluationAspect, AspectScore, TestResult
                
                mock_results = []
                for test in test_data['tests']:
                    aspect_scores = {}
                    
                    if test['evaluate'].get('correctness'):
                        aspect_scores[EvaluationAspect.CORRECTNESS] = AspectScore(
                            aspect=EvaluationAspect.CORRECTNESS,
                            score=8.5,
                            details={'reasoning': 'Good correctness'}
                        )
                    
                    if test['evaluate'].get('faithfulness'):
                        aspect_scores[EvaluationAspect.FAITHFULNESS] = AspectScore(
                            aspect=EvaluationAspect.FAITHFULNESS,
                            score=9.0,
                            details={'reasoning': 'Faithful to input'}
                        )
                    
                    if test['evaluate'].get('style_tone'):
                        aspect_scores[EvaluationAspect.STYLE_TONE] = AspectScore(
                            aspect=EvaluationAspect.STYLE_TONE,
                            score=7.5,
                            details={'reasoning': 'Appropriately concise'}
                        )
                    
                    if test['evaluate'].get('safety'):
                        aspect_scores[EvaluationAspect.SAFETY] = AspectScore(
                            aspect=EvaluationAspect.SAFETY,
                            score=9.5,
                            details={'reasoning': 'No safety concerns'}
                        )
                    
                    if test['evaluate'].get('stability'):
                        aspect_scores[EvaluationAspect.STABILITY] = AspectScore(
                            aspect=EvaluationAspect.STABILITY,
                            score=8.0,
                            details={'reasoning': 'Consistent outputs', 'num_runs': 5}
                        )
                    
                    if test['evaluate'].get('model_quality'):
                        aspect_scores[EvaluationAspect.MODEL_QUALITY] = AspectScore(
                            aspect=EvaluationAspect.MODEL_QUALITY,
                            score=8.5,
                            details={
                                'model_scores': {'gpt-4': 8.5, 'claude': 8.3},
                                'best_model': 'gpt-4'
                            }
                        )
                    
                    result = TestResult(
                        test_name=test['name'],
                        input_data=test['inputs'],
                        output=f"Mock output for {test['name']}",
                        expected=test.get('expected'),
                        aspect_scores=aspect_scores,
                        overall_score=sum(s.score for s in aspect_scores.values()) / len(aspect_scores) if aspect_scores else 0,
                        passed=all(s.passed for s in aspect_scores.values())
                    )
                    mock_results.append(result)
                
                mock_evaluator.run_test_suite.return_value = {
                    'total_tests': len(mock_results),
                    'passed_tests': sum(1 for r in mock_results if r.passed),
                    'pass_rate': sum(1 for r in mock_results if r.passed) / len(mock_results),
                    'results': mock_results,
                    'aspect_summaries': {
                        'correctness': {
                            'avg_score': 8.5,
                            'min_score': 8.0,
                            'max_score': 9.0,
                            'passed': 1
                        },
                        'faithfulness': {
                            'avg_score': 9.0,
                            'min_score': 9.0,
                            'max_score': 9.0,
                            'passed': 1
                        },
                        'style_tone': {
                            'avg_score': 7.5,
                            'min_score': 7.5,
                            'max_score': 7.5,
                            'passed': 1
                        },
                        'safety': {
                            'avg_score': 9.5,
                            'min_score': 9.5,
                            'max_score': 9.5,
                            'passed': 1
                        },
                        'stability': {
                            'avg_score': 8.0,
                            'min_score': 8.0,
                            'max_score': 8.0,
                            'passed': 1
                        },
                        'model_quality': {
                            'avg_score': 8.5,
                            'min_score': 8.5,
                            'max_score': 8.5,
                            'passed': 1
                        }
                    },
                    'metadata': {
                        'prompt_file': str(prompt_file),
                        'test_file': str(test_file),
                        'model': 'gpt-4'
                    }
                }
                
                # Step 3: Run comprehensive tests
                result = cli_runner.invoke(app, [
                    "testcomp",
                    str(prompt_file),
                    str(test_file)
                ])
                
                assert result.exit_code == 0
                assert "Running comprehensive tests" in result.output
                assert "Comprehensive Test Results" in result.output
                assert "Aspect Analysis" in result.output
                
                # Check all aspects are shown
                assert "Correctness" in result.output
                assert "Faithfulness" in result.output
                assert "Style Tone" in result.output
                assert "Safety" in result.output
                assert "Stability" in result.output
                assert "Model Quality" in result.output
                
                # Step 4: Verify report was saved
                eval_dir = temp_path / "evaluations"
                assert eval_dir.exists()
                
                report_files = list(eval_dir.glob("comprehensive_test_*.json"))
                assert len(report_files) == 1
                
                # Load and verify report content
                with open(report_files[0], 'r') as f:
                    report = json.load(f)
                
                assert 'summary' in report
                assert 'aspect_summaries' in report
                assert 'detailed_results' in report
                assert report['summary']['total_tests'] == 3
            
            finally:
                os.chdir(original_cwd)
    
    @patch('pbt.cli.main.ComprehensiveEvaluator')
    def test_jsonl_comprehensive_workflow(self, mock_evaluator_class, cli_runner):
        """Test comprehensive testing with JSONL format"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create prompt file
            prompt_file = temp_path / "test.yaml"
            with open(prompt_file, 'w') as f:
                yaml.dump({'name': 'test', 'template': 'Test: {input}'}, f)
            
            # Create JSONL test file
            test_file = temp_path / "tests.jsonl"
            tests = [
                {
                    'name': 'test1',
                    'inputs': {'input': 'data1'},
                    'evaluate': {
                        'correctness': True,
                        'safety': True
                    }
                },
                {
                    'name': 'test2',
                    'inputs': {'input': 'data2'},
                    'stability_runs': 3,
                    'evaluate': {
                        'stability': True
                    }
                }
            ]
            
            with open(test_file, 'w') as f:
                for test in tests:
                    f.write(json.dumps(test) + '\n')
            
            # Mock evaluator
            mock_evaluator = mock_evaluator_class.return_value
            mock_evaluator.run_test_suite.return_value = {
                'total_tests': 2,
                'passed_tests': 2,
                'pass_rate': 1.0,
                'results': [],
                'aspect_summaries': {},
                'metadata': {}
            }
            
            # Run with JSON output
            result = cli_runner.invoke(app, [
                "testcomp",
                str(prompt_file),
                str(test_file),
                "--format", "json",
                "--no-save"
            ])
            
            assert result.exit_code == 0
            
            # Verify JSON output
            output_data = json.loads(result.output.strip())
            assert output_data['summary']['total_tests'] == 2
            assert output_data['summary']['pass_rate'] == 1.0
    
    @patch('pbt.cli.main.ComprehensiveEvaluator')
    def test_selective_aspect_testing(self, mock_evaluator_class, cli_runner):
        """Test running only specific aspects"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create files
            prompt_file = temp_path / "prompt.yaml"
            test_file = temp_path / "test.yaml"
            
            for f in [prompt_file, test_file]:
                with open(f, 'w') as file:
                    yaml.dump({'dummy': 'content'}, file)
            
            # Mock evaluator
            mock_evaluator = mock_evaluator_class.return_value
            mock_evaluator.run_test_suite.return_value = {
                'total_tests': 1,
                'passed_tests': 1,
                'pass_rate': 1.0,
                'results': [],
                'aspect_summaries': {
                    'correctness': {'avg_score': 8.0, 'min_score': 8.0, 'max_score': 8.0, 'passed': 1},
                    'safety': {'avg_score': 9.5, 'min_score': 9.5, 'max_score': 9.5, 'passed': 1}
                },
                'metadata': {}
            }
            
            # Run with specific aspects
            result = cli_runner.invoke(app, [
                "testcomp",
                str(prompt_file),
                str(test_file),
                "--aspects", "correctness,safety",
                "--no-save"
            ])
            
            assert result.exit_code == 0
            assert "Correctness" in result.output
            assert "Safety" in result.output
            # These aspects should not appear
            assert "Faithfulness" not in result.output
            assert "Style Tone" not in result.output