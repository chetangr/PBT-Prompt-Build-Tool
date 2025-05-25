"""Mock classes for PBT testing"""

from typing import Dict, List, Any, Optional
from pathlib import Path


class MockPromptGenerator:
    """Mock PromptGenerator for testing"""
    
    def generate(self, goal: str, model: str = "claude", style: str = "professional", 
                 variables: Optional[List[str]] = None) -> Dict[str, Any]:
        """Mock generate method"""
        return {
            'success': True,
            'prompt_yaml': {
                'name': goal.lower().replace(' ', '-'),
                'version': '1.0',
                'model': model,
                'template': f'Mock template for: {goal}',
                'variables': {var: {'type': 'string'} for var in (variables or [])}
            }
        }
    
    def generate_jsonl_tests(self, prompt_content: str, num_tests: int) -> Dict[str, Any]:
        """Mock test generation"""
        return {
            'success': True,
            'test_cases': [
                {'test_name': f'test_{i}', 'inputs': {'var': f'value_{i}'}}
                for i in range(num_tests)
            ]
        }
    
    def save_jsonl_tests(self, test_cases: List[Dict], filename: str) -> bool:
        """Mock save tests"""
        return True


class MockPromptEvaluator:
    """Mock PromptEvaluator for testing"""
    
    def test_agent_with_file(self, prompt_file: str, test_file: str, model: str) -> Dict[str, Any]:
        """Mock test execution"""
        return {
            'summary': {
                'total': 2,
                'passed': 2,
                'failed': 0,
                'pass_rate': 1.0
            },
            'results': [
                {'test_name': 'test_1', 'passed': True, 'score': 8.5},
                {'test_name': 'test_2', 'passed': True, 'score': 9.0}
            ]
        }
    
    def generate_tests(self, prompt_content: str, num_tests: int, test_type: str) -> Dict[str, Any]:
        """Mock test generation"""
        return {
            'success': True,
            'tests': [
                {'name': f'auto_test_{i}', 'inputs': {}, 'expected': 'result'}
                for i in range(num_tests)
            ]
        }
    
    def run_tests(self, template: str, tests: List[Dict], model: str) -> Dict[str, Any]:
        """Mock run tests"""
        return {
            'summary': {
                'total': len(tests),
                'passed': len(tests),
                'failed': 0,
                'pass_rate': 1.0
            },
            'results': [
                {'test_name': test.get('name', f'test_{i}'), 'passed': True, 'score': 8.0}
                for i, test in enumerate(tests)
            ]
        }
    
    def run_jsonl_tests(self, prompt_file: str, jsonl_file: str, model: str) -> Dict[str, Any]:
        """Mock JSONL test execution"""
        return {
            'summary': {
                'total': 2,
                'passed': 2,
                'failed': 0,
                'pass_rate': 1.0
            },
            'results': [
                {
                    'test_name': 'test_1',
                    'passed': True,
                    'score': 8.5,
                    'keyword_matches': ['keyword1'],
                    'expected_keywords': ['keyword1']
                }
            ]
        }
    
    def assess_production_readiness(self, prompt_file: str, test_file: str, threshold: float) -> Dict[str, Any]:
        """Mock production readiness assessment"""
        return {
            'ready_for_production': True,
            'production_score': 0.95,
            'pass_rate': 0.95,
            'avg_score': 8.5,
            'recommendation': 'Ready for production'
        }
    
    def compare_prompt_versions(self, versions: List[Dict], test_file: str) -> Dict[str, Any]:
        """Mock version comparison"""
        return {
            'ranked_versions': [
                {'version': v['name'], 'pass_rate': 0.9, 'avg_score': 8.0}
                for v in versions
            ],
            'best_version': {'version': versions[0]['name'], 'pass_rate': 0.9}
        }
    
    def compare_models(self, prompt_file: str, test_file: str, models: List[str]) -> Dict[str, Any]:
        """Mock model comparison"""
        return {
            'ranked_models': [
                {'model': model, 'pass_rate': 0.85, 'avg_score': 8.0, 'response_time': 1.2}
                for model in models
            ],
            'best_model': {'model': models[0], 'pass_rate': 0.85}
        }
    
    def regression_test(self, current: str, baseline: str, test_file: str) -> Dict[str, Any]:
        """Mock regression test"""
        return {
            'regression_detected': False,
            'performance_delta': {
                'pass_rate_change': 0.05,
                'score_change': 0.3
            },
            'test_regressions': [],
            'recommendation': 'No regression detected'
        }
    
    def validate_all_agents(self, agents_dir: str, tests_dir: str, model: str) -> Dict[str, Any]:
        """Mock batch validation"""
        return {
            'overall_summary': {
                'total_agents': 3,
                'passed_agents': 3,
                'total_tests': 9,
                'passed_tests': 9,
                'agent_pass_rate': 1.0,
                'test_pass_rate': 1.0
            },
            'validation_results': {
                'agent_1': {'summary': {'total': 3, 'passed': 3, 'failed': 0, 'pass_rate': 1.0}},
                'agent_2': {'summary': {'total': 3, 'passed': 3, 'failed': 0, 'pass_rate': 1.0}},
                'agent_3': {'summary': {'total': 3, 'passed': 3, 'failed': 0, 'pass_rate': 1.0}}
            }
        }


