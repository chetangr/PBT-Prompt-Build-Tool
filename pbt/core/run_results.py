"""Run results tracking - DBT-like execution history and metrics"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from pathlib import Path
import json
from datetime import datetime
import time
from enum import Enum


class RunStatus(Enum):
    """Status of a run execution"""
    SUCCESS = "success"
    ERROR = "error"
    SKIPPED = "skipped"
    WARN = "warn"
    

@dataclass
class TimingInfo:
    """Timing information for execution steps"""
    name: str
    started_at: str
    completed_at: str
    duration: float
    

@dataclass
class PromptRunResult:
    """Result of a single prompt execution"""
    unique_id: str
    status: RunStatus
    execution_time: float
    message: Optional[str] = None
    failures: Optional[List[Dict[str, Any]]] = None
    warnings: Optional[List[str]] = None
    timing: List[TimingInfo] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    

@dataclass
class RunResults:
    """Complete run results for a PBT execution"""
    run_id: str
    project_name: str
    started_at: str
    completed_at: str
    elapsed_time: float
    success: bool
    results: List[PromptRunResult]
    args: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    

class RunResultsManager:
    """Manages execution results and history"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.results_dir = project_root / ".pbt" / "run_results"
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.current_run: Optional[RunResults] = None
        self._start_times: Dict[str, float] = {}
        
    def start_run(self, project_name: str, args: Dict[str, Any]) -> str:
        """Start a new run and return run ID"""
        run_id = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
        
        self.current_run = RunResults(
            run_id=run_id,
            project_name=project_name,
            started_at=datetime.utcnow().isoformat(),
            completed_at="",
            elapsed_time=0.0,
            success=True,
            results=[],
            args=args,
            metadata={
                "pbt_version": "0.1.0",
                "python_version": "3.9+",
                "platform": "darwin"  # This should be dynamic
            }
        )
        
        self._start_times[run_id] = time.time()
        return run_id
        
    def start_prompt_execution(self, prompt_id: str) -> float:
        """Mark the start of a prompt execution"""
        self._start_times[prompt_id] = time.time()
        return self._start_times[prompt_id]
        
    def record_prompt_result(self, prompt_id: str, status: RunStatus, 
                           message: str = None, failures: List[Dict[str, Any]] = None,
                           warnings: List[str] = None, metadata: Dict[str, Any] = None) -> None:
        """Record the result of a prompt execution"""
        if not self.current_run:
            raise ValueError("No active run. Call start_run() first.")
            
        execution_time = time.time() - self._start_times.get(prompt_id, time.time())
        
        result = PromptRunResult(
            unique_id=prompt_id,
            status=status,
            execution_time=execution_time,
            message=message,
            failures=failures,
            warnings=warnings,
            metadata=metadata or {}
        )
        
        # Update overall success status
        if status in [RunStatus.ERROR, RunStatus.WARN]:
            self.current_run.success = False
            
        self.current_run.results.append(result)
        
    def add_timing(self, prompt_id: str, step_name: str, duration: float) -> None:
        """Add timing information for a specific step"""
        # Find the result for this prompt
        for result in self.current_run.results:
            if result.unique_id == prompt_id:
                timing = TimingInfo(
                    name=step_name,
                    started_at=datetime.utcnow().isoformat(),
                    completed_at=datetime.utcnow().isoformat(),
                    duration=duration
                )
                result.timing.append(timing)
                break
                
    def complete_run(self) -> RunResults:
        """Complete the current run and save results"""
        if not self.current_run:
            raise ValueError("No active run to complete")
            
        self.current_run.completed_at = datetime.utcnow().isoformat()
        self.current_run.elapsed_time = time.time() - self._start_times.get(self.current_run.run_id, 0)
        
        # Save to file
        self._save_results(self.current_run)
        
        # Save as latest
        self._save_latest(self.current_run)
        
        completed_run = self.current_run
        self.current_run = None
        
        return completed_run
        
    def _save_results(self, results: RunResults) -> None:
        """Save run results to timestamped file"""
        filename = f"run_results_{results.run_id}.json"
        filepath = self.results_dir / filename
        
        # Convert to dict with proper serialization
        results_dict = self._serialize_results(results)
        
        with open(filepath, 'w') as f:
            json.dump(results_dict, f, indent=2)
            
    def _save_latest(self, results: RunResults) -> None:
        """Save as latest run results"""
        latest_path = self.project_root / ".pbt" / "run_results.json"
        
        results_dict = self._serialize_results(results)
        
        with open(latest_path, 'w') as f:
            json.dump(results_dict, f, indent=2)
            
    def _serialize_results(self, results: RunResults) -> Dict[str, Any]:
        """Serialize RunResults to JSON-compatible dict"""
        results_dict = asdict(results)
        
        # Convert enum values
        for result in results_dict['results']:
            result['status'] = result['status'].value if isinstance(result['status'], RunStatus) else result['status']
            
        return results_dict
        
    def get_latest_results(self) -> Optional[RunResults]:
        """Get the most recent run results"""
        latest_path = self.project_root / ".pbt" / "run_results.json"
        
        if not latest_path.exists():
            return None
            
        with open(latest_path, 'r') as f:
            data = json.load(f)
            
        return self._deserialize_results(data)
        
    def get_run_history(self, limit: int = 10) -> List[RunResults]:
        """Get recent run history"""
        history = []
        
        # Get all run result files
        result_files = sorted(self.results_dir.glob("run_results_*.json"), reverse=True)
        
        for result_file in result_files[:limit]:
            with open(result_file, 'r') as f:
                data = json.load(f)
                
            history.append(self._deserialize_results(data))
            
        return history
        
    def _deserialize_results(self, data: Dict[str, Any]) -> RunResults:
        """Deserialize JSON data to RunResults object"""
        # Convert status strings back to enums
        for result in data['results']:
            result['status'] = RunStatus(result['status'])
            
        # Convert timing data
        for result in data['results']:
            result['timing'] = [TimingInfo(**t) for t in result.get('timing', [])]
            
        # Create PromptRunResult objects
        results = [PromptRunResult(**r) for r in data['results']]
        
        return RunResults(
            run_id=data['run_id'],
            project_name=data['project_name'],
            started_at=data['started_at'],
            completed_at=data['completed_at'],
            elapsed_time=data['elapsed_time'],
            success=data['success'],
            results=results,
            args=data['args'],
            metadata=data.get('metadata', {})
        )
        
    def generate_summary(self, results: RunResults = None) -> str:
        """Generate a human-readable summary of run results"""
        if results is None:
            results = self.get_latest_results()
            
        if not results:
            return "No run results found"
            
        # Count statuses
        status_counts = {
            RunStatus.SUCCESS: 0,
            RunStatus.ERROR: 0,
            RunStatus.SKIPPED: 0,
            RunStatus.WARN: 0
        }
        
        total_time = 0.0
        
        for result in results.results:
            status_counts[result.status] += 1
            total_time += result.execution_time
            
        summary = [
            f"Run ID: {results.run_id}",
            f"Project: {results.project_name}",
            f"Started: {results.started_at}",
            f"Completed: {results.completed_at}",
            f"Total Duration: {results.elapsed_time:.2f}s",
            f"Overall Status: {'SUCCESS' if results.success else 'FAILED'}",
            "",
            "Results Summary:",
            f"  Successful: {status_counts[RunStatus.SUCCESS]}",
            f"  Errors: {status_counts[RunStatus.ERROR]}",
            f"  Warnings: {status_counts[RunStatus.WARN]}",
            f"  Skipped: {status_counts[RunStatus.SKIPPED]}",
            f"  Total Execution Time: {total_time:.2f}s",
            ""
        ]
        
        # Add failed prompts if any
        failed = [r for r in results.results if r.status == RunStatus.ERROR]
        if failed:
            summary.append("Failed Prompts:")
            for result in failed:
                summary.append(f"  - {result.unique_id}: {result.message or 'No message'}")
                
        return '\n'.join(summary)
        
    def export_metrics(self, output_path: Path = None) -> Dict[str, Any]:
        """Export execution metrics for monitoring"""
        history = self.get_run_history(limit=100)
        
        metrics = {
            "total_runs": len(history),
            "success_rate": 0.0,
            "average_duration": 0.0,
            "prompts_per_run": 0.0,
            "failure_reasons": {},
            "performance_trend": []
        }
        
        if not history:
            return metrics
            
        # Calculate metrics
        successful_runs = sum(1 for r in history if r.success)
        metrics["success_rate"] = successful_runs / len(history)
        
        total_duration = sum(r.elapsed_time for r in history)
        metrics["average_duration"] = total_duration / len(history)
        
        total_prompts = sum(len(r.results) for r in history)
        metrics["prompts_per_run"] = total_prompts / len(history)
        
        # Analyze failure reasons
        for run in history:
            for result in run.results:
                if result.status == RunStatus.ERROR and result.message:
                    reason = result.message[:50]  # Truncate for grouping
                    metrics["failure_reasons"][reason] = metrics["failure_reasons"].get(reason, 0) + 1
                    
        # Performance trend (last 10 runs)
        for run in history[:10]:
            metrics["performance_trend"].append({
                "run_id": run.run_id,
                "duration": run.elapsed_time,
                "success": run.success,
                "prompt_count": len(run.results)
            })
            
        if output_path:
            with open(output_path, 'w') as f:
                json.dump(metrics, f, indent=2)
                
        return metrics