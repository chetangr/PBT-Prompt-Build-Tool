"""Unit tests for the pbt compare and regression commands"""

import pytest
from pathlib import Path
import yaml
import json
import os
from unittest.mock import patch, Mock
from typer.testing import CliRunner

from pbt.cli.main import app


class TestCompareCommand:
    """Test the compare command functionality"""
    
    @patch('pbt.cli.main.PromptEvaluator')
    def test_compare_versions(self, mock_evaluator_class, cli_runner, temp_dir):
        """Test comparing multiple prompt versions"""
        # Create version files
        v1_file = temp_dir / "v1.yaml"
        v2_file = temp_dir / "v2.yaml"
        test_file = temp_dir / "test.yaml"
        
        for f in [v1_file, v2_file, test_file]:
            with open(f, 'w') as file:
                yaml.dump({'name': 'test', 'template': 'test'}, file)
        
        # Set up mock
        mock_evaluator = Mock()
        mock_evaluator_class.return_value = mock_evaluator
        
        mock_evaluator.compare_prompt_versions.return_value = {
            'ranked_versions': [
                {
                    'version': 'v2',
                    'pass_rate': 0.95,
                    'avg_score': 8.5
                },
                {
                    'version': 'v1',
                    'pass_rate': 0.80,
                    'avg_score': 7.2
                }
            ],
            'best_version': {
                'version': 'v2',
                'pass_rate': 0.95,
                'avg_score': 8.5
            }
        }
        
        result = cli_runner.invoke(app, [
            "compare",
            str(test_file),
            "--mode", "versions",
            "--version", str(v1_file),
            "--version", str(v2_file)
        ])
        
        assert result.exit_code == 0
        assert "Comparing 2 prompt versions" in result.output
        assert "Version Comparison Results" in result.output
        assert "🥇 v2" in result.output  # Winner
        assert "95.0%" in result.output
        assert "Best Version: v2" in result.output
    
    @patch('pbt.cli.main.PromptEvaluator')
    def test_compare_models(self, mock_evaluator_class, cli_runner, temp_dir):
        """Test comparing different models"""
        prompt_file = temp_dir / "prompt.yaml"
        test_file = temp_dir / "test.yaml"
        
        for f in [prompt_file, test_file]:
            with open(f, 'w') as file:
                yaml.dump({'name': 'test', 'template': 'test'}, file)
        
        # Set up mock
        mock_evaluator = Mock()
        mock_evaluator_class.return_value = mock_evaluator
        
        mock_evaluator.compare_models.return_value = {
            'ranked_models': [
                {
                    'model': 'claude',
                    'pass_rate': 0.90,
                    'avg_score': 8.8,
                    'response_time': 1.2
                },
                {
                    'model': 'gpt-4',
                    'pass_rate': 0.85,
                    'avg_score': 8.2,
                    'response_time': 1.5
                }
            ],
            'best_model': {
                'model': 'claude',
                'pass_rate': 0.90
            }
        }
        
        result = cli_runner.invoke(app, [
            "compare",
            str(test_file),
            "--mode", "models",
            "--model", "claude",
            "--model", "gpt-4",
            "--version", str(prompt_file)
        ])
        
        assert result.exit_code == 0
        assert "Comparing 2 models" in result.output
        assert "Model Comparison Results" in result.output
        assert "🥇 claude" in result.output
        assert "90.0%" in result.output
        assert "1.2s" in result.output
        assert "Best Model: claude" in result.output
    
    def test_compare_invalid_mode(self, cli_runner):
        """Test invalid comparison mode"""
        result = cli_runner.invoke(app, [
            "compare",
            "test.yaml",
            "--mode", "invalid"
        ])
        
        assert result.exit_code == 1
        assert "Invalid comparison mode" in result.output
    
    def test_compare_missing_params(self, cli_runner):
        """Test missing required parameters"""
        result = cli_runner.invoke(app, [
            "compare",
            "test.yaml",
            "--mode", "versions"
        ])
        
        assert result.exit_code == 1
        assert "Invalid comparison mode or missing parameters" in result.output
        assert "Examples:" in result.output


