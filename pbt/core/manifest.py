"""Manifest Generation - DBT-like documentation and metadata management"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from pathlib import Path
import yaml
import json
from datetime import datetime
import hashlib


@dataclass
class PromptMetadata:
    """Metadata for a single prompt"""
    name: str
    path: str
    version: str
    description: str
    checksum: str
    created_at: str
    updated_at: str
    tags: List[str] = field(default_factory=list)
    variables: List[str] = field(default_factory=list)
    examples: List[Dict[str, Any]] = field(default_factory=list)
    tests: List[Dict[str, Any]] = field(default_factory=list)
    depends_on: List[str] = field(default_factory=list)
    model_config: Dict[str, Any] = field(default_factory=dict)
    

@dataclass
class TestMetadata:
    """Metadata for prompt tests"""
    name: str
    type: str  # unit, integration, performance
    prompt_ref: str
    assertions: List[Dict[str, Any]] = field(default_factory=list)
    last_run: Optional[str] = None
    last_status: Optional[str] = None
    

class Manifest:
    """Manages prompt project manifest - similar to DBT's manifest.json"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.prompts: Dict[str, PromptMetadata] = {}
        self.tests: Dict[str, TestMetadata] = {}
        self.metadata = {
            "generated_at": datetime.utcnow().isoformat(),
            "pbt_version": "0.1.0",
            "project_name": self._get_project_name()
        }
        
    def _get_project_name(self) -> str:
        """Get project name from pbt.yaml"""
        config_path = self.project_root / "pbt.yaml"
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                return config.get('name', 'unnamed_project')
        return 'unnamed_project'
        
    def _calculate_checksum(self, content: str) -> str:
        """Calculate checksum for content"""
        return hashlib.sha256(content.encode()).hexdigest()
        
    def load_prompts(self, prompts_dir: Path = None) -> None:
        """Load all prompts and generate metadata"""
        if prompts_dir is None:
            prompts_dir = self.project_root / "prompts"
            
        for prompt_file in prompts_dir.rglob("*.yaml"):
            self._load_prompt_metadata(prompt_file)
            
    def _load_prompt_metadata(self, prompt_path: Path) -> None:
        """Load metadata for a single prompt"""
        with open(prompt_path, 'r') as f:
            content = f.read()
            data = yaml.safe_load(content)
            
        name = data.get('name', prompt_path.stem)
        
        # Get file timestamps
        stat = prompt_path.stat()
        created_at = datetime.fromtimestamp(stat.st_ctime).isoformat()
        updated_at = datetime.fromtimestamp(stat.st_mtime).isoformat()
        
        metadata = PromptMetadata(
            name=name,
            path=str(prompt_path.relative_to(self.project_root)),
            version=data.get('version', '1.0.0'),
            description=data.get('description', ''),
            checksum=self._calculate_checksum(content),
            created_at=created_at,
            updated_at=updated_at,
            tags=data.get('tags', []),
            variables=data.get('variables', []),
            examples=data.get('examples', []),
            tests=data.get('tests', []),
            depends_on=data.get('depends_on', []),
            model_config=data.get('model_config', {})
        )
        
        self.prompts[name] = metadata
        
    def load_tests(self, tests_dir: Path = None) -> None:
        """Load all test definitions"""
        if tests_dir is None:
            tests_dir = self.project_root / "tests"
            
        if not tests_dir.exists():
            return
            
        for test_file in tests_dir.rglob("*.yaml"):
            self._load_test_metadata(test_file)
            
    def _load_test_metadata(self, test_path: Path) -> None:
        """Load metadata for a single test"""
        with open(test_path, 'r') as f:
            data = yaml.safe_load(f)
            
        for test in data.get('tests', []):
            name = test.get('name', test_path.stem)
            metadata = TestMetadata(
                name=name,
                type=test.get('type', 'unit'),
                prompt_ref=test.get('prompt_ref', ''),
                assertions=test.get('assertions', [])
            )
            
            self.tests[name] = metadata
            
    def generate_docs(self, output_dir: Path = None) -> None:
        """Generate documentation from manifest"""
        if output_dir is None:
            output_dir = self.project_root / "docs" / "generated"
            
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate index
        self._generate_index(output_dir)
        
        # Generate prompt pages
        for prompt_name, prompt_meta in self.prompts.items():
            self._generate_prompt_doc(prompt_name, prompt_meta, output_dir)
            
        # Generate lineage diagram
        self._generate_lineage_diagram(output_dir)
        
    def _generate_index(self, output_dir: Path) -> None:
        """Generate documentation index"""
        content = [
            f"# {self.metadata['project_name']} - Prompt Documentation",
            f"\nGenerated at: {self.metadata['generated_at']}",
            f"\nPBT Version: {self.metadata['pbt_version']}",
            "\n## Prompts\n"
        ]
        
        # Group prompts by tags
        prompts_by_tag = {}
        for name, meta in self.prompts.items():
            for tag in meta.tags or ['untagged']:
                if tag not in prompts_by_tag:
                    prompts_by_tag[tag] = []
                prompts_by_tag[tag].append((name, meta))
                
        for tag, prompts in sorted(prompts_by_tag.items()):
            content.append(f"\n### {tag}\n")
            for name, meta in sorted(prompts):
                content.append(f"- [{name}](./{name}.md) - {meta.description}")
                
        with open(output_dir / "index.md", 'w') as f:
            f.write('\n'.join(content))
            
    def _generate_prompt_doc(self, name: str, meta: PromptMetadata, output_dir: Path) -> None:
        """Generate documentation for a single prompt"""
        content = [
            f"# {name}",
            f"\n{meta.description}",
            f"\n**Version:** {meta.version}",
            f"\n**Path:** `{meta.path}`",
            f"\n**Created:** {meta.created_at}",
            f"\n**Updated:** {meta.updated_at}",
            f"\n**Checksum:** `{meta.checksum}`"
        ]
        
        if meta.tags:
            content.append(f"\n**Tags:** {', '.join(meta.tags)}")
            
        if meta.depends_on:
            content.append("\n## Dependencies")
            for dep in meta.depends_on:
                content.append(f"- {dep}")
                
        if meta.variables:
            content.append("\n## Variables")
            for var in meta.variables:
                content.append(f"- `{var}`")
                
        if meta.examples:
            content.append("\n## Examples")
            for i, example in enumerate(meta.examples, 1):
                content.append(f"\n### Example {i}")
                content.append("```yaml")
                content.append(yaml.dump(example, default_flow_style=False))
                content.append("```")
                
        if meta.model_config:
            content.append("\n## Model Configuration")
            content.append("```yaml")
            content.append(yaml.dump(meta.model_config, default_flow_style=False))
            content.append("```")
            
        with open(output_dir / f"{name}.md", 'w') as f:
            f.write('\n'.join(content))
            
    def _generate_lineage_diagram(self, output_dir: Path) -> None:
        """Generate lineage diagram in Mermaid format"""
        content = ["# Prompt Lineage", "\n```mermaid", "graph TD"]
        
        # Add nodes
        for name in self.prompts:
            content.append(f"    {name}")
            
        # Add edges based on dependencies
        for name, meta in self.prompts.items():
            for dep in meta.depends_on:
                if dep.startswith('ref('):
                    dep_name = dep[4:-1].strip("'\"")
                    content.append(f"    {dep_name} --> {name}")
                    
        content.append("```")
        
        with open(output_dir / "lineage.md", 'w') as f:
            f.write('\n'.join(content))
            
    def to_json(self, output_path: Path = None) -> str:
        """Export manifest as JSON"""
        manifest = {
            "metadata": self.metadata,
            "prompts": {k: asdict(v) for k, v in self.prompts.items()},
            "tests": {k: asdict(v) for k, v in self.tests.items()}
        }
        
        json_str = json.dumps(manifest, indent=2)
        
        if output_path:
            with open(output_path, 'w') as f:
                f.write(json_str)
                
        return json_str
        
    def validate_freshness(self) -> List[Dict[str, Any]]:
        """Check if prompts have been modified without updating version"""
        stale_prompts = []
        
        for name, meta in self.prompts.items():
            prompt_path = self.project_root / meta.path
            if prompt_path.exists():
                with open(prompt_path, 'r') as f:
                    current_checksum = self._calculate_checksum(f.read())
                    
                if current_checksum != meta.checksum:
                    stale_prompts.append({
                        "name": name,
                        "path": meta.path,
                        "expected_checksum": meta.checksum,
                        "actual_checksum": current_checksum,
                        "message": "Prompt has been modified without version update"
                    })
                    
        return stale_prompts