class MockPBTProject:
    """Mock PBTProject for testing"""
    
    @staticmethod
    def init(project_dir: Path, project_name: str, template: str):
        """Mock project initialization"""
        # Create directories
        project_dir.mkdir(parents=True, exist_ok=True)
        (project_dir / "prompts").mkdir(exist_ok=True)
        (project_dir / "tests").mkdir(exist_ok=True)
        (project_dir / "evaluations").mkdir(exist_ok=True)
        
        # Create config file
        config = {
            'name': project_name,
            'version': '1.0.0',
            'template': template
        }
        
        import yaml
        with open(project_dir / "pbt.yaml", 'w') as f:
            yaml.dump(config, f)
        
        # Create .env.example
        with open(project_dir / ".env.example", 'w') as f:
            f.write("ANTHROPIC_API_KEY=your-key-here\n")
            f.write("OPENAI_API_KEY=your-key-here\n")
        
        return MockPBTProject()


class MockPromptDAG:
    """Mock PromptDAG for testing"""
    
    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.nodes = {}
        self.graph = type('obj', (object,), {'edges': lambda: []})()
    
    def load_prompts(self):
        """Mock load prompts"""
        self.nodes = {
            'prompt1': {'deps': []},
            'prompt2': {'deps': ['prompt1']},
            'prompt3': {'deps': ['prompt1', 'prompt2']}
        }
    
    def get_execution_order(self, target: Optional[str] = None) -> List[str]:
        """Mock execution order"""
        if target:
            return [target]
        return ['prompt1', 'prompt2', 'prompt3']
    
    def get_lineage(self, prompt_name: str) -> Dict[str, List[str]]:
        """Mock lineage"""
        return {
            'upstream': ['prompt1'] if prompt_name != 'prompt1' else [],
            'downstream': ['prompt3'] if prompt_name != 'prompt3' else []
        }
    
    def to_mermaid(self) -> str:
        """Mock mermaid diagram"""
        return "graph LR\n  prompt1 --> prompt2\n  prompt2 --> prompt3"


class MockSnapshotManager:
    """Mock SnapshotManager for testing"""
    
    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
    
    def create_snapshot(self, prompt_path: Path, reason: str):
        """Mock create snapshot"""
        return {'timestamp': '2024-01-01', 'version': '1.0'}
    
    def snapshot_all(self, reason: str) -> List[Dict]:
        """Mock snapshot all"""
        return [
            {'prompt': 'prompt1', 'timestamp': '2024-01-01'},
            {'prompt': 'prompt2', 'timestamp': '2024-01-01'}
        ]
    
    def get_snapshots(self, prompt_name: str) -> List:
        """Mock get snapshots"""
        return [
            type('obj', (object,), {
                'timestamp': '2024-01-01',
                'version': '1.0',
                'metadata': {'reason': 'Initial snapshot'}
            })()
        ]
    
    def diff_snapshots(self, prompt_name: str) -> str:
        """Mock diff"""
        return "+ Added line\n- Removed line"
    
    def restore_snapshot(self, prompt_name: str, timestamp: str) -> bool:
        """Mock restore"""
        return True


