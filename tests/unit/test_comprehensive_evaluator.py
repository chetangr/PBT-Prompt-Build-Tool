"""Unit tests for the comprehensive evaluator module"""

import pytest
from pathlib import Path
import json
import yaml
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

from pbt.core.comprehensive_evaluator import (
    ComprehensiveEvaluator,
    EvaluationAspect,
    AspectScore,
    TestResult
)


class TestAspectScore:
    """Test the AspectScore dataclass"""
    
    def test_aspect_score_creation(self):
        """Test creating an aspect score"""
        score = AspectScore(
            aspect=EvaluationAspect.CORRECTNESS,
            score=8.5,
            details={'reasoning': 'Good accuracy'}
        )
        
        assert score.aspect == EvaluationAspect.CORRECTNESS
        assert score.score == 8.5
        assert score.details['reasoning'] == 'Good accuracy'
        assert score.passed  # Default min_score is 7.0
    
    def test_aspect_score_pass_fail(self):
        """Test pass/fail logic"""
        # Passing score
        score = AspectScore(
            aspect=EvaluationAspect.SAFETY,
            score=9.5,
            details={'min_score': 9.0}
        )
        assert score.passed
        
        # Failing score
        score = AspectScore(
            aspect=EvaluationAspect.SAFETY,
            score=8.5,
            details={'min_score': 9.0}
        )
        assert not score.passed


