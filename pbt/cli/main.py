#!/usr/bin/env python3
"""
PBT CLI - Main entry point
"""

# Load .env files before any other imports
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load from current directory and upward
except ImportError:
    pass

import typer
from typing import Optional, List, Dict
from pathlib import Path
import yaml
import json
import os
import sys
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax

from pbt.core.config import PBTConfig
from pbt.core.project import PBTProject
from pbt.core.generator import PromptGenerator
from pbt.core.evaluator import PromptEvaluator
from pbt.core.deployer import PromptDeployer
from pbt.__version__ import __version__

app = typer.Typer(
    name="pbt",
    help="🚀 Prompt Build Tool - Infrastructure-grade prompt engineering for AI teams",
    add_completion=False,
    rich_markup_mode="rich"
)

console = Console()

def version_callback(value: bool):
    if value:
        console.print(f"[bold blue]PBT (Prompt Build Tool)[/bold blue] version [green]{__version__}[/green]")
        console.print("\n[dim]To get started:[/dim]")
        console.print("1. [cyan]pbt init[/cyan] - Initialize new project")
        console.print("2. Add [yellow]ANTHROPIC_API_KEY[/yellow] to .env file")
        console.print("3. [cyan]pbt generate --goal 'Your prompt goal'[/cyan]")
        console.print("\n[dim]Need API keys? See: API_KEYS.md[/dim]")
        raise typer.Exit()

def show_welcome_screen():
    """Display welcome screen with introduction and getting started guide"""
    console.print()
    console.print("[bold blue]🚀 Welcome to PBT (Prompt Build Tool)[/bold blue]")
    console.print(f"[dim]Version {__version__}[/dim]")
    console.print()
    
    # Main description
    console.print("[bold]Infrastructure-grade prompt engineering for AI teams[/bold]")
    console.print("PBT is like [yellow]dbt + Terraform[/yellow] for LLM prompts - build, test, and deploy")
    console.print("prompts across Claude, GPT-4, Mistral, and more.")
    console.print()
    
    # Key features
    console.print("[bold cyan]✨ Key Features:[/bold cyan]")
    features = [
        "🎯 AI-powered prompt generation",
        "🧪 Cross-model testing & comparison", 
        "📦 Prompt packs for team collaboration",
        "🔄 Convert existing agent code to PBT",
        "📊 Claude-based evaluation judge",
        "🌐 Visual IDE + CLI interface",
        "🔒 Enterprise auth & marketplace"
    ]
    
    for feature in features:
        console.print(f"  {feature}")
    console.print()
    
    # Getting started
    console.print("[bold green]🚀 Quick Start (2 minutes):[/bold green]")
    console.print()
    console.print("[bold]1. Initialize your first project:[/bold]")
    console.print("   [cyan]pbt init my-prompts[/cyan]")
    console.print("   [cyan]cd my-prompts[/cyan]")
    console.print()
    
    console.print("[bold]2. Add your API key:[/bold]")
    console.print("   [cyan]cp .env.example .env[/cyan]")
    console.print("   [dim]# Edit .env and add: ANTHROPIC_API_KEY=sk-ant-your-key[/dim]")
    console.print("   [dim]# Get key from: https://console.anthropic.com[/dim]")
    console.print()
    
    console.print("[bold]3. Generate your first prompt:[/bold]")
    console.print("   [cyan]pbt generate --goal \"Summarize customer feedback\"[/cyan]")
    console.print()
    
    console.print("[bold]4. Test it:[/bold]")
    console.print("   [cyan]pbt test *.prompt.yaml[/cyan]")
    console.print()
    
    # Use cases
    console.print("[bold magenta]🎯 Common Use Cases:[/bold magenta]")
    use_cases = [
        "[bold]Convert existing agents:[/bold] [cyan]pbt convert your_agent.py[/cyan]",
        "[bold]Compare models:[/bold] [cyan]pbt compare --prompt \"Hello\" --models claude gpt-4[/cyan]",
        "[bold]Start web UI:[/bold] [cyan]pbt serve[/cyan]",
        "[bold]Deploy prompts:[/bold] [cyan]pbt deploy --provider supabase[/cyan]"
    ]
    
    for use_case in use_cases:
        console.print(f"  • {use_case}")
    console.print()
    
    # Command reference
    console.print("[bold yellow]📚 Available Commands:[/bold yellow]")
    commands = [
        ("init", "Initialize new PBT project"),
        ("generate", "AI-powered prompt generation"),
        ("test", "Test prompts with evaluation"),
        ("compare", "Compare across models"),
        ("convert", "Convert Python agents to PBT"),
        ("serve", "Start web interface"),
        ("deploy", "Deploy to cloud providers"),
        ("eval", "Run evaluations")
    ]
    
    for cmd, desc in commands:
        console.print(f"  [cyan]pbt {cmd:<10}[/cyan] {desc}")
    console.print()
    
    console.print("[dim]💡 Tip: Run [cyan]pbt <command> --help[/cyan] for detailed usage[/dim]")
    console.print("[dim]📖 Full docs: https://github.com/your-org/prompt-build-tool[/dim]")
    console.print()