class MockProfileManager:
    """Mock ProfileManager for testing"""
    
    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.profiles = {
            'development': type('obj', (object,), {
                'target': 'dev',
                'outputs': {'dev': {'llm_provider': 'openai'}}
            })()
        }
        self.active_profile = 'development'
    
    def set_active_profile(self, profile: str, target: Optional[str] = None):
        """Mock set active profile"""
        self.active_profile = profile
    
    def validate_profile(self, profile_name: str) -> List[str]:
        """Mock validate profile"""
        return []  # No errors
    
    def create_profile(self, name: str, outputs: Dict):
        """Mock create profile"""
        self.profiles[name] = type('obj', (object,), {
            'target': 'dev',
            'outputs': outputs
        })()
        return self.profiles[name]


class MockRunResultsManager:
    """Mock RunResultsManager for testing"""
    
    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.run_id = None
    
    def start_run(self, project_name: str, args: Dict) -> str:
        """Mock start run"""
        self.run_id = "run_123"
        return self.run_id
    
    def start_prompt_execution(self, prompt_name: str):
        """Mock start execution"""
        pass
    
    def record_prompt_result(self, prompt_name: str, status, message: str):
        """Mock record result"""
        pass
    
    def complete_run(self) -> Dict:
        """Mock complete run"""
        return {
            'run_id': self.run_id,
            'status': 'success',
            'prompts_run': 3,
            'prompts_passed': 3
        }
    
    def generate_summary(self, results: Dict) -> str:
        """Mock generate summary"""
        return "Run completed successfully: 3/3 prompts passed"


class MockManifest:
    """Mock Manifest for testing"""
    
    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
    
    def load_prompts(self):
        """Mock load prompts"""
        pass
    
    def load_tests(self):
        """Mock load tests"""
        pass
    
    def generate_docs(self, output_dir: Path):
        """Mock generate docs"""
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "index.html").write_text("<html>Mock docs</html>")


# Mock RunStatus enum
class RunStatus:
    SUCCESS = "success"
    FAILED = "failed"


class MockComprehensiveEvaluator:
    """Mock ComprehensiveEvaluator for testing"""
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
    
    def evaluate_comprehensive(self, prompt_template: str, test_case: Dict, 
                             model: str = "gpt-4", aspects_to_evaluate=None):
        """Mock comprehensive evaluation"""
        from tests.mocks import EvaluationAspect, AspectScore, TestResult
        
        # Create mock aspect scores
        aspect_scores = {}
        for aspect in (aspects_to_evaluate or []):
            aspect_scores[aspect] = AspectScore(
                aspect=aspect,
                score=8.5,
                details={'reasoning': f'Mock evaluation for {aspect.value}'}
            )
        
        return TestResult(
            test_name=test_case.get('name', 'test'),
            input_data=test_case.get('inputs', {}),
            output="Mock output",
            expected=test_case.get('expected'),
            aspect_scores=aspect_scores,
            overall_score=8.5,
            passed=True
        )
    
    def run_test_suite(self, prompt_file: str, test_file: str, model: str = "gpt-4"):
        """Mock test suite run"""
        return {
            'total_tests': 2,
            'passed_tests': 2,
            'pass_rate': 1.0,
            'results': [
                self.evaluate_comprehensive(
                    "template", {'name': 'test1'}, model
                ),
                self.evaluate_comprehensive(
                    "template", {'name': 'test2'}, model
                )
            ],
            'aspect_summaries': {
                'correctness': {
                    'avg_score': 8.5,
                    'min_score': 8.0,
                    'max_score': 9.0,
                    'passed': 2
                }
            },
            'metadata': {
                'prompt_file': prompt_file,
                'test_file': test_file,
                'model': model
            }
        }


# Mock dataclasses for comprehensive evaluator
from enum import Enum
from dataclasses import dataclass, field


class EvaluationAspect(Enum):
    CORRECTNESS = "correctness"
    FAITHFULNESS = "faithfulness"
    STYLE_TONE = "style_tone"
    SAFETY = "safety"
    STABILITY = "stability"
    MODEL_QUALITY = "model_quality"


@dataclass
class AspectScore:
    aspect: EvaluationAspect
    score: float
    details: Dict[str, Any] = field(default_factory=dict)
    passed: bool = field(init=False)
    
    def __post_init__(self):
        self.passed = self.score >= self.details.get('min_score', 7.0)


@dataclass
class TestResult:
    test_name: str
    input_data: Dict[str, Any]
    output: str
    expected: Optional[str]
    aspect_scores: Dict[EvaluationAspect, AspectScore]
    overall_score: float
    passed: bool
    metadata: Dict[str, Any] = field(default_factory=dict)