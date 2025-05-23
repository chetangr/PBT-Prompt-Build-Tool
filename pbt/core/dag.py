"""Dependency Graph Management for Prompts - DBT-like DAG functionality"""

from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path
import yaml
import networkx as nx
from collections import defaultdict
import json


@dataclass
class PromptNode:
    """Represents a prompt in the dependency graph"""
    name: str
    path: Path
    depends_on: List[str] = field(default_factory=list)
    materialized: str = "view"  # view, table, incremental
    tags: List[str] = field(default_factory=list)
    description: str = ""
    config: Dict[str, Any] = field(default_factory=dict)
    

class PromptDAG:
    """Manages prompt dependencies and execution order"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.graph = nx.DiGraph()
        self.nodes: Dict[str, PromptNode] = {}
        
    def load_prompts(self, prompts_dir: Path = None) -> None:
        """Load all prompts and build dependency graph"""
        if prompts_dir is None:
            prompts_dir = self.project_root / "prompts"
            
        for prompt_file in prompts_dir.rglob("*.yaml"):
            self._load_prompt(prompt_file)
            
        self._validate_dag()
        
    def _load_prompt(self, prompt_path: Path) -> None:
        """Load a single prompt and add to graph"""
        with open(prompt_path, 'r') as f:
            data = yaml.safe_load(f)
            
        name = data.get('name', prompt_path.stem)
        node = PromptNode(
            name=name,
            path=prompt_path,
            depends_on=data.get('depends_on', []),
            materialized=data.get('config', {}).get('materialized', 'view'),
            tags=data.get('tags', []),
            description=data.get('description', ''),
            config=data.get('config', {})
        )
        
        self.nodes[name] = node
        self.graph.add_node(name, data=node)
        
        # Add dependencies
        for dep in node.depends_on:
            if dep.startswith('ref('):
                # Parse ref() syntax like DBT
                dep_name = dep[4:-1].strip("'\"")
                self.graph.add_edge(dep_name, name)
                
    def _validate_dag(self) -> None:
        """Validate the DAG has no cycles"""
        if not nx.is_directed_acyclic_graph(self.graph):
            cycles = list(nx.simple_cycles(self.graph))
            raise ValueError(f"Circular dependencies detected: {cycles}")
            
    def get_execution_order(self, target: Optional[str] = None) -> List[str]:
        """Get prompts in execution order"""
        if target:
            # Get all ancestors of target
            ancestors = nx.ancestors(self.graph, target)
            ancestors.add(target)
            subgraph = self.graph.subgraph(ancestors)
            return list(nx.topological_sort(subgraph))
        else:
            return list(nx.topological_sort(self.graph))
            
    def get_downstream(self, prompt_name: str) -> Set[str]:
        """Get all prompts that depend on this one"""
        return nx.descendants(self.graph, prompt_name)
        
    def get_upstream(self, prompt_name: str) -> Set[str]:
        """Get all prompts this one depends on"""
        return nx.ancestors(self.graph, prompt_name)
        
    def visualize(self, output_path: Path = None) -> None:
        """Generate a visual representation of the DAG"""
        try:
            import matplotlib.pyplot as plt
            
            pos = nx.spring_layout(self.graph)
            plt.figure(figsize=(12, 8))
            
            # Draw nodes with different colors based on materialization
            node_colors = []
            for node in self.graph.nodes():
                mat_type = self.nodes[node].materialized
                if mat_type == 'incremental':
                    node_colors.append('lightgreen')
                elif mat_type == 'table':
                    node_colors.append('lightblue')
                else:
                    node_colors.append('lightgray')
                    
            nx.draw(self.graph, pos, node_color=node_colors, 
                   with_labels=True, node_size=2000, font_size=10,
                   font_weight='bold', arrows=True)
            
            if output_path:
                plt.savefig(output_path)
            else:
                plt.show()
                
        except ImportError:
            print("Matplotlib not installed. Skipping visualization.")
            
    def to_mermaid(self) -> str:
        """Generate Mermaid diagram syntax for documentation"""
        lines = ["graph TD"]
        
        for node_name, node_data in self.nodes.items():
            # Add node with styling based on materialization
            if node_data.materialized == 'incremental':
                lines.append(f"    {node_name}[{node_name}]:::incremental")
            elif node_data.materialized == 'table':
                lines.append(f"    {node_name}[{node_name}]:::table")
            else:
                lines.append(f"    {node_name}[{node_name}]")
                
        # Add edges
        for source, target in self.graph.edges():
            lines.append(f"    {source} --> {target}")
            
        # Add styling
        lines.extend([
            "    classDef incremental fill:#90EE90,stroke:#333,stroke-width:2px;",
            "    classDef table fill:#ADD8E6,stroke:#333,stroke-width:2px;"
        ])
        
        return "\n".join(lines)
        
    def get_lineage(self, prompt_name: str) -> Dict[str, Any]:
        """Get full lineage information for a prompt"""
        if prompt_name not in self.nodes:
            raise ValueError(f"Prompt '{prompt_name}' not found")
            
        return {
            "prompt": prompt_name,
            "upstream": list(self.get_upstream(prompt_name)),
            "downstream": list(self.get_downstream(prompt_name)),
            "direct_dependencies": self.nodes[prompt_name].depends_on,
            "tags": self.nodes[prompt_name].tags,
            "materialized": self.nodes[prompt_name].materialized,
            "description": self.nodes[prompt_name].description
        }