@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: Optional[bool] = typer.Option(
        None, 
        "--version", 
        "-v",
        callback=version_callback,
        help="Show version and exit"
    ),
    verbose: bool = typer.Option(False, "--verbose", help="Enable verbose output"),
    config_file: Optional[Path] = typer.Option(None, "--config", help="Path to config file")
):
    """
    🚀 Prompt Build Tool (PBT)
    
    Infrastructure-grade prompt engineering for AI teams working across LLMs,
    multimodal models, and agent workflows.
    """
    if verbose:
        console.print("[dim]Verbose mode enabled[/dim]")
    
    # If no command is provided, show welcome screen
    if ctx.invoked_subcommand is None:
        show_welcome_screen()

@app.command()
def init(
    name: Optional[str] = typer.Option(None, "--name", help="Project name"),
    directory: Optional[Path] = typer.Option(None, "--directory", help="Project directory"),
    template: Optional[str] = typer.Option("default", "--template", help="Project template")
):
    """
    🔧 Initialize a new PBT project
    
    Creates project structure with prompts/, tests/, and pbt.yaml configuration.
    """
    project_dir = directory or Path.cwd()
    project_name = name or project_dir.name
    
    console.print(f"[bold blue]🚀 Initializing PBT project: {project_name}[/bold blue]")
    
    try:
        project = PBTProject.init(project_dir, project_name, template)
        
        console.print(f"[green]✅ Project initialized in {project_dir}[/green]")
        console.print("\n[bold]Created structure:[/bold]")
        console.print("📁 prompts/")
        console.print("📁 tests/") 
        console.print("📁 evaluations/")
        console.print("📄 pbt.yaml")
        console.print("📄 .env.example")
        
        console.print(f"\n[yellow]Next steps:[/yellow]")
        console.print("1. Copy .env.example to .env and add your API keys")
        console.print("2. Run: [bold]pbt generate --goal 'Your prompt goal'[/bold]")
        console.print("3. Run: [bold]pbt test your_prompt.yaml[/bold]")
        
    except Exception as e:
        console.print(f"[red]❌ Error initializing project: {e}[/red]")
        raise typer.Exit(1)