class TestComprehensiveEvaluator:
    """Test the ComprehensiveEvaluator class"""
    
    @pytest.fixture
    def evaluator(self):
        """Create an evaluator instance"""
        return ComprehensiveEvaluator()
    
    @pytest.fixture
    def mock_llm_client(self):
        """Create a mock LLM client"""
        client = Mock()
        client.generate.return_value = '{"score": 8.5, "reasoning": "Good output"}'
        return client
    
    def test_evaluator_initialization(self, evaluator):
        """Test evaluator initialization"""
        assert evaluator.llm_client is None
        assert len(evaluator.evaluation_prompts) > 0
        assert len(evaluator.safety_patterns) > 0
    
    def test_evaluate_correctness(self, evaluator):
        """Test correctness evaluation"""
        score = evaluator._evaluate_correctness(
            input_data={'text': 'test input'},
            output='test output',
            expected='expected output'
        )
        
        assert score.aspect == EvaluationAspect.CORRECTNESS
        assert isinstance(score.score, float)
        assert 0 <= score.score <= 10
        assert 'reasoning' in score.details
    
    def test_evaluate_faithfulness(self, evaluator):
        """Test faithfulness evaluation"""
        # Test with matching expected output
        score = evaluator._evaluate_faithfulness(
            input_data={'text': 'test'},
            output='This is the expected output',
            expected='expected output'
        )
        
        assert score.aspect == EvaluationAspect.FAITHFULNESS
        assert score.score >= 8.0  # Should score high for containing expected
    
    def test_evaluate_style_tone(self, evaluator):
        """Test style and tone evaluation"""
        # Test concise style
        score = evaluator._evaluate_style_tone(
            input_data={'text': 'test'},
            output='Short output.',
            style_expectation='concise'
        )
        
        assert score.aspect == EvaluationAspect.STYLE_TONE
        assert score.score >= 8.0  # Should score high for being concise
        assert 'word_count' in score.details
        
        # Test verbose style
        long_output = ' '.join(['word'] * 150)
        score = evaluator._evaluate_style_tone(
            input_data={'text': 'test'},
            output=long_output,
            style_expectation='verbose'
        )
        
        assert score.score >= 8.0  # Should score high for being verbose
    
    def test_evaluate_safety(self, evaluator):
        """Test safety evaluation"""
        # Safe content
        score = evaluator._evaluate_safety(
            output='This is a safe and helpful response about coding.'
        )
        
        assert score.aspect == EvaluationAspect.SAFETY
        assert score.score >= 9.0
        assert len(score.details['unsafe_matches']) == 0
        
        # Unsafe content
        score = evaluator._evaluate_safety(
            output='Here is how to hack into systems and bypass security.'
        )
        
        assert score.score < 7.0
        assert 'hack' in str(score.details['reasoning']).lower()
    
    def test_evaluate_stability(self, evaluator):
        """Test stability evaluation"""
        # Mock consistent outputs
        with patch.object(evaluator, '_run_prompt') as mock_run:
            mock_run.return_value = 'Consistent output'
            
            score = evaluator._evaluate_stability(
                template='Test: {input}',
                inputs={'input': 'test'},
                model='gpt-4',
                num_runs=5
            )
            
            assert score.aspect == EvaluationAspect.STABILITY
            assert score.score == 10.0  # Perfect consistency
            assert mock_run.call_count == 5
    
    def test_evaluate_model_quality(self, evaluator):
        """Test model quality comparison"""
        with patch.object(evaluator, '_run_prompt') as mock_run:
            # Different outputs for different models
            mock_run.side_effect = [
                'High quality output with good structure.',
                'ok output',
                'Another well-structured response with details.'
            ]
            
            score = evaluator._evaluate_model_quality(
                template='Test: {input}',
                inputs={'input': 'test'},
                models=['gpt-4', 'gpt-3.5', 'claude']
            )
            
            assert score.aspect == EvaluationAspect.MODEL_QUALITY
            assert 'model_scores' in score.details
            assert 'best_model' in score.details
            assert len(score.details['model_scores']) == 3
    
    def test_evaluate_comprehensive(self, evaluator):
        """Test comprehensive evaluation of a test case"""
        test_case = {
            'name': 'test_comprehensive',
            'inputs': {'text': 'Test input'},
            'expected': 'Test output',
            'style_expectation': 'concise',
            'stability_runs': 3,
            'compare_models': ['gpt-4', 'claude']
        }
        
        result = evaluator.evaluate_comprehensive(
            prompt_template='Summarize: {text}',
            test_case=test_case,
            model='gpt-4',
            aspects_to_evaluate=[
                EvaluationAspect.CORRECTNESS,
                EvaluationAspect.STYLE_TONE
            ]
        )
        
        assert isinstance(result, TestResult)
        assert result.test_name == 'test_comprehensive'
        assert len(result.aspect_scores) == 2
        assert EvaluationAspect.CORRECTNESS in result.aspect_scores
        assert EvaluationAspect.STYLE_TONE in result.aspect_scores
        assert result.overall_score > 0
    
    def test_run_test_suite_yaml(self, evaluator, temp_dir):
        """Test running a complete test suite from YAML"""
        # Create prompt file
        prompt_file = temp_dir / "test.prompt.yaml"
        prompt_data = {
            'name': 'test_prompt',
            'template': 'Summarize: {text}'
        }
        with open(prompt_file, 'w') as f:
            yaml.dump(prompt_data, f)
        
        # Create test file
        test_file = temp_dir / "test.yaml"
        test_data = {
            'tests': [
                {
                    'name': 'test1',
                    'inputs': {'text': 'input1'},
                    'expected': 'output1'
                },
                {
                    'name': 'test2',
                    'inputs': {'text': 'input2'},
                    'expected': 'output2'
                }
            ]
        }
        with open(test_file, 'w') as f:
            yaml.dump(test_data, f)
        
        # Run test suite
        results = evaluator.run_test_suite(
            prompt_file=str(prompt_file),
            test_file=str(test_file),
            model='gpt-4'
        )
        
        assert results['total_tests'] == 2
        assert 'results' in results
        assert len(results['results']) == 2
        assert 'aspect_summaries' in results
        assert results['pass_rate'] >= 0
    
    def test_run_test_suite_jsonl(self, evaluator, temp_dir):
        """Test running a test suite from JSONL"""
        # Create prompt file
        prompt_file = temp_dir / "test.prompt.yaml"
        prompt_data = {
            'name': 'test_prompt',
            'template': 'Process: {text}'
        }
        with open(prompt_file, 'w') as f:
            yaml.dump(prompt_data, f)
        
        # Create JSONL test file
        test_file = temp_dir / "test.jsonl"
        tests = [
            {'name': 'test1', 'inputs': {'text': 'data1'}},
            {'name': 'test2', 'inputs': {'text': 'data2'}, 'expected': 'result2'}
        ]
        with open(test_file, 'w') as f:
            for test in tests:
                f.write(json.dumps(test) + '\n')
        
        # Run test suite
        results = evaluator.run_test_suite(
            prompt_file=str(prompt_file),
            test_file=str(test_file)
        )
        
        assert results['total_tests'] == 2
        assert len(results['results']) == 2