class TestRegressionCommand:
    """Test the regression command functionality"""
    
    @patch('pbt.cli.main.PromptEvaluator')
    def test_regression_no_regression(self, mock_evaluator_class, cli_runner, temp_dir):
        """Test regression test with no regression detected"""
        # Set up mock
        mock_evaluator = Mock()
        mock_evaluator_class.return_value = mock_evaluator
        
        mock_evaluator.regression_test.return_value = {
            'regression_detected': False,
            'performance_delta': {
                'pass_rate_change': 0.05,
                'score_change': 0.3
            },
            'test_regressions': [],
            'recommendation': 'No regression detected. Safe to deploy.'
        }
        
        result = cli_runner.invoke(app, [
            "regression",
            "current.yaml",
            "baseline.yaml",
            "test.yaml"
        ])
        
        assert result.exit_code == 0
        assert "NO REGRESSION" in result.output
        assert "+5.0%" in result.output  # Pass rate improved
        assert "+0.3" in result.output  # Score improved
        assert "Safe to deploy" in result.output
    
    @patch('pbt.cli.main.PromptEvaluator')
    def test_regression_detected(self, mock_evaluator_class, cli_runner, temp_dir):
        """Test regression test with regression detected"""
        # Set up mock
        mock_evaluator = Mock()
        mock_evaluator_class.return_value = mock_evaluator
        
        mock_evaluator.regression_test.return_value = {
            'regression_detected': True,
            'performance_delta': {
                'pass_rate_change': -0.15,
                'score_change': -1.2
            },
            'test_regressions': [
                {
                    'test_name': 'test_critical_feature',
                    'score_difference': -3.0
                },
                {
                    'test_name': 'test_edge_case',
                    'score_difference': -2.5
                }
            ],
            'recommendation': 'Regression detected! Do not deploy. Fix failing tests.'
        }
        
        result = cli_runner.invoke(app, [
            "regression",
            "current.yaml",
            "baseline.yaml",
            "test.yaml",
            "--no-save"
        ])
        
        assert result.exit_code == 0
        assert "REGRESSION DETECTED" in result.output
        assert "-15.0%" in result.output  # Pass rate decreased
        assert "-1.2" in result.output  # Score decreased
        assert "Failed Tests:" in result.output
        assert "test_critical_feature" in result.output
        assert "-3.0 points" in result.output
        assert "Do not deploy" in result.output
    
    @patch('pbt.cli.main.PromptEvaluator')
    def test_regression_save_report(self, mock_evaluator_class, cli_runner, temp_dir):
        """Test saving regression report"""
        # Set up mock
        mock_evaluator = Mock()
        mock_evaluator_class.return_value = mock_evaluator
        
        mock_evaluator.regression_test.return_value = {
            'regression_detected': False,
            'performance_delta': {'pass_rate_change': 0, 'score_change': 0},
            'test_regressions': [],
            'recommendation': 'No changes detected.'
        }
        
        # Change to temp dir
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            result = cli_runner.invoke(app, [
                "regression",
                "current.yaml",
                "baseline.yaml",
                "test.yaml",
                "--save"
            ])
            
            assert result.exit_code == 0
            assert "Report saved" in result.output
            
            # Check report file
            eval_dir = temp_dir / "evaluations"
            assert eval_dir.exists()
            
            report_files = list(eval_dir.glob("regression_test_*.json"))
            assert len(report_files) == 1
        
        finally:
            os.chdir(original_cwd)
    
    @patch('pbt.cli.main.PromptEvaluator')
    def test_regression_error_handling(self, mock_evaluator_class, cli_runner):
        """Test regression error handling"""
        # Set up mock to raise exception
        mock_evaluator = Mock()
        mock_evaluator_class.return_value = mock_evaluator
        mock_evaluator.regression_test.side_effect = Exception("Baseline file not found")
        
        result = cli_runner.invoke(app, [
            "regression",
            "current.yaml",
            "baseline.yaml",
            "test.yaml"
        ])
        
        assert result.exit_code == 1
        assert "Error running regression test" in result.output
        assert "Baseline file not found" in result.output