@app.command()
def generate(
    goal: str = typer.Option(..., "--goal", help="Description of what the prompt should accomplish"),
    model: str = typer.Option("claude", "--model", help="LLM to use for generation"),
    style: str = typer.Option("professional", "--style", help="Prompt style"),
    variables: Optional[str] = typer.Option(None, "--variables", help="Comma-separated variable names"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path"),
    generate_tests: bool = typer.Option(True, "--tests/--no-tests", help="Generate JSONL test file"),
    num_tests: int = typer.Option(6, "--num-tests", help="Number of test cases to generate")
):
    """
    🤖 Generate a prompt using AI
    
    Uses Claude or GPT-4 to generate structured prompt templates from goals.
    """
    console.print(f"[bold blue]🤖 Generating prompt for: {goal}[/bold blue]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Generating prompt...", total=None)
        
        try:
            generator = PromptGenerator()
            
            var_list = variables.split(',') if variables else []
            var_list = [v.strip() for v in var_list if v.strip()]
            
            result = generator.generate(
                goal=goal,
                model=model,
                style=style,
                variables=var_list
            )
            
            progress.update(task, description="✅ Generation complete!")
            
            if result.get("success"):
                prompt_yaml = result.get("prompt_yaml")
                
                # Save to file
                filename = output or f"{prompt_yaml['name']}.prompt.yaml"
                with open(filename, 'w') as f:
                    yaml.dump(prompt_yaml, f, indent=2)
                
                console.print(f"\n[green]✅ Generated prompt saved to: {filename}[/green]")
                
                # Generate JSONL tests if requested
                if generate_tests:
                    progress.update(task, description="Generating test cases...")
                    
                    # Read the saved prompt file
                    with open(filename, 'r') as f:
                        prompt_content = f.read()
                    
                    test_result = generator.generate_jsonl_tests(prompt_content, num_tests)
                    
                    if test_result.get("success"):
                        test_cases = test_result.get("test_cases", [])
                        
                        # Determine test file name
                        prompt_name = Path(filename).stem.replace('.prompt', '')
                        test_filename = f"tests/{prompt_name}.test.jsonl"
                        
                        # Create tests directory if it doesn't exist
                        os.makedirs("tests", exist_ok=True)
                        
                        # Save JSONL tests
                        if generator.save_jsonl_tests(test_cases, test_filename):
                            console.print(f"[green]✅ Generated {len(test_cases)} test cases: {test_filename}[/green]")
                        else:
                            console.print(f"[red]❌ Failed to save test cases[/red]")
                    else:
                        console.print(f"[yellow]⚠️ Failed to generate test cases: {test_result.get('error', 'Unknown error')}[/yellow]")
                
                # Show preview
                console.print("\n[bold]Preview:[/bold]")
                yaml_content = yaml.dump(prompt_yaml, indent=2)
                syntax = Syntax(yaml_content, "yaml", theme="monokai", line_numbers=True)
                console.print(Panel(syntax, title="Generated Prompt", expand=False))
                
            else:
                console.print(f"\n[yellow]⚠️ Generated raw content:[/yellow]")
                console.print(result.get('raw_content', 'No content'))
                
        except Exception as e:
            console.print(f"[red]❌ Error generating prompt: {e}[/red]")
            raise typer.Exit(1)

def find_prompt_file(filename: str) -> Optional[Path]:
    """
    Auto-locate prompt file in common directories
    
    Args:
        filename: Name of the prompt file to find
        
    Returns:
        Path to the file if found, None otherwise
    """
    current_dir = Path.cwd()
    
    # Common directories to search
    search_dirs = [
        current_dir,                    # Current directory
        current_dir / "prompts",        # prompts/
        current_dir / "agents",         # agents/
        current_dir / "templates",      # templates/
        current_dir / "prompt_packs",   # prompt_packs/
        current_dir / "packs",          # packs/
    ]
    
    # Also search subdirectories up to 2 levels deep
    for pattern in ["**/*.prompt.yaml", "**/*.yaml", "**/*.yml"]:
        for file_path in current_dir.glob(pattern):
            if file_path.name == filename or file_path.stem == Path(filename).stem:
                return file_path
    
    # Search in each directory
    for search_dir in search_dirs:
        if search_dir.exists():
            # Try exact filename
            candidate = search_dir / filename
            if candidate.exists():
                return candidate
            
            # Try with .prompt.yaml extension
            if not filename.endswith(('.yaml', '.yml')):
                candidate = search_dir / f"{filename}.prompt.yaml"
                if candidate.exists():
                    return candidate
                
                candidate = search_dir / f"{filename}.yaml"
                if candidate.exists():
                    return candidate
    
    return None

@app.command()
def test(
    target: str = typer.Argument(..., help="Test file (tests/test_*.yaml) or prompt file to test"),
    num_tests: int = typer.Option(5, "--num-tests", "-n", help="Number of test cases to generate (if auto-generating)"),
    test_type: str = typer.Option("functional", "--test-type", help="Type of tests (functional, edge_case, performance)"),
    model: str = typer.Option("claude", "--model", help="Model to test with"),
    save_results: bool = typer.Option(True, "--save/--no-save", help="Save test results to file")
):
    """
    🧪 Test prompts using test cases
    
    Two modes:
    1. Run specific test file: pbt test tests/test_summarizer.yaml
    2. Auto-generate tests for prompt: pbt test agents/summarizer.prompt.yaml
    
    Test files should be in tests/ directory and reference prompt_file.
    """
    # Determine if this is a test file or prompt file
    target_path = Path(target)
    
    if not target_path.exists():
        # Try to auto-locate the file
        console.print(f"[yellow]🔍 File not found at: {target}[/yellow]")
        console.print("[cyan]🔎 Searching for file in project directories...[/cyan]")
        
        found_path = find_prompt_file(target)
        if found_path:
            target_path = found_path
            console.print(f"[green]✅ Found file at: {target_path}[/green]")
        else:
            console.print(f"[red]❌ Could not locate file: {target}[/red]")
            console.print("\n[yellow]💡 Searched in:[/yellow]")
            search_locations = [
                "tests/ (for test files)",
                "agents/ (for prompt files)",
                "prompts/ (for prompt files)",
                "Current directory"
            ]
            for location in search_locations:
                console.print(f"   • {location}")
            
            console.print(f"\n[cyan]💡 Examples:[/cyan]")
            console.print(f"   • [cyan]pbt test tests/test_summarizer.yaml[/cyan]")
            console.print(f"   • [cyan]pbt test agents/summarizer.prompt.yaml[/cyan]")
            raise typer.Exit(1)
    
    # Check if it's a test file or prompt file
    if target_path.name.startswith('test_') or 'tests/' in str(target_path):
        # It's a test file - run defined test cases
        console.print(f"[green]📋 Running test file: {target_path}[/green]")
        run_test_file(target_path, model, save_results)
    else:
        # It's a prompt file - auto-generate tests
        console.print(f"[green]📁 Auto-generating tests for prompt: {target_path}[/green]")
        run_auto_generated_tests(target_path, num_tests, test_type, model, save_results)

def run_test_file(test_file_path: Path, model: str, save_results: bool):
    """Run tests from a dedicated test file"""
    console.print(f"[bold blue]🧪 Running test cases from: {test_file_path}[/bold blue]")
    
    # Load test file
    with open(test_file_path) as f:
        test_data = yaml.safe_load(f)
    
    prompt_file_ref = test_data.get('prompt_file')
    if not prompt_file_ref:
        console.print("[red]❌ Test file must specify 'prompt_file' field[/red]")
        raise typer.Exit(1)
    
    # Load the referenced prompt file
    prompt_path = Path(prompt_file_ref)
    if not prompt_path.exists():
        # Try to find the file in common locations
        found_path = find_prompt_file(prompt_file_ref)
        if found_path:
            prompt_path = found_path
            console.print(f"[green]✅ Found prompt file at: {prompt_path}[/green]")
        else:
            console.print(f"[red]❌ Referenced prompt file not found: {prompt_file_ref}[/red]")
            raise typer.Exit(1)
    
    console.print(f"[cyan]🎯 Testing prompt: {prompt_path}[/cyan]")
    console.print(f"[cyan]📝 Test cases: {len(test_data.get('tests', []))}[/cyan]")
    
    # Check for performance tests
    perf_tests = test_data.get('performance_tests', [])
    if perf_tests:
        console.print(f"[cyan]⚡ Performance tests: {len(perf_tests)}[/cyan]")
    
    # Run the tests using the new agent testing method
    evaluator = PromptEvaluator()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Running test cases...", total=None)
        
        # Use the new test_agent_with_file method
        run_result = evaluator.test_agent_with_file(
            str(prompt_path), str(test_file_path), model
        )
        
        progress.update(task, description="✅ Tests complete!")
    
    # Display results
    display_test_results(run_result, save_results, test_file_path.name)
    
    # Display performance results if available
    if 'performance_results' in run_result:
        display_performance_results(run_result['performance_results'])

def display_test_results(run_result: Dict, save_results: bool, test_source: str = "prompt"):
    """Display test results in a formatted table"""
    # Display results
    summary = run_result.get("summary", {})
    results = run_result.get("results", [])
    
    console.print(f"\n[bold]📊 Test Results from {test_source}:[/bold]")
    
    # Create results table
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Test", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Score", justify="center")
    
    for result in results:
        status = "✅ PASS" if result.get("passed") else "❌ FAIL"
        status_style = "green" if result.get("passed") else "red"
        table.add_row(
            result.get("test_name", "Unknown"),
            f"[{status_style}]{status}[/{status_style}]",
            "✓" if result.get("passed") else "✗"
        )
    
    console.print(table)
    
    # Summary
    pass_rate = summary.get('pass_rate', 0) * 100
    console.print(f"\n[bold]Summary:[/bold]")
    console.print(f"Total: {summary.get('total', 0)}")
    console.print(f"Passed: [green]{summary.get('passed', 0)}[/green]")
    console.print(f"Failed: [red]{summary.get('failed', 0)}[/red]")
    console.print(f"Pass Rate: [{'green' if pass_rate >= 80 else 'yellow' if pass_rate >= 60 else 'red'}]{pass_rate:.1f}%[/]")
    
    # Save results
    if save_results:
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"evaluations/test_results_{timestamp}.json"
        
        os.makedirs("evaluations", exist_ok=True)
        with open(results_file, 'w') as f:
            json.dump(run_result, f, indent=2)
        
        console.print(f"\n[dim]💾 Results saved to: {results_file}[/dim]")