class TestComprehensiveTestCommand:
    """Test the testcomp CLI command"""
    
    @patch('pbt.cli.main.ComprehensiveEvaluator')
    def test_testcomp_command_basic(self, mock_evaluator_class, cli_runner, temp_dir):
        """Test basic testcomp command"""
        # Create test files
        prompt_file = temp_dir / "test.yaml"
        test_file = temp_dir / "test_cases.yaml"
        
        for f in [prompt_file, test_file]:
            f.write_text("dummy: content")
        
        # Mock evaluator
        mock_evaluator = Mock()
        mock_evaluator_class.return_value = mock_evaluator
        
        mock_result = Mock()
        mock_result.test_name = "test1"
        mock_result.passed = True
        mock_result.overall_score = 8.5
        mock_result.aspect_scores = {}
        
        mock_evaluator.run_test_suite.return_value = {
            'total_tests': 1,
            'passed_tests': 1,
            'pass_rate': 1.0,
            'results': [mock_result],
            'aspect_summaries': {},
            'metadata': {}
        }
        
        result = cli_runner.invoke(app, [
            "testcomp",
            str(prompt_file),
            str(test_file)
        ])
        
        assert result.exit_code == 0
        assert "Running comprehensive tests" in result.output
        assert "Comprehensive Test Results" in result.output
        assert "100.0%" in result.output
    
    @patch('pbt.cli.main.ComprehensiveEvaluator')
    def test_testcomp_with_aspects(self, mock_evaluator_class, cli_runner, temp_dir):
        """Test testcomp with specific aspects"""
        # Create test files
        prompt_file = temp_dir / "test.yaml"
        test_file = temp_dir / "test_cases.yaml"
        
        for f in [prompt_file, test_file]:
            f.write_text("dummy: content")
        
        # Mock evaluator
        mock_evaluator = Mock()
        mock_evaluator_class.return_value = mock_evaluator
        
        mock_evaluator.run_test_suite.return_value = {
            'total_tests': 0,
            'passed_tests': 0,
            'pass_rate': 0,
            'results': [],
            'aspect_summaries': {},
            'metadata': {}
        }
        
        result = cli_runner.invoke(app, [
            "testcomp",
            str(prompt_file),
            str(test_file),
            "--aspects", "correctness,safety"
        ])
        
        assert result.exit_code == 1  # No tests means failure
        assert "correctness" in result.output.lower() or "CORRECTNESS" in result.output
    
    @patch('pbt.cli.main.ComprehensiveEvaluator')
    def test_testcomp_json_output(self, mock_evaluator_class, cli_runner, temp_dir):
        """Test testcomp with JSON output format"""
        # Create test files
        prompt_file = temp_dir / "test.yaml"
        test_file = temp_dir / "test_cases.yaml"
        
        for f in [prompt_file, test_file]:
            f.write_text("dummy: content")
        
        # Mock evaluator
        mock_evaluator = Mock()
        mock_evaluator_class.return_value = mock_evaluator
        
        mock_result = Mock()
        mock_result.test_name = "test1"
        mock_result.passed = True
        mock_result.overall_score = 8.5
        mock_result.aspect_scores = {}
        
        mock_evaluator.run_test_suite.return_value = {
            'total_tests': 1,
            'passed_tests': 1,
            'pass_rate': 1.0,
            'results': [mock_result],
            'aspect_summaries': {},
            'metadata': {}
        }
        
        result = cli_runner.invoke(app, [
            "testcomp",
            str(prompt_file),
            str(test_file),
            "--format", "json",
            "--no-save"
        ])
        
        assert result.exit_code == 0
        # Should contain valid JSON
        output_json = json.loads(result.output.strip())
        assert 'summary' in output_json
        assert output_json['summary']['total_tests'] == 1
    
    @patch('pbt.cli.main.ComprehensiveEvaluator')
    def test_testcomp_markdown_output(self, mock_evaluator_class, cli_runner, temp_dir):
        """Test testcomp with markdown output format"""
        # Create test files
        prompt_file = temp_dir / "test.yaml"
        test_file = temp_dir / "test_cases.yaml"
        
        for f in [prompt_file, test_file]:
            f.write_text("dummy: content")
        
        # Mock evaluator
        mock_evaluator = Mock()
        mock_evaluator_class.return_value = mock_evaluator
        
        mock_evaluator.run_test_suite.return_value = {
            'total_tests': 2,
            'passed_tests': 1,
            'pass_rate': 0.5,
            'results': [],
            'aspect_summaries': {
                'correctness': {
                    'avg_score': 7.5,
                    'min_score': 6.0,
                    'max_score': 9.0,
                    'passed': 1
                }
            },
            'metadata': {}
        }
        
        result = cli_runner.invoke(app, [
            "testcomp",
            str(prompt_file),
            str(test_file),
            "--format", "markdown",
            "--no-save"
        ])
        
        assert result.exit_code == 1  # Low pass rate
        assert "# Comprehensive Test Report" in result.output
        assert "## Summary" in result.output
        assert "## Aspect Analysis" in result.output
        assert "### Correctness" in result.output