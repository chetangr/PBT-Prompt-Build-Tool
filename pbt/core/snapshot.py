"""Snapshot functionality for tracking prompt changes over time - DBT-like snapshots"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import yaml
import json
from datetime import datetime
import hashlib
import shutil
from difflib import unified_diff


@dataclass
class PromptSnapshot:
    """Represents a point-in-time snapshot of a prompt"""
    prompt_name: str
    version: str
    content: str
    checksum: str
    timestamp: str
    metadata: Dict[str, Any]
    

class SnapshotManager:
    """Manages prompt snapshots for version tracking and comparison"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.snapshots_dir = project_root / ".pbt" / "snapshots"
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)
        
    def create_snapshot(self, prompt_path: Path, reason: str = "") -> PromptSnapshot:
        """Create a snapshot of a prompt"""
        with open(prompt_path, 'r') as f:
            content = f.read()
            data = yaml.safe_load(content)
            
        prompt_name = data.get('name', prompt_path.stem)
        version = data.get('version', '1.0.0')
        timestamp = datetime.utcnow().isoformat()
        checksum = hashlib.sha256(content.encode()).hexdigest()
        
        snapshot = PromptSnapshot(
            prompt_name=prompt_name,
            version=version,
            content=content,
            checksum=checksum,
            timestamp=timestamp,
            metadata={
                "reason": reason,
                "path": str(prompt_path.relative_to(self.project_root)),
                "tags": data.get('tags', []),
                "variables": data.get('variables', [])
            }
        )
        
        self._save_snapshot(snapshot)
        return snapshot
        
    def _save_snapshot(self, snapshot: PromptSnapshot) -> None:
        """Save snapshot to disk"""
        # Create directory for this prompt
        prompt_dir = self.snapshots_dir / snapshot.prompt_name
        prompt_dir.mkdir(exist_ok=True)
        
        # Save snapshot with timestamp
        filename = f"{snapshot.timestamp.replace(':', '-')}.yaml"
        filepath = prompt_dir / filename
        
        snapshot_data = {
            "prompt_name": snapshot.prompt_name,
            "version": snapshot.version,
            "checksum": snapshot.checksum,
            "timestamp": snapshot.timestamp,
            "metadata": snapshot.metadata,
            "content": snapshot.content
        }
        
        with open(filepath, 'w') as f:
            yaml.dump(snapshot_data, f, default_flow_style=False)
            
    def get_snapshots(self, prompt_name: str) -> List[PromptSnapshot]:
        """Get all snapshots for a prompt"""
        prompt_dir = self.snapshots_dir / prompt_name
        if not prompt_dir.exists():
            return []
            
        snapshots = []
        for snapshot_file in sorted(prompt_dir.glob("*.yaml")):
            with open(snapshot_file, 'r') as f:
                data = yaml.safe_load(f)
                
            snapshot = PromptSnapshot(
                prompt_name=data['prompt_name'],
                version=data['version'],
                content=data['content'],
                checksum=data['checksum'],
                timestamp=data['timestamp'],
                metadata=data['metadata']
            )
            snapshots.append(snapshot)
            
        return snapshots
        
    def diff_snapshots(self, prompt_name: str, timestamp1: str = None, timestamp2: str = None) -> str:
        """Compare two snapshots or latest with previous"""
        snapshots = self.get_snapshots(prompt_name)
        
        if len(snapshots) < 2:
            return "Not enough snapshots to compare"
            
        # If no timestamps provided, compare latest two
        if timestamp1 is None and timestamp2 is None:
            snap1 = snapshots[-2]
            snap2 = snapshots[-1]
        else:
            # Find snapshots by timestamp
            snap1 = next((s for s in snapshots if s.timestamp == timestamp1), None)
            snap2 = next((s for s in snapshots if s.timestamp == timestamp2), None)
            
            if not snap1 or not snap2:
                return "Snapshots not found for given timestamps"
                
        # Generate unified diff
        lines1 = snap1.content.splitlines(keepends=True)
        lines2 = snap2.content.splitlines(keepends=True)
        
        diff = unified_diff(
            lines1, lines2,
            fromfile=f"{prompt_name} @ {snap1.timestamp}",
            tofile=f"{prompt_name} @ {snap2.timestamp}",
            lineterm=''
        )
        
        return ''.join(diff)
        
    def snapshot_all(self, reason: str = "Manual snapshot") -> Dict[str, PromptSnapshot]:
        """Create snapshots for all prompts"""
        snapshots = {}
        prompts_dir = self.project_root / "prompts"
        
        if prompts_dir.exists():
            for prompt_file in prompts_dir.rglob("*.yaml"):
                try:
                    snapshot = self.create_snapshot(prompt_file, reason)
                    snapshots[snapshot.prompt_name] = snapshot
                except Exception as e:
                    print(f"Error snapshotting {prompt_file}: {e}")
                    
        return snapshots
        
    def restore_snapshot(self, prompt_name: str, timestamp: str, backup: bool = True) -> bool:
        """Restore a prompt from a snapshot"""
        snapshots = self.get_snapshots(prompt_name)
        snapshot = next((s for s in snapshots if s.timestamp == timestamp), None)
        
        if not snapshot:
            return False
            
        # Find current prompt file
        prompt_path = None
        prompts_dir = self.project_root / "prompts"
        
        for p in prompts_dir.rglob("*.yaml"):
            with open(p, 'r') as f:
                data = yaml.safe_load(f)
                if data.get('name') == prompt_name:
                    prompt_path = p
                    break
                    
        if not prompt_path:
            # Create new file if doesn't exist
            prompt_path = prompts_dir / f"{prompt_name}.yaml"
            
        # Backup current version if exists and requested
        if backup and prompt_path.exists():
            self.create_snapshot(prompt_path, reason="Pre-restore backup")
            
        # Restore content
        with open(prompt_path, 'w') as f:
            f.write(snapshot.content)
            
        return True
        
    def get_history(self, prompt_name: str) -> List[Dict[str, Any]]:
        """Get change history for a prompt"""
        snapshots = self.get_snapshots(prompt_name)
        
        history = []
        for i, snapshot in enumerate(snapshots):
            entry = {
                "timestamp": snapshot.timestamp,
                "version": snapshot.version,
                "checksum": snapshot.checksum,
                "reason": snapshot.metadata.get('reason', ''),
                "changes": ""
            }
            
            # Calculate changes from previous
            if i > 0:
                prev_snapshot = snapshots[i-1]
                if snapshot.checksum != prev_snapshot.checksum:
                    entry["changes"] = f"Modified (version {prev_snapshot.version} → {snapshot.version})"
                else:
                    entry["changes"] = "No changes"
                    
            history.append(entry)
            
        return history
        
    def cleanup_old_snapshots(self, keep_last: int = 10) -> int:
        """Remove old snapshots, keeping only the most recent ones"""
        removed_count = 0
        
        for prompt_dir in self.snapshots_dir.iterdir():
            if prompt_dir.is_dir():
                snapshots = sorted(prompt_dir.glob("*.yaml"))
                
                if len(snapshots) > keep_last:
                    for snapshot_file in snapshots[:-keep_last]:
                        snapshot_file.unlink()
                        removed_count += 1
                        
        return removed_count