def run_auto_generated_tests(prompt_path: Path, num_tests: int, test_type: str, model: str, save_results: bool):
    """Run auto-generated tests for a prompt file"""
    console.print(f"[bold blue]🧪 Auto-generating {num_tests} tests for: {prompt_path}[/bold blue]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        # Load prompt
        task1 = progress.add_task("Loading prompt...", total=None)
        with open(prompt_path) as f:
            prompt_content = f.read()
        
        # Generate tests
        progress.update(task1, description="Generating test cases...")
        evaluator = PromptEvaluator()
        
        test_result = evaluator.generate_tests(
            prompt_content, num_tests, test_type
        )
        
        if not test_result.get("success"):
            console.print(f"[red]❌ Failed to generate test cases[/red]")
            raise typer.Exit(1)
        
        tests = test_result.get("tests", [])
        progress.update(task1, description=f"Generated {len(tests)} test cases")
        
        # Run tests
        progress.update(task1, description="Running tests...")
        prompt_data = yaml.safe_load(prompt_content)
        
        run_result = evaluator.run_tests(
            prompt_data.get("template", ""), tests, model
        )
        
        progress.update(task1, description="✅ Tests complete!")
    
    # Display results
    display_test_results(run_result, save_results, str(prompt_path))

def display_performance_results(perf_results: Dict):
    """Display performance test results"""
    console.print(f"\n[bold]⚡ Performance Test Results:[/bold]")
    
    perf_tests = perf_results.get('performance_tests', [])
    
    # Create performance table
    perf_table = Table(show_header=True, header_style="bold magenta")
    perf_table.add_column("Test", style="cyan")
    perf_table.add_column("Runs", justify="center")
    perf_table.add_column("Consistency", justify="center")
    perf_table.add_column("Status", style="green")
    
    for test in perf_tests:
        consistency = test.get('consistency_score', 0)
        status = "✅ PASS" if consistency >= 0.7 else "⚠️ WARN" if consistency >= 0.5 else "❌ FAIL"
        status_style = "green" if consistency >= 0.7 else "yellow" if consistency >= 0.5 else "red"
        
        perf_table.add_row(
            test.get('test_name', 'Unknown'),
            str(test.get('runs', 0)),
            f"{consistency:.2f}",
            f"[{status_style}]{status}[/{status_style}]"
        )
    
    console.print(perf_table)
    
    console.print(f"\n[dim]💡 Consistency scores: 0.7+ = Pass, 0.5-0.7 = Warning, <0.5 = Fail[/dim]")

@app.command()
def ready(
    prompt_file: str = typer.Argument(..., help="Prompt file to assess"),
    test_file: str = typer.Argument(..., help="Test file to run against"),
    threshold: float = typer.Option(0.8, "--threshold", help="Pass rate threshold for production"),
    save_report: bool = typer.Option(True, "--save/--no-save", help="Save assessment report")
):
    """
    🚀 Assess if a prompt is ready for production
    
    Evaluates prompt against production criteria:
    - Pass rate threshold
    - Average quality score  
    - Consistency metrics
    - Error handling
    """
    console.print(f"[bold blue]🚀 Assessing production readiness: {prompt_file}[/bold blue]")
    
    try:
        evaluator = PromptEvaluator()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Running production assessment...", total=None)
            
            assessment = evaluator.assess_production_readiness(prompt_file, test_file, threshold)
            
            progress.update(task, description="✅ Assessment complete!")
        
        # Display results
        ready = assessment['ready_for_production']
        score = assessment['production_score']
        
        status_color = "green" if ready else "red"
        status_text = "READY FOR PRODUCTION" if ready else "NOT READY"
        
        console.print(f"\n[bold {status_color}]🎯 {status_text}[/bold {status_color}]")
        console.print(f"Production Score: [{status_color}]{score:.2f}/1.0[/{status_color}]")
        console.print(f"Pass Rate: {assessment['pass_rate']:.1%}")
        console.print(f"Avg Quality: {assessment['avg_score']:.1f}/10")
        
        console.print(f"\n[bold]📋 Recommendation:[/bold]")
        console.print(assessment['recommendation'])
        
        # Save report
        if save_report:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = f"evaluations/production_readiness_{timestamp}.json"
            os.makedirs("evaluations", exist_ok=True)
            
            with open(report_file, 'w') as f:
                json.dump(assessment, f, indent=2)
            
            console.print(f"\n[dim]💾 Report saved: {report_file}[/dim]")
            
    except Exception as e:
        console.print(f"[red]❌ Error assessing readiness: {e}[/red]")
        raise typer.Exit(1)

@app.command()
def compare(
    test_file: str = typer.Argument(..., help="Test file to use for comparison"),
    versions: Optional[List[str]] = typer.Option(None, "--version", help="Prompt files to compare (can specify multiple)"),
    models: Optional[List[str]] = typer.Option(None, "--model", help="Models to compare (claude, gpt-4)"),
    mode: str = typer.Option("versions", "--mode", help="Comparison mode: versions, models")
):
    """
    📊 Compare prompt versions or models
    
    Two modes:
    1. Version comparison: --mode versions --version file1.yaml --version file2.yaml
    2. Model comparison: --mode models --model claude --model gpt-4 prompt.yaml
    """
    evaluator = PromptEvaluator()
    
    if mode == "versions" and versions:
        console.print(f"[bold blue]📊 Comparing {len(versions)} prompt versions[/bold blue]")
        
        version_list = [{'file': v, 'name': Path(v).stem} for v in versions]
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Running version comparison...", total=None)
            
            comparison = evaluator.compare_prompt_versions(version_list, test_file)
            
            progress.update(task, description="✅ Comparison complete!")
        
        # Display results
        console.print(f"\n[bold]📊 Version Comparison Results:[/bold]")
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Version", style="cyan")
        table.add_column("Pass Rate", justify="center")
        table.add_column("Avg Score", justify="center")
        table.add_column("Status", style="green")
        
        for i, version in enumerate(comparison['ranked_versions']):
            rank_emoji = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else "📄"
            table.add_row(
                f"{rank_emoji} {version['version']}",
                f"{version['pass_rate']:.1%}",
                f"{version['avg_score']:.1f}",
                "BEST" if i == 0 else f"#{i+1}"
            )
        
        console.print(table)
        
        best = comparison['best_version']
        console.print(f"\n[green]🏆 Best Version: {best['version']} ({best['pass_rate']:.1%} pass rate)[/green]")
    
    elif mode == "models" and models and versions:
        prompt_file = versions[0]  # Use first version as the prompt file
        console.print(f"[bold blue]🤖 Comparing {len(models)} models on {prompt_file}[/bold blue]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Running model comparison...", total=None)
            
            comparison = evaluator.compare_models(prompt_file, test_file, models)
            
            progress.update(task, description="✅ Comparison complete!")
        
        # Display results
        console.print(f"\n[bold]🤖 Model Comparison Results:[/bold]")
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Model", style="cyan")
        table.add_column("Pass Rate", justify="center")
        table.add_column("Avg Score", justify="center")
        table.add_column("Response Time", justify="center")
        table.add_column("Status", style="green")
        
        for i, model in enumerate(comparison['ranked_models']):
            rank_emoji = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else "🤖"
            table.add_row(
                f"{rank_emoji} {model['model']}",
                f"{model['pass_rate']:.1%}",
                f"{model['avg_score']:.1f}",
                f"{model['response_time']:.1f}s",
                "BEST" if i == 0 else f"#{i+1}"
            )
        
        console.print(table)
        
        best = comparison['best_model']
        console.print(f"\n[green]🏆 Best Model: {best['model']} ({best['pass_rate']:.1%} pass rate)[/green]")
    
    else:
        console.print("[red]❌ Invalid comparison mode or missing parameters[/red]")
        console.print("\n[yellow]Examples:[/yellow]")
        console.print("• [cyan]pbt compare tests/test.yaml --mode versions --version v1.yaml --version v2.yaml[/cyan]")
        console.print("• [cyan]pbt compare tests/test.yaml --mode models --model claude --model gpt-4 prompt.yaml[/cyan]")
        raise typer.Exit(1)

@app.command()
def regression(
    current: str = typer.Argument(..., help="Current prompt file"),
    baseline: str = typer.Argument(..., help="Baseline prompt file"),
    test_file: str = typer.Argument(..., help="Test file to use"),
    save_report: bool = typer.Option(True, "--save/--no-save", help="Save regression report")
):
    """
    🔍 Test for regressions between prompt versions
    
    Compares current prompt against baseline to detect:
    - Performance degradation
    - Quality score drops
    - Individual test failures
    """
    console.print(f"[bold blue]🔍 Running regression test[/bold blue]")
    console.print(f"Current: {current}")
    console.print(f"Baseline: {baseline}")
    
    try:
        evaluator = PromptEvaluator()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Running regression analysis...", total=None)
            
            regression = evaluator.regression_test(current, baseline, test_file)
            
            progress.update(task, description="✅ Regression test complete!")
        
        # Display results
        detected = regression['regression_detected']
        status_color = "red" if detected else "green"
        status_text = "REGRESSION DETECTED" if detected else "NO REGRESSION"
        
        console.print(f"\n[bold {status_color}]🎯 {status_text}[/bold {status_color}]")
        
        # Performance comparison
        delta = regression['performance_delta']
        console.print(f"\n[bold]📊 Performance Changes:[/bold]")
        console.print(f"Pass Rate: {delta['pass_rate_change']:+.1%}")
        console.print(f"Avg Score: {delta['score_change']:+.1f}")
        
        # Test regressions
        if regression['test_regressions']:
            console.print(f"\n[bold red]⚠️ Failed Tests:[/bold red]")
            for test_reg in regression['test_regressions']:
                console.print(f"• {test_reg['test_name']}: {test_reg['score_difference']:+.1f} points")
        
        console.print(f"\n[bold]📋 Recommendation:[/bold]")
        console.print(regression['recommendation'])
        
        # Save report
        if save_report:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = f"evaluations/regression_test_{timestamp}.json"
            os.makedirs("evaluations", exist_ok=True)
            
            with open(report_file, 'w') as f:
                json.dump(regression, f, indent=2)
            
            console.print(f"\n[dim]💾 Report saved: {report_file}[/dim]")
            
    except Exception as e:
        console.print(f"[red]❌ Error running regression test: {e}[/red]")
        raise typer.Exit(1)

@app.command()
def validate(
    agents_dir: str = typer.Option("agents", "--agents-dir", help="Directory containing agent files"),
    tests_dir: str = typer.Option("tests", "--tests-dir", help="Directory containing JSONL test files"),
    model: str = typer.Option("claude", "--model", help="Model to use for testing"),
    save_report: bool = typer.Option(True, "--save/--no-save", help="Save validation report"),
    individual_reports: bool = typer.Option(False, "--individual/--summary-only", help="Show individual agent results")
):
    """
    🔍 Run batch validation on all agents using JSONL test files
    
    Validates all agents in agents/ directory against corresponding test files 
    in tests/ directory. Test files should be named {agent_name}.test.jsonl
    
    Example structure:
    - agents/summarizer.prompt.yaml → tests/summarizer.test.jsonl
    - agents/critic.prompt.yaml → tests/critic.test.jsonl
    """
    console.print(f"[bold blue]🔍 Running batch validation[/bold blue]")
    console.print(f"Agents: {agents_dir}/")
    console.print(f"Tests: {tests_dir}/")
    
    try:
        evaluator = PromptEvaluator()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Running validation suite...", total=None)
            
            validation = evaluator.validate_all_agents(agents_dir, tests_dir, model)
            
            progress.update(task, description="✅ Validation complete!")
        
        # Display overall summary
        summary = validation['overall_summary']
        
        # Overall status
        overall_pass_rate = summary['agent_pass_rate']
        status_color = "green" if overall_pass_rate >= 0.8 else "yellow" if overall_pass_rate >= 0.6 else "red"
        status_text = "READY FOR DEPLOYMENT" if overall_pass_rate >= 0.8 else "NEEDS REVIEW" if overall_pass_rate >= 0.6 else "NOT READY"
        
        console.print(f"\n[bold {status_color}]🎯 {status_text}[/bold {status_color}]")
        console.print(f"Agent Pass Rate: [{status_color}]{overall_pass_rate:.1%}[/{status_color}]")
        
        # Summary table
        console.print(f"\n[bold]📊 Validation Summary:[/bold]")
        console.print(f"Total Agents: {summary['total_agents']}")
        console.print(f"Passed Agents: [green]{summary['passed_agents']}[/green] ({summary['agent_pass_rate']:.1%})")
        console.print(f"Total Tests: {summary['total_tests']}")
        console.print(f"Passed Tests: [green]{summary['passed_tests']}[/green] ({summary['test_pass_rate']:.1%})")
        
        # Individual agent results
        if individual_reports:
            console.print(f"\n[bold]📋 Individual Agent Results:[/bold]")
            
            results_table = Table(show_header=True, header_style="bold magenta")
            results_table.add_column("Agent", style="cyan")
            results_table.add_column("Tests", justify="center")
            results_table.add_column("Passed", justify="center")
            results_table.add_column("Pass Rate", justify="center")
            results_table.add_column("Status", style="green")
            
            for agent_name, result in validation['validation_results'].items():
                if 'error' in result:
                    results_table.add_row(
                        agent_name,
                        "ERROR",
                        "0",
                        "0%",
                        "[red]❌ ERROR[/red]"
                    )
                else:
                    summary = result['summary']
                    pass_rate = summary['pass_rate']
                    status = "✅ PASS" if pass_rate >= 0.8 else "⚠️ WARN" if pass_rate >= 0.6 else "❌ FAIL"
                    status_style = "green" if pass_rate >= 0.8 else "yellow" if pass_rate >= 0.6 else "red"
                    
                    results_table.add_row(
                        agent_name,
                        str(summary['total']),
                        str(summary['passed']),
                        f"{pass_rate:.1%}",
                        f"[{status_style}]{status}[/{status_style}]"
                    )
            
            console.print(results_table)
        
        # Deployment recommendation
        console.print(f"\n[bold]📋 Deployment Recommendation:[/bold]")
        if overall_pass_rate >= 0.8:
            console.print("✅ All agents are performing well. Safe to deploy to production.")
        elif overall_pass_rate >= 0.6:
            console.print("⚠️ Some agents need attention. Review failing tests before deployment.")
        else:
            console.print("❌ Multiple agents failing. Do not deploy - investigate and fix issues.")
        
        # Save report
        if save_report:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = f"evaluations/validation_report_{timestamp}.json"
            os.makedirs("evaluations", exist_ok=True)
            
            with open(report_file, 'w') as f:
                json.dump(validation, f, indent=2)
            
            console.print(f"\n[dim]💾 Report saved: {report_file}[/dim]")
            
    except Exception as e:
        console.print(f"[red]❌ Error running validation: {e}[/red]")
        raise typer.Exit(1)

@app.command() 
def testjsonl(
    prompt_file: str = typer.Argument(..., help="Prompt file to test"),
    jsonl_file: str = typer.Argument(..., help="JSONL test file"),
    model: str = typer.Option("claude", "--model", help="Model to test with"),
    save_results: bool = typer.Option(True, "--save/--no-save", help="Save test results")
):
    """
    🧪 Test a prompt against a JSONL test file
    
    JSONL format (one JSON object per line):
    {"test_name": "example", "inputs": {"content": "text"}, "expected_keywords": ["key1", "key2"], "quality_criteria": "description"}
    
    Each line should contain:
    - test_name: Descriptive name for the test
    - inputs: Variables to substitute in the prompt template  
    - expected_keywords: Keywords that should appear in output
    - quality_criteria: Description of what makes a good response
    """
    console.print(f"[bold blue]🧪 Testing {prompt_file} with {jsonl_file}[/bold blue]")
    
    try:
        evaluator = PromptEvaluator()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Running JSONL tests...", total=None)
            
            results = evaluator.run_jsonl_tests(prompt_file, jsonl_file, model)
            
            progress.update(task, description="✅ Tests complete!")
        
        # Display results
        summary = results['summary']
        
        console.print(f"\n[bold]📊 JSONL Test Results:[/bold]")
        
        # Create results table
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Test", style="cyan")
        table.add_column("Keywords", justify="center")
        table.add_column("Score", justify="center")
        table.add_column("Status", style="green")
        
        for result in results['results']:
            if 'error' in result:
                table.add_row(
                    result['test_name'],
                    "ERROR",
                    "0",
                    "[red]❌ ERROR[/red]"
                )
            else:
                keyword_matches = result.get('keyword_matches', [])
                expected_keywords = result.get('expected_keywords', [])
                keyword_ratio = f"{len(keyword_matches)}/{len(expected_keywords)}" if expected_keywords else "N/A"
                
                status = "✅ PASS" if result.get('passed') else "❌ FAIL"
                status_style = "green" if result.get('passed') else "red"
                
                table.add_row(
                    result['test_name'],
                    keyword_ratio,
                    f"{result.get('score', 0):.1f}",
                    f"[{status_style}]{status}[/{status_style}]"
                )
        
        console.print(table)
        
        # Summary
        pass_rate = summary.get('pass_rate', 0) * 100
        console.print(f"\n[bold]Summary:[/bold]")
        console.print(f"Total: {summary.get('total', 0)}")
        console.print(f"Passed: [green]{summary.get('passed', 0)}[/green]")
        console.print(f"Failed: [red]{summary.get('failed', 0)}[/red]")
        console.print(f"Pass Rate: [{'green' if pass_rate >= 80 else 'yellow' if pass_rate >= 60 else 'red'}]{pass_rate:.1f}%[/]")
        
        # Save results
        if save_results:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_file = f"evaluations/jsonl_test_results_{timestamp}.json"
            
            os.makedirs("evaluations", exist_ok=True)
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2)
            
            console.print(f"\n[dim]💾 Results saved to: {results_file}[/dim]")
            
    except Exception as e:
        console.print(f"[red]❌ Error running JSONL tests: {e}[/red]")
        raise typer.Exit(1)

@app.command()
def gentests(
    prompt_file: str = typer.Argument(..., help="Prompt file to generate tests for"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output JSONL file path"),
    num_tests: int = typer.Option(6, "--num-tests", "-n", help="Number of test cases to generate"),
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite existing test file")
):
    """
    🧪 Generate JSONL test cases for an existing prompt
    
    Creates comprehensive test cases for any prompt file.
    Automatically determines test file name if not specified.
    
    Examples:
    - pbt gentests agents/summarizer.prompt.yaml
    - pbt gentests my_prompt.yaml --output custom_tests.jsonl
    """
    console.print(f"[bold blue]🧪 Generating test cases for: {prompt_file}[/bold blue]")
    
    # Check if prompt file exists
    if not Path(prompt_file).exists():
        console.print(f"[red]❌ Prompt file not found: {prompt_file}[/red]")
        raise typer.Exit(1)
    
    # Determine output file name
    if output:
        test_filename = output
    else:
        prompt_name = Path(prompt_file).stem.replace('.prompt', '')
        test_filename = f"tests/{prompt_name}.test.jsonl"
    
    # Check if test file already exists
    if Path(test_filename).exists() and not overwrite:
        console.print(f"[yellow]⚠️ Test file already exists: {test_filename}[/yellow]")
        console.print("Use --overwrite to replace it, or specify a different --output path")
        raise typer.Exit(1)
    
    try:
        generator = PromptGenerator()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Generating test cases...", total=None)
            
            # Read prompt file
            with open(prompt_file, 'r') as f:
                prompt_content = f.read()
            
            # Generate test cases
            test_result = generator.generate_jsonl_tests(prompt_content, num_tests)
            
            progress.update(task, description="✅ Test generation complete!")
        
        if test_result.get("success"):
            test_cases = test_result.get("test_cases", [])
            
            # Create tests directory if needed
            os.makedirs(Path(test_filename).parent, exist_ok=True)
            
            # Save JSONL tests
            if generator.save_jsonl_tests(test_cases, test_filename):
                console.print(f"\n[green]✅ Generated {len(test_cases)} test cases: {test_filename}[/green]")
                
                # Show preview of first test case
                if test_cases:
                    console.print(f"\n[bold]Preview (first test case):[/bold]")
                    preview = json.dumps(test_cases[0], indent=2)
                    syntax = Syntax(preview, "json", theme="monokai", line_numbers=True)
                    console.print(Panel(syntax, title="Sample Test Case", expand=False))
                
                console.print(f"\n[dim]💡 Run tests with: pbt testjsonl {prompt_file} {test_filename}[/dim]")
            else:
                console.print(f"[red]❌ Failed to save test cases[/red]")
                raise typer.Exit(1)
        else:
            console.print(f"[red]❌ Failed to generate test cases: {test_result.get('error', 'Unknown error')}[/red]")
            if 'raw_content' in test_result:
                console.print(f"\n[yellow]Raw response:[/yellow]")
                console.print(test_result['raw_content'])
            raise typer.Exit(1)
            
    except Exception as e:
        console.print(f"[red]❌ Error generating test cases: {e}[/red]")
        raise typer.Exit(1)

if __name__ == "__main__":
    app()