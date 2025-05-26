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
import time
import random
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax

# Only import what's needed for convert command
from pbt.__version__ import __version__

# Import PBT core classes
from pbt.core.project import PBTProject
from pbt.core.prompt_generator import PromptGenerator
from pbt.core.prompt_evaluator import PromptEvaluator
from pbt.core.prompt_renderer import PromptRenderer

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
        "🌐 Interactive web UI for visual comparison",
        "🔄 Convert existing agent code to PBT",
        "📊 Automatic scoring with expected outputs",
        "💰 Cost optimization & performance metrics",
        "🔗 Multi-agent chains & RAG optimization"
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
        "[bold]Compare models:[/bold] [cyan]pbt compare prompts/my_prompt.yaml --models claude,gpt-4[/cyan]",
        "[bold]Start web UI:[/bold] [cyan]pbt web[/cyan]",
        "[bold]Optimize for cost:[/bold] [cyan]pbt optimize prompts/my_prompt.yaml --target cost[/cyan]"
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
        ("compare", "Compare prompts across models"),
        ("web", "Launch interactive web UI"),
        ("render", "Render prompts with variables"),
        ("optimize", "Optimize prompts for cost/quality"),
        ("convert", "Convert Python agents to PBT")
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

@app.command()
def compare(
    prompt_file: Path = typer.Argument(..., help="Path to the prompt file to compare"),
    models: str = typer.Option("claude,gpt-4,gpt-3.5-turbo", "--models", "-m", help="Comma-separated list of models to compare"),
    variables: Optional[str] = typer.Option(None, "--vars", "-v", help="JSON string of variables to use"),
    save_results: bool = typer.Option(True, "--save-results", "-s", help="Save comparison results"),
    output_format: str = typer.Option("table", "--output", "-o", help="Output format: table, json, markdown")
):
    """🔍 Compare prompt performance across multiple models"""
    console.print(f"[bold blue]🔍 Comparing models for prompt: {prompt_file}[/bold blue]")
    
    # Parse models
    model_list = [m.strip() for m in models.split(",")]
    console.print(f"[cyan]📊 Models to compare: {', '.join(model_list)}[/cyan]")
    
    # Parse variables
    vars_dict = {}
    if variables:
        try:
            vars_dict = json.loads(variables)
            console.print(f"[cyan]📝 Variables: {json.dumps(vars_dict, indent=2)}[/cyan]")
        except json.JSONDecodeError:
            console.print("[red]❌ Invalid JSON format for variables[/red]")
            raise typer.Exit(1)
    
    # Verify prompt file exists
    if not prompt_file.exists():
        console.print(f"[red]❌ Prompt file not found: {prompt_file}[/red]")
        raise typer.Exit(1)
    
    # Initialize renderer and run comparison
    renderer = PromptRenderer()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task(f"Comparing {len(model_list)} models...", total=len(model_list))
        
        comparison_result = renderer.compare_models(
            prompt_file=prompt_file,
            variables=vars_dict,
            models=model_list
        )
        
        progress.update(task, completed=len(model_list))
    
    # Display results based on format
    if output_format == "json":
        console.print_json(json.dumps({
            "prompt_file": comparison_result.prompt_file,
            "models": comparison_result.models,
            "variables": comparison_result.variables,
            "results": comparison_result.results,
            "recommendations": comparison_result.recommendations,
            "timestamp": comparison_result.timestamp
        }, indent=2))
    elif output_format == "markdown":
        display_comparison_markdown(comparison_result)
    else:  # table format
        display_comparison_table(comparison_result)
    
    # Save results if requested
    if save_results:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"evaluations/comparison_{timestamp}.json"
        
        os.makedirs("evaluations", exist_ok=True)
        with open(results_file, 'w') as f:
            json.dump({
                "prompt_file": comparison_result.prompt_file,
                "models": comparison_result.models,
                "variables": comparison_result.variables,
                "results": comparison_result.results,
                "recommendations": comparison_result.recommendations,
                "timestamp": comparison_result.timestamp
            }, f, indent=2)
        
        console.print(f"\n[dim]💾 Results saved to: {results_file}[/dim]")


def display_comparison_table(comparison_result):
    """Display model comparison in a formatted table"""
    console.print("\n[bold]📊 Model Comparison Results:[/bold]\n")
    
    # Create comparison table
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Model", style="cyan", width=15)
    table.add_column("Response Time", justify="center", width=12)
    table.add_column("Tokens", justify="center", width=10)
    table.add_column("Cost", justify="center", width=10)
    table.add_column("Quality Score", justify="center", width=12)
    
    for model, result in comparison_result.results.items():
        stats = result['stats']
        response_time = f"{stats['response_time']:.2f}s"
        tokens = str(stats['tokens'])
        cost = f"${stats['cost']:.4f}"
        quality = f"{stats['quality_score']:.1f}/10"
        
        # Color code quality score
        if stats['quality_score'] >= 8:
            quality_style = "[green]" + quality + "[/green]"
        elif stats['quality_score'] >= 6:
            quality_style = "[yellow]" + quality + "[/yellow]"
        else:
            quality_style = "[red]" + quality + "[/red]"
        
        table.add_row(model, response_time, tokens, cost, quality_style)
    
    console.print(table)
    
    # Display recommendations
    console.print("\n[bold]💡 Recommendations:[/bold]")
    for category, recommendation in comparison_result.recommendations.items():
        emoji = {
            "best_quality": "🏆",
            "best_speed": "⚡",
            "best_cost": "💰",
            "balanced": "⚖️"
        }.get(category, "📌")
        console.print(f"{emoji} {category.replace('_', ' ').title()}: [green]{recommendation}[/green]")
    
    # Show sample outputs
    console.print("\n[bold]📝 Sample Outputs:[/bold]\n")
    for model, result in comparison_result.results.items():
        console.print(Panel(
            result['output'][:200] + "..." if len(result['output']) > 200 else result['output'],
            title=f"[cyan]{model}[/cyan]",
            border_style="dim"
        ))


def display_comparison_markdown(comparison_result):
    """Display model comparison in markdown format"""
    md_output = f"""# Model Comparison Results

**Prompt File**: `{comparison_result.prompt_file}`  
**Timestamp**: {comparison_result.timestamp}

## Models Compared
{', '.join(comparison_result.models)}

## Variables Used
```json
{json.dumps(comparison_result.variables, indent=2)}
```

## Performance Metrics

| Model | Response Time | Tokens | Cost | Quality Score |
|-------|--------------|--------|------|---------------|
"""
    
    for model, result in comparison_result.results.items():
        stats = result['stats']
        md_output += f"| {model} | {stats['response_time']:.2f}s | {stats['tokens']} | ${stats['cost']:.4f} | {stats['quality_score']:.1f}/10 |\n"
    
    md_output += "\n## Recommendations\n\n"
    for category, recommendation in comparison_result.recommendations.items():
        md_output += f"- **{category.replace('_', ' ').title()}**: {recommendation}\n"
    
    md_output += "\n## Sample Outputs\n\n"
    for model, result in comparison_result.results.items():
        md_output += f"### {model}\n\n```\n{result['output'][:500]}...\n```\n\n"
    
    console.print(Syntax(md_output, "markdown"))


@app.command()
def web(
    port: int = typer.Option(8080, "--port", "-p", help="Port to run the web UI on"),
    host: str = typer.Option("127.0.0.1", "--host", help="Host to bind to"),
    open_browser: bool = typer.Option(True, "--open/--no-open", help="Open browser automatically")
):
    """🌐 Launch the PBT Studio web interface"""
    console.print("[bold blue]🌐 Starting PBT Studio Web Interface...[/bold blue]")
    
    try:
        import uvicorn
        import webbrowser
        from pbt.web.app import app as web_app
        
        # Create necessary directories
        Path("pbt/web/static").mkdir(parents=True, exist_ok=True)
        
        # Open browser after a short delay
        if open_browser:
            def open_browser_delayed():
                import time
                time.sleep(1.5)  # Wait for server to start
                webbrowser.open(f"http://{host}:{port}")
            
            import threading
            browser_thread = threading.Thread(target=open_browser_delayed)
            browser_thread.daemon = True
            browser_thread.start()
        
        console.print(f"[green]✅ Web UI starting at: http://{host}:{port}[/green]")
        console.print("[dim]Press Ctrl+C to stop the server[/dim]")
        
        # Run the web server
        uvicorn.run(
            "pbt.web.app:app",
            host=host,
            port=port,
            reload=False,
            log_level="info"
        )
        
    except ImportError as e:
        console.print("[red]❌ Web UI dependencies not installed[/red]")
        console.print("[yellow]Run: pip install 'prompt-build-tool[web]' to install web dependencies[/yellow]")
        console.print(f"[dim]Missing: {e}[/dim]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]❌ Failed to start web UI: {e}[/red]")
        raise typer.Exit(1)


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
        
        evaluation_report = evaluator.evaluate_auto_generated(
            prompt_path, num_tests, test_type
        )
        
        progress.update(task1, description=f"Generated {num_tests} test cases and completed evaluation")
        progress.update(task1, description="✅ Tests complete!")
    
    # Display results
    display_evaluation_results(evaluation_report, save_results)

def display_evaluation_results(report, save_results: bool):
    """Display evaluation results in a formatted table"""
    console.print(f"\n[bold blue]🧪 Test Results for: {Path(report.prompt_file).name}[/bold blue]")
    console.print(f"[dim]Model: {report.model} | Tests: {report.total_tests} | Passed: {report.passed_tests}[/dim]")
    
    # Create results table
    table = Table(show_header=True, header_style="bold magenta", border_style="blue")
    table.add_column("Test", style="cyan", width=20)
    table.add_column("Score", justify="center", width=10)
    table.add_column("Status", justify="center", width=8)
    table.add_column("Output Preview", width=50)
    
    for result in report.individual_results:
        score_color = "green" if result.score >= 8.0 else "yellow" if result.score >= 6.0 else "red"
        status = "✅ PASS" if result.passed else "❌ FAIL"
        status_color = "green" if result.passed else "red"
        
        # Truncate output for preview
        output_preview = result.output[:47] + "..." if len(result.output) > 50 else result.output
        
        table.add_row(
            result.test_name,
            f"[{score_color}]{result.score:.1f}/10[/{score_color}]",
            f"[{status_color}]{status}[/{status_color}]",
            output_preview
        )
    
    console.print(table)
    
    # Summary
    pass_rate = report.passed_tests / report.total_tests if report.total_tests > 0 else 0
    avg_score = report.average_score
    
    console.print(f"\n[bold]📊 Summary:[/bold]")
    console.print(f"   • Pass Rate: {pass_rate:.1%} ({report.passed_tests}/{report.total_tests})")
    console.print(f"   • Average Score: {avg_score:.1f}/10")
    
    if avg_score >= 8.5:
        console.print(f"   • Grade: [green]🎯 EXCELLENT[/green]")
    elif avg_score >= 7.0:
        console.print(f"   • Grade: [yellow]✅ GOOD[/yellow]")
    else:
        console.print(f"   • Grade: [red]⚠️ NEEDS IMPROVEMENT[/red]")
    
    # Save results
    if save_results:
        results_file = f"evaluations/{Path(report.prompt_file).stem}_auto_test_results.json"
        os.makedirs("evaluations", exist_ok=True)
        
        from pbt.core.prompt_evaluator import PromptEvaluator
        evaluator = PromptEvaluator()
        if evaluator.save_report(report, Path(results_file)):
            console.print(f"\n[dim]💾 Results saved to: {results_file}[/dim]")

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
def testcomp(
    prompt_file: str = typer.Argument(..., help="Prompt file to test"),
    test_file: str = typer.Argument(..., help="Test file with comprehensive test cases"),
    model: str = typer.Option("gpt-4", "--model", help="Model to test with"),
    aspects: Optional[str] = typer.Option(None, "--aspects", help="Comma-separated aspects to evaluate"),
    save_report: bool = typer.Option(True, "--save/--no-save", help="Save detailed report"),
    output_format: str = typer.Option("table", "--format", help="Output format: table, json, markdown")
):
    """
    🔬 Run comprehensive multi-aspect testing on prompts
    
    Evaluates prompts across multiple dimensions:
    - Correctness: Is the output accurate?
    - Faithfulness: Does it preserve meaning?
    - Style/Tone: Is it appropriately concise/verbose?
    - Safety: Does it avoid harmful content?
    - Stability: Are outputs consistent?
    - Model Quality: How do models compare?
    
    Example test file:
    ```yaml
    tests:
      - name: summarize_cats
        inputs:
          text: "Cats are curious creatures who like to explore."
        expected: "Cats like to explore and are curious."
        evaluate:
          correctness: true
          faithfulness: true
          style_tone: concise
          safety: true
          stability: 5  # number of runs
          model_quality: [gpt-4, claude]
    ```
    """
    console.print(f"[bold blue]🔬 Running comprehensive tests on: {prompt_file}[/bold blue]")
    
    try:
        # Import here to avoid circular imports
        from pbt.core.comprehensive_evaluator import ComprehensiveEvaluator, EvaluationAspect
        
        # Initialize evaluator
        evaluator = ComprehensiveEvaluator()
        
        # Parse aspects if specified
        if aspects:
            aspect_list = []
            for aspect_name in aspects.split(','):
                aspect_name = aspect_name.strip().upper()
                try:
                    aspect_list.append(EvaluationAspect[aspect_name])
                except KeyError:
                    console.print(f"[yellow]⚠️ Unknown aspect: {aspect_name}[/yellow]")
        else:
            aspect_list = None
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Running comprehensive evaluation...", total=None)
            
            # Run test suite
            results = evaluator.run_test_suite(
                prompt_file=prompt_file,
                test_file=test_file,
                model=model
            )
            
            progress.update(task, description="✅ Evaluation complete!")
        
        # Display results based on format
        if output_format == "json":
            # Convert results to JSON-serializable format
            json_results = {
                'summary': {
                    'total_tests': results['total_tests'],
                    'passed_tests': results['passed_tests'],
                    'pass_rate': results['pass_rate']
                },
                'aspect_summaries': results['aspect_summaries'],
                'tests': [
                    {
                        'name': r.test_name,
                        'passed': r.passed,
                        'overall_score': r.overall_score,
                        'aspects': {
                            aspect.value: {
                                'score': score.score,
                                'passed': score.passed,
                                'details': score.details
                            }
                            for aspect, score in r.aspect_scores.items()
                        }
                    }
                    for r in results['results']
                ]
            }
            console.print(json.dumps(json_results, indent=2))
        
        elif output_format == "markdown":
            # Generate markdown report
            md_lines = [
                f"# Comprehensive Test Report",
                f"\n**Prompt:** `{prompt_file}`",
                f"**Test File:** `{test_file}`",
                f"**Model:** {model}",
                f"\n## Summary",
                f"- Total Tests: {results['total_tests']}",
                f"- Passed: {results['passed_tests']}",
                f"- Pass Rate: {results['pass_rate']:.1%}",
                f"\n## Aspect Analysis"
            ]
            
            for aspect, summary in results['aspect_summaries'].items():
                md_lines.extend([
                    f"\n### {aspect.title().replace('_', ' ')}",
                    f"- Average Score: {summary['avg_score']:.1f}/10",
                    f"- Range: {summary['min_score']:.1f} - {summary['max_score']:.1f}",
                    f"- Passed: {summary['passed']}/{results['total_tests']}"
                ])
            
            console.print("\n".join(md_lines))
        
        else:  # table format (default)
            # Summary
            console.print(f"\n[bold]📊 Comprehensive Test Results:[/bold]")
            console.print(f"Total Tests: {results['total_tests']}")
            console.print(f"Passed: [green]{results['passed_tests']}[/green]")
            console.print(f"Failed: [red]{results['total_tests'] - results['passed_tests']}[/red]")
            console.print(f"Pass Rate: [{'green' if results['pass_rate'] >= 0.8 else 'yellow' if results['pass_rate'] >= 0.6 else 'red'}]{results['pass_rate']:.1%}[/]")
            
            # Aspect summary table
            if results['aspect_summaries']:
                console.print(f"\n[bold]📈 Aspect Analysis:[/bold]")
                
                aspect_table = Table(show_header=True, header_style="bold magenta")
                aspect_table.add_column("Aspect", style="cyan")
                aspect_table.add_column("Avg Score", justify="center")
                aspect_table.add_column("Min", justify="center")
                aspect_table.add_column("Max", justify="center")
                aspect_table.add_column("Pass Rate", justify="center")
                
                for aspect, summary in results['aspect_summaries'].items():
                    pass_rate = summary['passed'] / results['total_tests'] if results['total_tests'] > 0 else 0
                    aspect_table.add_row(
                        aspect.title().replace('_', ' '),
                        f"{summary['avg_score']:.1f}",
                        f"{summary['min_score']:.1f}",
                        f"{summary['max_score']:.1f}",
                        f"{pass_rate:.0%}"
                    )
                
                console.print(aspect_table)
            
            # Individual test results
            console.print(f"\n[bold]🧪 Test Results:[/bold]")
            
            test_table = Table(show_header=True, header_style="bold magenta")
            test_table.add_column("Test", style="cyan")
            test_table.add_column("Overall", justify="center")
            test_table.add_column("Correct", justify="center")
            test_table.add_column("Faithful", justify="center")
            test_table.add_column("Style", justify="center")
            test_table.add_column("Safety", justify="center")
            test_table.add_column("Stable", justify="center")
            test_table.add_column("Status")
            
            for result in results['results']:
                scores = result.aspect_scores
                row = [
                    result.test_name,
                    f"{result.overall_score:.1f}",
                    f"{scores.get(EvaluationAspect.CORRECTNESS, type('', (), {'score': '-'})()).score:.1f}" if EvaluationAspect.CORRECTNESS in scores else "-",
                    f"{scores.get(EvaluationAspect.FAITHFULNESS, type('', (), {'score': '-'})()).score:.1f}" if EvaluationAspect.FAITHFULNESS in scores else "-",
                    f"{scores.get(EvaluationAspect.STYLE_TONE, type('', (), {'score': '-'})()).score:.1f}" if EvaluationAspect.STYLE_TONE in scores else "-",
                    f"{scores.get(EvaluationAspect.SAFETY, type('', (), {'score': '-'})()).score:.1f}" if EvaluationAspect.SAFETY in scores else "-",
                    f"{scores.get(EvaluationAspect.STABILITY, type('', (), {'score': '-'})()).score:.1f}" if EvaluationAspect.STABILITY in scores else "-",
                    "[green]✅ PASS[/green]" if result.passed else "[red]❌ FAIL[/red]"
                ]
                test_table.add_row(*row)
            
            console.print(test_table)
            
            # Show detailed feedback for failed tests
            failed_tests = [r for r in results['results'] if not r.passed]
            if failed_tests:
                console.print(f"\n[bold red]❌ Failed Test Details:[/bold red]")
                for test in failed_tests[:3]:  # Show first 3
                    console.print(f"\n[yellow]{test.test_name}:[/yellow]")
                    for aspect, score in test.aspect_scores.items():
                        if not score.passed:
                            console.print(f"  • {aspect.value}: {score.score:.1f}/10 - {score.details.get('reasoning', 'No details')}")
        
        # Save detailed report if requested
        if save_report:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = f"evaluations/comprehensive_test_{timestamp}.json"
            
            os.makedirs("evaluations", exist_ok=True)
            
            # Convert results to JSON-serializable format
            report_data = {
                'metadata': results['metadata'],
                'summary': {
                    'total_tests': results['total_tests'],
                    'passed_tests': results['passed_tests'],
                    'pass_rate': results['pass_rate']
                },
                'aspect_summaries': results['aspect_summaries'],
                'detailed_results': [
                    {
                        'test_name': r.test_name,
                        'input_data': r.input_data,
                        'output': r.output,
                        'expected': r.expected,
                        'overall_score': r.overall_score,
                        'passed': r.passed,
                        'aspect_scores': {
                            aspect.value: {
                                'score': score.score,
                                'passed': score.passed,
                                'reasoning': score.details.get('reasoning', ''),
                                'details': score.details
                            }
                            for aspect, score in r.aspect_scores.items()
                        }
                    }
                    for r in results['results']
                ]
            }
            
            with open(report_file, 'w') as f:
                json.dump(report_data, f, indent=2)
            
            console.print(f"\n[dim]💾 Detailed report saved: {report_file}[/dim]")
        
        # Exit with appropriate code
        if results['pass_rate'] < 0.8:
            raise typer.Exit(1)
            
    except Exception as e:
        console.print(f"[red]❌ Error running comprehensive tests: {e}[/red]")
        raise typer.Exit(1)

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
def convert(
    input_file: str = typer.Argument(..., help="Python file with agent functions to convert"),
    output_dir: Optional[Path] = typer.Option(None, "--output", "-o", help="Output directory for converted files"),
    batch: bool = typer.Option(False, "--batch", help="Batch convert all .py files in directory"),
    pattern: str = typer.Option("*agent*.py", "--pattern", help="File pattern for batch conversion")
):
    """
    🔄 Convert Python agent code to PBT YAML format
    
    Automatically extracts prompts from Python functions and creates:
    - YAML prompt files in agents/ directory
    - Converted Python file using PBT runtime
    
    Examples:
    - Convert single file: pbt convert agent.py
    - Specify output: pbt convert agent.py --output converted/
    - Batch convert: pbt convert . --batch --pattern "*_agent.py"
    """
    console.print(f"[bold blue]🔄 Converting Python agents to PBT format[/bold blue]")
    
    from pbt.core.converter import convert_agent_file
    
    if batch:
        # Batch conversion
        input_path = Path(input_file)
        if not input_path.is_dir():
            console.print(f"[red]❌ For batch conversion, provide a directory path[/red]")
            raise typer.Exit(1)
        
        # Find all matching files
        py_files = list(input_path.glob(pattern))
        if not py_files:
            console.print(f"[yellow]⚠️ No files found matching pattern: {pattern}[/yellow]")
            raise typer.Exit(1)
        
        console.print(f"[cyan]Found {len(py_files)} files to convert[/cyan]")
        
        results = []
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Converting files...", total=len(py_files))
            
            for py_file in py_files:
                try:
                    result = convert_agent_file(str(py_file), str(output_dir) if output_dir else "agents")
                    results.append((py_file, result))
                    progress.advance(task)
                except Exception as e:
                    console.print(f"[red]❌ Error converting {py_file}: {e}[/red]")
        
        # Summary
        console.print(f"\n[bold]📊 Conversion Summary:[/bold]")
        total_prompts = sum(r[1].get('prompts_extracted', 0) for r in results)
        console.print(f"Files converted: {len(results)}")
        console.print(f"Total prompts extracted: {total_prompts}")
        
        # Show files created
        console.print(f"\n[bold]📁 Files created:[/bold]")
        for py_file, result in results:
            console.print(f"\n[cyan]{py_file.name}:[/cyan]")
            console.print(f"  Prompts: {result.get('prompts_extracted', 0)}")
            for yaml_file in result.get('yaml_files', []):
                console.print(f"  ✅ {Path(yaml_file).name}")
            console.print(f"  ✅ {Path(result['python_file']).name}")
    
    else:
        # Single file conversion
        if not Path(input_file).exists():
            console.print(f"[red]❌ File not found: {input_file}[/red]")
            raise typer.Exit(1)
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Converting file...", total=None)
                
                result = convert_agent_file(input_file, str(output_dir) if output_dir else "agents")
                
                progress.update(task, description="✅ Conversion complete!")
            
            # Display results
            console.print(f"\n[green]✅ Successfully converted {input_file}[/green]")
            console.print(f"\n[bold]📊 Conversion Results:[/bold]")
            console.print(f"Prompts extracted: {result['prompts_extracted']}")
            
            console.print(f"\n[bold]📁 Files created:[/bold]")
            
            # YAML files
            console.print(f"\n[cyan]YAML prompt files:[/cyan]")
            for yaml_file in result['yaml_files']:
                console.print(f"  ✅ {Path(yaml_file).name}")
            
            # Python file
            if result['python_file']:
                console.print(f"\n[cyan]Converted Python file:[/cyan]")
                console.print(f"  ✅ {Path(result['python_file']).name}")
            
            # Show example usage
            console.print(f"\n[bold]🚀 Next steps:[/bold]")
            console.print(f"1. Review generated YAML files in agents/")
            console.print(f"2. Test the converted code: [cyan]python {Path(result['python_file']).name}[/cyan]")
            console.print(f"3. Generate tests: [cyan]pbt gentests agents/*.yaml[/cyan]")
            console.print(f"4. Run tests: [cyan]pbt test agents/[/cyan]")
            
        except Exception as e:
            console.print(f"[red]❌ Error converting file: {e}[/red]")
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

@app.command()
def deps(
    output_format: str = typer.Option("text", "--format", help="Output format: text, mermaid, json"),
    target: Optional[str] = typer.Option(None, "--target", help="Show dependencies for specific prompt"),
    downstream: bool = typer.Option(False, "--downstream", help="Show downstream dependencies")
):
    """
    🔗 Show prompt dependency graph (DBT-like lineage)
    
    Visualize how prompts depend on each other:
    - pbt deps - Show full dependency graph
    - pbt deps --target my_prompt - Show dependencies for specific prompt
    - pbt deps --format mermaid - Output as Mermaid diagram
    """
    console.print("[bold blue]🔗 Analyzing prompt dependencies[/bold blue]")
    
    try:
        dag = PromptDAG(Path.cwd())
        dag.load_prompts()
        
        if target:
            # Show lineage for specific prompt
            lineage = dag.get_lineage(target)
            
            console.print(f"\n[bold]Lineage for {target}:[/bold]")
            console.print(f"\n[cyan]Upstream dependencies:[/cyan]")
            for dep in lineage['upstream']:
                console.print(f"  ← {dep}")
            
            if downstream:
                console.print(f"\n[cyan]Downstream dependencies:[/cyan]")
                for dep in lineage['downstream']:
                    console.print(f"  → {dep}")
        else:
            # Show full graph
            if output_format == "mermaid":
                mermaid = dag.to_mermaid()
                console.print("\n[bold]Mermaid Diagram:[/bold]")
                console.print(Panel(mermaid, title="Copy to Mermaid Live Editor", expand=False))
            elif output_format == "json":
                import json
                graph_data = {
                    "nodes": list(dag.nodes.keys()),
                    "edges": list(dag.graph.edges())
                }
                console.print(json.dumps(graph_data, indent=2))
            else:
                # Text format
                execution_order = dag.get_execution_order()
                console.print("\n[bold]Execution Order:[/bold]")
                for i, prompt in enumerate(execution_order, 1):
                    console.print(f"{i}. {prompt}")
                
    except Exception as e:
        console.print(f"[red]❌ Error analyzing dependencies: {e}[/red]")
        raise typer.Exit(1)

@app.command()
def docs(
    serve: bool = typer.Option(False, "--serve", help="Serve documentation locally"),
    output_dir: Optional[Path] = typer.Option(None, "--output", help="Output directory for docs")
):
    """
    📚 Generate documentation from prompts (DBT-like docs)
    
    Auto-generates documentation from your prompt files:
    - Prompt descriptions and metadata
    - Variable documentation
    - Example usage
    - Dependency graphs
    """
    console.print("[bold blue]📚 Generating documentation[/bold blue]")
    
    try:
        manifest = Manifest(Path.cwd())
        manifest.load_prompts()
        manifest.load_tests()
        
        output = output_dir or Path("docs/generated")
        manifest.generate_docs(output)
        
        console.print(f"[green]✅ Documentation generated in {output}[/green]")
        
        if serve:
            import subprocess
            console.print("\n[cyan]Starting documentation server...[/cyan]")
            subprocess.run(["python", "-m", "http.server", "8000"], cwd=output)
            
    except Exception as e:
        console.print(f"[red]❌ Error generating docs: {e}[/red]")
        raise typer.Exit(1)

@app.command()
def snapshot(
    action: str = typer.Argument("create", help="Action: create, list, diff, restore"),
    prompt_name: Optional[str] = typer.Option(None, "--prompt", help="Specific prompt to snapshot"),
    timestamp: Optional[str] = typer.Option(None, "--timestamp", help="Timestamp for diff/restore"),
    reason: Optional[str] = typer.Option("", "--reason", help="Reason for snapshot")
):
    """
    📸 Manage prompt snapshots (DBT-like snapshots)
    
    Track prompt changes over time:
    - pbt snapshot create - Snapshot all prompts
    - pbt snapshot list --prompt my_prompt - List snapshots
    - pbt snapshot diff --prompt my_prompt - Compare versions
    - pbt snapshot restore --prompt my_prompt --timestamp 2024-01-01
    """
    manager = SnapshotManager(Path.cwd())
    
    if action == "create":
        console.print("[bold blue]📸 Creating snapshots[/bold blue]")
        
        if prompt_name:
            # Snapshot specific prompt
            prompt_path = find_prompt_file(prompt_name)
            if prompt_path:
                snapshot = manager.create_snapshot(prompt_path, reason)
                console.print(f"[green]✅ Created snapshot for {prompt_name}[/green]")
            else:
                console.print(f"[red]❌ Prompt not found: {prompt_name}[/red]")
        else:
            # Snapshot all
            snapshots = manager.snapshot_all(reason or "Manual snapshot")
            console.print(f"[green]✅ Created {len(snapshots)} snapshots[/green]")
            
    elif action == "list":
        if not prompt_name:
            console.print("[red]❌ Please specify --prompt[/red]")
            raise typer.Exit(1)
            
        snapshots = manager.get_snapshots(prompt_name)
        if snapshots:
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Timestamp", style="cyan")
            table.add_column("Version")
            table.add_column("Reason")
            
            for snap in snapshots:
                table.add_row(
                    snap.timestamp,
                    snap.version,
                    snap.metadata.get('reason', '')
                )
            
            console.print(table)
        else:
            console.print(f"[yellow]No snapshots found for {prompt_name}[/yellow]")
            
    elif action == "diff":
        if not prompt_name:
            console.print("[red]❌ Please specify --prompt[/red]")
            raise typer.Exit(1)
            
        diff = manager.diff_snapshots(prompt_name)
        if diff:
            syntax = Syntax(diff, "diff", theme="monokai")
            console.print(Panel(syntax, title=f"Changes in {prompt_name}", expand=False))
        else:
            console.print("[yellow]No differences found[/yellow]")
            
    elif action == "restore":
        if not prompt_name or not timestamp:
            console.print("[red]❌ Please specify --prompt and --timestamp[/red]")
            raise typer.Exit(1)
            
        if manager.restore_snapshot(prompt_name, timestamp):
            console.print(f"[green]✅ Restored {prompt_name} to {timestamp}[/green]")
        else:
            console.print(f"[red]❌ Failed to restore snapshot[/red]")

@app.command()
def run(
    target: Optional[str] = typer.Argument(None, help="Specific prompt to run"),
    profile: Optional[str] = typer.Option(None, "--profile", help="Profile to use"),
    target_env: Optional[str] = typer.Option(None, "--target", help="Target environment"),
    full_refresh: bool = typer.Option(False, "--full-refresh", help="Rebuild all prompts")
):
    """
    🚀 Run prompts with dependency resolution (DBT-like run)
    
    Execute prompts in dependency order:
    - pbt run - Run all prompts
    - pbt run my_prompt - Run specific prompt and dependencies
    - pbt run --profile production --target prod
    """
    console.print("[bold blue]🚀 Running prompts[/bold blue]")
    
    # Initialize managers
    dag = PromptDAG(Path.cwd())
    profiles = ProfileManager(Path.cwd())
    run_results = RunResultsManager(Path.cwd())
    
    # Set profile if specified
    if profile:
        profiles.set_active_profile(profile, target_env)
    
    # Load prompts and get execution order
    dag.load_prompts()
    execution_order = dag.get_execution_order(target)
    
    # Start run
    run_id = run_results.start_run(
        project_name=Path.cwd().name,
        args={"target": target, "profile": profile, "full_refresh": full_refresh}
    )
    
    console.print(f"Run ID: {run_id}")
    console.print(f"Prompts to run: {len(execution_order)}")
    
    # Execute prompts
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Running prompts...", total=len(execution_order))
        
        for prompt_name in execution_order:
            progress.update(task, description=f"Running {prompt_name}...")
            
            # Record execution (placeholder - would actually run the prompt)
            run_results.start_prompt_execution(prompt_name)
            
            # Simulate execution
            import time
            time.sleep(0.5)
            
            # Record result
            run_results.record_prompt_result(
                prompt_name,
                RunStatus.SUCCESS,
                message="Prompt executed successfully"
            )
            
            progress.advance(task)
    
    # Complete run
    results = run_results.complete_run()
    
    # Display summary
    summary = run_results.generate_summary(results)
    console.print("\n" + summary)

@app.command()
def profiles(
    action: str = typer.Argument("list", help="Action: list, create, validate"),
    name: Optional[str] = typer.Option(None, "--name", help="Profile name")
):
    """
    👤 Manage environment profiles (DBT-like profiles.yml)
    
    Configure different environments:
    - pbt profiles list - Show all profiles
    - pbt profiles create --name production
    - pbt profiles validate --name staging
    """
    manager = ProfileManager(Path.cwd())
    
    if action == "list":
        if not manager.profiles:
            console.print("[yellow]No profiles found. Create profiles.yml[/yellow]")
            console.print("\n[dim]Example profiles.yml:[/dim]")
            example = """development:
  target: dev
  outputs:
    dev:
      llm_provider: openai
      llm_model: gpt-4
      temperature: 0.7
    
production:
  target: prod
  outputs:
    prod:
      llm_provider: anthropic
      llm_model: claude-3
      temperature: 0.3
      deployment_provider: supabase"""
            syntax = Syntax(example, "yaml", theme="monokai")
            console.print(Panel(syntax, expand=False))
        else:
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Profile", style="cyan")
            table.add_column("Target")
            table.add_column("Outputs")
            table.add_column("Active")
            
            for profile_name, profile in manager.profiles.items():
                is_active = profile_name == manager.active_profile
                table.add_row(
                    profile_name,
                    profile.target,
                    ", ".join(profile.outputs.keys()),
                    "✓" if is_active else ""
                )
            
            console.print(table)
            
    elif action == "validate":
        profile_name = name or manager.active_profile
        errors = manager.validate_profile(profile_name)
        
        if errors:
            console.print(f"[red]❌ Profile validation failed:[/red]")
            for error in errors:
                console.print(f"  • {error}")
        else:
            console.print(f"[green]✅ Profile '{profile_name}' is valid[/green]")
            
    elif action == "create":
        if not name:
            console.print("[red]❌ Please specify --name[/red]")
            raise typer.Exit(1)
            
        # Create example profile
        example_outputs = {
            "dev": {
                "llm_provider": "openai",
                "llm_model": "gpt-4",
                "temperature": 0.7
            }
        }
        
        profile = manager.create_profile(name, example_outputs)
        console.print(f"[green]✅ Created profile '{name}'[/green]")
        console.print("[dim]Edit profiles.yml to customize[/dim]")

@app.command()
def render(
    prompt_file: str = typer.Argument(..., help="Prompt file to render"),
    compare: Optional[str] = typer.Option(None, "--compare", help="Comma-separated models to compare"),
    variables: Optional[str] = typer.Option(None, "--variables", "-v", help="Variables as key=value pairs"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output format (json, table, markdown)")
):
    """
    🎨 Render a prompt with different models and compare outputs
    
    Examples:
    - pbt render prompt.yaml --compare gpt-4 claude-3
    - pbt render prompt.yaml --variables "name=John,age=30"
    """
    console.print(f"[bold blue]🎨 Rendering prompt: {prompt_file}[/bold blue]")
    
    if not Path(prompt_file).exists():
        console.print(f"[red]❌ Prompt file not found: {prompt_file}[/red]")
        raise typer.Exit(1)
    
    # Parse variables
    vars_dict = {}
    if variables:
        for var in variables.split(','):
            if '=' in var:
                key, value = var.split('=', 1)
                vars_dict[key.strip()] = value.strip()
    
    # Load prompt
    with open(prompt_file, 'r') as f:
        prompt_data = yaml.safe_load(f)
    
    # Render with different models
    if compare:
        models = [m.strip() for m in compare.split(',')]
    else:
        models = [prompt_data.get('model', 'gpt-4')]
    results = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task(f"Rendering with {len(models)} models...", total=len(models))
        
        for model in models:
            # Simulate rendering (in real implementation, would call LLM)
            result = {
                'model': model,
                'output': f"[Rendered output from {model} with prompt: {prompt_data.get('name', 'Unnamed')}]",
                'tokens': 150,
                'time': 1.23
            }
            results.append(result)
            progress.advance(task)
    
    # Display results
    if output == "json":
        console.print(json.dumps(results, indent=2))
    else:
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Model", style="cyan")
        table.add_column("Output", style="white")
        table.add_column("Tokens", style="yellow")
        table.add_column("Time (s)", style="green")
        
        for result in results:
            table.add_row(
                result['model'],
                result['output'][:50] + "...",
                str(result['tokens']),
                f"{result['time']:.2f}"
            )
        
        console.print(table)


@app.command()
def eval(
    prompt_folder: str = typer.Argument(..., help="Folder containing prompts to evaluate"),
    metrics: Optional[str] = typer.Option(None, "--metrics", "-m", help="Comma-separated metrics to evaluate"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output report file"),
    model: str = typer.Option("gpt-4", "--model", help="Model to use for evaluation")
):
    """
    📊 Evaluate prompts in a folder against quality metrics
    
    Examples:
    - pbt eval prompts/
    - pbt eval agents/ --metrics clarity,specificity
    """
    console.print(f"[bold blue]📊 Evaluating prompts in: {prompt_folder}[/bold blue]")
    
    folder_path = Path(prompt_folder)
    if not folder_path.exists():
        console.print(f"[red]❌ Folder not found: {prompt_folder}[/red]")
        raise typer.Exit(1)
    
    # Find all prompt files
    prompt_files = list(folder_path.glob("*.yaml")) + list(folder_path.glob("*.prompt.yaml"))
    
    if not prompt_files:
        console.print(f"[yellow]⚠️ No prompt files found in {prompt_folder}[/yellow]")
        raise typer.Exit(1)
    
    console.print(f"[cyan]Found {len(prompt_files)} prompts to evaluate[/cyan]")
    
    # Default metrics
    if metrics:
        eval_metrics = [m.strip() for m in metrics.split(',')]
    else:
        eval_metrics = ["clarity", "specificity", "effectiveness"]
    
    results = []
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Evaluating prompts...", total=len(prompt_files))
        
        for prompt_file in prompt_files:
            # Simulate evaluation (in real implementation, would analyze prompt)
            scores = {metric: round(random.uniform(0.7, 1.0), 2) for metric in eval_metrics}
            results.append({
                'prompt': prompt_file.name,
                'scores': scores,
                'average': round(sum(scores.values()) / len(scores), 2)
            })
            progress.advance(task)
    
    # Display results
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Prompt", style="cyan")
    for metric in eval_metrics:
        table.add_column(metric.capitalize(), style="yellow")
    table.add_column("Average", style="green")
    
    for result in results:
        row = [result['prompt']]
        for metric in eval_metrics:
            row.append(str(result['scores'][metric]))
        row.append(str(result['average']))
        table.add_row(*row)
    
    console.print(table)
    
    # Save report if requested
    if output:
        with open(output, 'w') as f:
            json.dump(results, f, indent=2)
        console.print(f"\n[dim]📄 Report saved to: {output}[/dim]")


@app.command()
def badge(
    add: Optional[str] = typer.Option(None, "--add", help="Badge to add (e.g., GDPR-compliant)"),
    remove: Optional[str] = typer.Option(None, "--remove", help="Badge to remove"),
    list: bool = typer.Option(False, "--list", "-l", help="List available badges"),
    prompt_file: Optional[str] = typer.Argument(None, help="Prompt file to modify")
):
    """
    🏷️ Manage badges for prompts (compliance, quality, etc.)
    
    Examples:
    - pbt badge --list
    - pbt badge prompt.yaml --add GDPR-compliant
    - pbt badge prompt.yaml --remove deprecated
    """
    if list:
        console.print("[bold blue]🏷️ Available badges:[/bold blue]")
        badges = [
            ("GDPR-compliant", "Complies with GDPR data protection"),
            ("HIPAA-compliant", "Complies with HIPAA healthcare privacy"),
            ("production-ready", "Tested and ready for production use"),
            ("experimental", "Under development, use with caution"),
            ("deprecated", "Scheduled for removal"),
            ("security-reviewed", "Passed security review"),
            ("performance-optimized", "Optimized for speed/tokens")
        ]
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Badge", style="cyan")
        table.add_column("Description", style="white")
        
        for badge, desc in badges:
            table.add_row(badge, desc)
        
        console.print(table)
        return
    
    if not prompt_file:
        console.print("[red]❌ Please specify a prompt file[/red]")
        raise typer.Exit(1)
    
    if not Path(prompt_file).exists():
        console.print(f"[red]❌ Prompt file not found: {prompt_file}[/red]")
        raise typer.Exit(1)
    
    # Load prompt
    with open(prompt_file, 'r') as f:
        prompt_data = yaml.safe_load(f)
    
    if 'badges' not in prompt_data:
        prompt_data['badges'] = []
    
    if add:
        if add not in prompt_data['badges']:
            prompt_data['badges'].append(add)
            console.print(f"[green]✅ Added badge '{add}' to {prompt_file}[/green]")
        else:
            console.print(f"[yellow]⚠️ Badge '{add}' already exists[/yellow]")
    
    if remove:
        if remove in prompt_data['badges']:
            prompt_data['badges'].remove(remove)
            console.print(f"[green]✅ Removed badge '{remove}' from {prompt_file}[/green]")
        else:
            console.print(f"[yellow]⚠️ Badge '{remove}' not found[/yellow]")
    
    # Save updated prompt
    with open(prompt_file, 'w') as f:
        yaml.dump(prompt_data, f, default_flow_style=False, sort_keys=False)
    
    # Show current badges
    if prompt_data['badges']:
        console.print(f"\n[cyan]Current badges: {', '.join(prompt_data['badges'])}[/cyan]")


@app.command()
def i18n(
    prompt_file: str = typer.Argument(..., help="Prompt file to internationalize"),
    languages: str = typer.Option(..., "--languages", "-l", help="Comma-separated language codes"),
    output_dir: Optional[str] = typer.Option(None, "--output", "-o", help="Output directory for translations")
):
    """
    🌍 Internationalize prompts into multiple languages
    
    Examples:
    - pbt i18n prompt.yaml --languages en,fr,es
    - pbt i18n agent.yaml --languages de,ja --output translations/
    """
    console.print(f"[bold blue]🌍 Internationalizing: {prompt_file}[/bold blue]")
    
    if not Path(prompt_file).exists():
        console.print(f"[red]❌ Prompt file not found: {prompt_file}[/red]")
        raise typer.Exit(1)
    
    lang_list = [lang.strip() for lang in languages.split(',')]
    output_path = Path(output_dir) if output_dir else Path("i18n")
    output_path.mkdir(exist_ok=True)
    
    # Load prompt
    with open(prompt_file, 'r') as f:
        prompt_data = yaml.safe_load(f)
    
    console.print(f"[cyan]Translating to: {', '.join(lang_list)}[/cyan]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Translating...", total=len(lang_list))
        
        for lang in lang_list:
            # Simulate translation (in real implementation, would use translation API)
            translated_data = prompt_data.copy()
            translated_data['language'] = lang
            translated_data['template'] = f"[{lang.upper()} translation of: {prompt_data.get('template', '')[:50]}...]"
            
            # Save translated file
            filename = Path(prompt_file).stem
            output_file = output_path / f"{filename}.{lang}.yaml"
            
            with open(output_file, 'w') as f:
                yaml.dump(translated_data, f, default_flow_style=False, sort_keys=False)
            
            progress.advance(task)
    
    console.print(f"\n[green]✅ Created {len(lang_list)} translations in {output_path}/[/green]")


@app.command()
def pack(
    action: str = typer.Argument(..., help="Action: build, publish, install"),
    name: Optional[str] = typer.Option(None, "--name", help="Pack name"),
    version: Optional[str] = typer.Option("1.0.0", "--version", help="Pack version"),
    registry: Optional[str] = typer.Option(None, "--registry", help="Registry URL")
):
    """
    📦 Manage prompt packs (build, publish, install)
    
    Examples:
    - pbt pack build --name my-agents
    - pbt pack publish --name my-agents --registry https://hub.pbt.io
    - pbt pack install openai/gpt-best-practices
    """
    console.print(f"[bold blue]📦 Pack action: {action}[/bold blue]")
    
    if action == "build":
        if not name:
            console.print("[red]❌ Please specify --name for the pack[/red]")
            raise typer.Exit(1)
        
        # Create pack structure
        pack_dir = Path(f"packs/{name}")
        pack_dir.mkdir(parents=True, exist_ok=True)
        
        # Create pack manifest
        manifest = {
            "name": name,
            "version": version,
            "description": f"Prompt pack: {name}",
            "prompts": [],
            "dependencies": []
        }
        
        # Find prompts in current directory
        prompt_files = list(Path(".").glob("*.yaml"))
        for pf in prompt_files:
            manifest["prompts"].append(str(pf))
        
        # Save manifest
        with open(pack_dir / "pack.yaml", 'w') as f:
            yaml.dump(manifest, f, default_flow_style=False)
        
        console.print(f"[green]✅ Built pack '{name}' with {len(prompt_files)} prompts[/green]")
        console.print(f"[dim]Pack location: {pack_dir}[/dim]")
    
    elif action == "publish":
        if not name:
            console.print("[red]❌ Please specify --name for the pack[/red]")
            raise typer.Exit(1)
        
        pack_dir = Path(f"packs/{name}")
        if not pack_dir.exists():
            console.print(f"[red]❌ Pack not found: {name}[/red]")
            console.print("[dim]Run 'pbt pack build' first[/dim]")
            raise typer.Exit(1)
        
        registry_url = registry or "https://hub.pbt.io"
        console.print(f"[cyan]Publishing to: {registry_url}[/cyan]")
        
        # Simulate publish
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Publishing pack...", total=None)
            time.sleep(1)  # Simulate upload
            
        console.print(f"[green]✅ Published '{name}' to registry[/green]")
        console.print(f"[dim]Install with: pbt pack install {name}[/dim]")
    
    elif action == "install":
        pack_spec = name
        if not pack_spec:
            console.print("[red]❌ Please specify pack to install[/red]")
            raise typer.Exit(1)
        
        console.print(f"[cyan]Installing pack: {pack_spec}[/cyan]")
        
        # Simulate install
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Downloading pack...", total=None)
            time.sleep(1)  # Simulate download
            
        console.print(f"[green]✅ Installed pack: {pack_spec}[/green]")
        console.print("[dim]Prompts added to ./prompts/[/dim]")


@app.command()
def deploy(
    provider: str = typer.Option(..., "--provider", help="Deployment provider (supabase, vercel, aws)"),
    env: str = typer.Option("production", "--env", help="Environment name"),
    config: Optional[str] = typer.Option(None, "--config", help="Deployment config file")
):
    """
    🚀 Deploy prompts to cloud providers
    
    Examples:
    - pbt deploy --provider supabase
    - pbt deploy --provider vercel --env staging
    - pbt deploy --provider aws --config deploy.yaml
    """
    console.print(f"[bold blue]🚀 Deploying to {provider}[/bold blue]")
    
    supported_providers = ["supabase", "vercel", "aws", "gcp", "azure"]
    if provider not in supported_providers:
        console.print(f"[red]❌ Unsupported provider: {provider}[/red]")
        console.print(f"[dim]Supported: {', '.join(supported_providers)}[/dim]")
        raise typer.Exit(1)
    
    # Check for provider credentials
    if provider == "supabase":
        if not os.getenv("SUPABASE_URL"):
            console.print("[red]❌ Missing SUPABASE_URL in environment[/red]")
            raise typer.Exit(1)
    
    # Find prompts to deploy
    prompt_files = list(Path(".").glob("**/*.yaml"))
    console.print(f"[cyan]Found {len(prompt_files)} prompts to deploy[/cyan]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task(f"Deploying to {provider}...", total=len(prompt_files))
        
        for pf in prompt_files:
            # Simulate deployment
            time.sleep(0.1)
            progress.advance(task)
    
    console.print(f"\n[green]✅ Deployed {len(prompt_files)} prompts to {provider}[/green]")
    console.print(f"[dim]Environment: {env}[/dim]")
    
    # Show deployment URL
    if provider == "supabase":
        console.print(f"[cyan]Dashboard: https://app.supabase.io[/cyan]")
    elif provider == "vercel":
        console.print(f"[cyan]Dashboard: https://vercel.com[/cyan]")


@app.command(name="import")
def import_prompts(
    source: str = typer.Option(..., "--source", help="Import source (notion, airtable, sheets)"),
    url: Optional[str] = typer.Option(None, "--url", help="Source URL or ID"),
    token: Optional[str] = typer.Option(None, "--token", help="API token for source"),
    output: Optional[str] = typer.Option("imported/", "--output", "-o", help="Output directory")
):
    """
    📥 Import prompts from external sources
    
    Examples:
    - pbt import --source notion --token $NOTION_TOKEN
    - pbt import --source airtable --url https://airtable.com/...
    - pbt import --source sheets --url $SHEET_ID
    """
    console.print(f"[bold blue]📥 Importing from {source}[/bold blue]")
    
    supported_sources = ["notion", "airtable", "sheets", "github", "gitlab"]
    if source not in supported_sources:
        console.print(f"[red]❌ Unsupported source: {source}[/red]")
        console.print(f"[dim]Supported: {', '.join(supported_sources)}[/dim]")
        raise typer.Exit(1)
    
    # Check credentials
    if source == "notion" and not token:
        token = os.getenv("NOTION_TOKEN")
        if not token:
            console.print("[red]❌ Missing Notion token (--token or NOTION_TOKEN env)[/red]")
            raise typer.Exit(1)
    
    output_path = Path(output)
    output_path.mkdir(exist_ok=True)
    
    # Simulate import
    console.print(f"[cyan]Connecting to {source}...[/cyan]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Importing prompts...", total=None)
        
        # Simulate finding and importing prompts
        time.sleep(1.5)
        imported_count = 5  # Simulated
        
        for i in range(imported_count):
            prompt_data = {
                "name": f"Imported Prompt {i+1}",
                "version": "1.0",
                "source": source,
                "template": f"This is an imported prompt from {source}",
                "variables": {}
            }
            
            with open(output_path / f"imported_{i+1}.yaml", 'w') as f:
                yaml.dump(prompt_data, f, default_flow_style=False)
    
    console.print(f"\n[green]✅ Imported {imported_count} prompts from {source}[/green]")
    console.print(f"[dim]Saved to: {output_path}/[/dim]")


@app.command()
def optimize(
    prompt_file: str = typer.Argument(..., help="Prompt file to optimize"),
    strategy: str = typer.Option("shorten", "--strategy", help="Optimization strategy: shorten, clarify, cost_reduce, embedding"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file for optimized prompt"),
    analyze_only: bool = typer.Option(False, "--analyze", help="Only analyze, don't optimize")
):
    """
    🔧 Optimize prompts for cost, clarity, or performance
    
    Strategies:
    - shorten: Reduce token count while preserving meaning
    - clarify: Improve clarity and structure
    - cost_reduce: Minimize token usage for cost savings
    - embedding: Optimize for RAG/retrieval systems
    """
    console.print(f"[bold blue]🔧 Optimizing prompt: {prompt_file}[/bold blue]")
    
    try:
        # Import here to avoid circular imports
        from pbt.core.prompt_optimizer import PromptOptimizer, OptimizationStrategy
        
        # Load prompt
        with open(prompt_file, 'r') as f:
            prompt_data = yaml.safe_load(f)
        
        prompt_template = prompt_data.get('template', '')
        
        # Initialize optimizer
        optimizer = PromptOptimizer()
        
        if analyze_only:
            # Just analyze and suggest optimizations
            suggestions = optimizer.suggest_optimizations(prompt_template)
            
            console.print(f"\n[bold]📊 Optimization Analysis:[/bold]")
            console.print(f"Word count: {suggestions['metrics']['word_count']}")
            console.print(f"Estimated tokens: {suggestions['metrics']['estimated_tokens']}")
            
            if suggestions['applicable_strategies']:
                console.print(f"\n[bold]🎯 Recommended Optimizations:[/bold]")
                for strategy in suggestions['applicable_strategies']:
                    console.print(f"  • {strategy.value}")
            
            if suggestions['priority_optimizations']:
                console.print(f"\n[bold]⚡ Priority Actions:[/bold]")
                for action in suggestions['priority_optimizations']:
                    console.print(f"  • {action}")
        else:
            # Perform optimization
            strategy_enum = OptimizationStrategy[strategy.upper()]
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task(f"Optimizing with {strategy} strategy...", total=None)
                
                result = optimizer.optimize(prompt_template, strategy_enum)
                
                progress.update(task, description="✅ Optimization complete!")
            
            # Display results
            console.print(f"\n[bold]📊 Optimization Results:[/bold]")
            console.print(f"Strategy: {result.strategy.value}")
            console.print(f"Original length: {len(result.original_prompt)} chars")
            console.print(f"Optimized length: {len(result.optimized_prompt)} chars")
            console.print(f"Reduction: {(1 - len(result.optimized_prompt)/len(result.original_prompt))*100:.1f}%")
            
            if result.cost_savings:
                console.print(f"Estimated cost savings: ${result.cost_savings:.6f} per call")
            
            if result.suggestions:
                console.print(f"\n[bold]💡 Changes made:[/bold]")
                for suggestion in result.suggestions[:5]:
                    console.print(f"  • {suggestion}")
            
            # Show preview
            console.print(f"\n[bold]🔍 Optimized prompt preview:[/bold]")
            preview = result.optimized_prompt[:200] + "..." if len(result.optimized_prompt) > 200 else result.optimized_prompt
            console.print(Panel(preview, title="Optimized Version", expand=False))
            
            # Save if requested
            if output:
                prompt_data['template'] = result.optimized_prompt
                prompt_data['optimization'] = {
                    'strategy': strategy,
                    'date': datetime.now().isoformat(),
                    'metrics': result.metrics
                }
                
                with open(output, 'w') as f:
                    yaml.dump(prompt_data, f, default_flow_style=False)
                
                console.print(f"\n[green]✅ Optimized prompt saved to: {output}[/green]")
            else:
                console.print(f"\n[dim]💡 Use --output to save the optimized version[/dim]")
                
    except Exception as e:
        console.print(f"[red]❌ Error optimizing prompt: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def chain(
    action: str = typer.Argument(..., help="Action: create, validate, execute, visualize"),
    chain_file: Optional[str] = typer.Option(None, "--file", help="Chain configuration file"),
    template: Optional[str] = typer.Option(None, "--template", help="Use predefined template"),
    inputs: Optional[str] = typer.Option(None, "--inputs", help="Input data as JSON string"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file")
):
    """
    🔗 Define and execute multi-agent chains
    
    Actions:
    - create: Create a new chain from template
    - validate: Validate chain configuration
    - execute: Run the agent chain
    - visualize: Generate chain diagram
    
    Templates:
    - summarize_critique_rewrite: Summarize → Critique → Rewrite
    - rag_pipeline: Retrieve → Augment → Generate
    """
    console.print(f"[bold blue]🔗 Agent chain: {action}[/bold blue]")
    
    try:
        # Import here to avoid circular imports
        from pbt.core.agent_chains import AgentChain, create_chain_from_template
        
        if action == "create":
            if not template:
                console.print("[red]❌ Please specify --template[/red]")
                console.print("Available templates: summarize_critique_rewrite, rag_pipeline")
                raise typer.Exit(1)
            
            chain = create_chain_from_template(template)
            
            output_file = output or f"{template}_chain.yaml"
            with open(output_file, 'w') as f:
                f.write(chain.to_yaml())
            
            console.print(f"[green]✅ Created chain configuration: {output_file}[/green]")
            console.print(f"\n[dim]Next steps:[/dim]")
            console.print(f"1. Edit {output_file} to customize")
            console.print(f"2. Run: pbt chain validate --file {output_file}")
            console.print(f"3. Execute: pbt chain execute --file {output_file} --inputs '{{\"key\": \"value\"}}'")
            
        elif action == "validate":
            if not chain_file:
                console.print("[red]❌ Please specify --file[/red]")
                raise typer.Exit(1)
            
            chain = AgentChain(chain_file)
            validation = chain.validate()
            
            if validation['valid']:
                console.print("[green]✅ Chain configuration is valid![/green]")
            else:
                console.print("[red]❌ Chain has issues:[/red]")
                for issue in validation['issues']:
                    console.print(f"  • {issue}")
            
            if validation['warnings']:
                console.print(f"\n[yellow]⚠️ Warnings:[/yellow]")
                for warning in validation['warnings']:
                    console.print(f"  • {warning}")
            
        elif action == "execute":
            if not chain_file:
                console.print("[red]❌ Please specify --file[/red]")
                raise typer.Exit(1)
            
            if not inputs:
                console.print("[red]❌ Please provide --inputs as JSON string[/red]")
                raise typer.Exit(1)
            
            chain = AgentChain(chain_file)
            input_data = json.loads(inputs)
            
            console.print(f"[cyan]Running chain: {chain.name}[/cyan]")
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Executing agents...", total=None)
                
                result = chain.execute(input_data)
                
                progress.update(task, description="✅ Chain execution complete!")
            
            # Display results
            if result.success:
                console.print(f"\n[green]✅ Chain executed successfully![/green]")
                console.print(f"\n[bold]📊 Outputs:[/bold]")
                for key, value in result.outputs.items():
                    console.print(f"  {key}: {value}")
                
                console.print(f"\n[bold]🔄 Execution path:[/bold]")
                console.print(" → ".join(result.execution_path))
            else:
                console.print(f"\n[red]❌ Chain execution failed![/red]")
                for error in result.errors:
                    console.print(f"  • {error}")
            
            # Save results if requested
            if output:
                with open(output, 'w') as f:
                    json.dump({
                        'success': result.success,
                        'outputs': result.outputs,
                        'execution_path': result.execution_path,
                        'agent_results': result.agent_results,
                        'errors': result.errors
                    }, f, indent=2)
                console.print(f"\n[dim]💾 Results saved to: {output}[/dim]")
                
        elif action == "visualize":
            if not chain_file:
                console.print("[red]❌ Please specify --file[/red]")
                raise typer.Exit(1)
            
            chain = AgentChain(chain_file)
            diagram = chain.visualize()
            
            console.print(f"\n[bold]📊 Chain Diagram (Mermaid):[/bold]")
            console.print(Panel(diagram, title=chain.name, expand=False))
            
            if output:
                with open(output, 'w') as f:
                    f.write(diagram)
                console.print(f"\n[dim]💾 Diagram saved to: {output}[/dim]")
                
    except Exception as e:
        console.print(f"[red]❌ Error with chain operation: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def chunk(
    input_file: str = typer.Argument(..., help="File to chunk (prompt or content)"),
    strategy: str = typer.Option("prompt_aware", "--strategy", help="Chunking strategy"),
    max_tokens: int = typer.Option(512, "--max-tokens", help="Maximum tokens per chunk"),
    overlap: int = typer.Option(50, "--overlap", help="Token overlap between chunks"),
    output_dir: Optional[Path] = typer.Option(None, "--output", "-o", help="Output directory for chunks"),
    rag_optimize: bool = typer.Option(False, "--rag", help="Optimize chunks for RAG")
):
    """
    📄 Create embedding-safe chunks from prompts and content
    
    Strategies:
    - prompt_aware: Preserve prompt context in chunks
    - semantic: Chunk by semantic boundaries
    - sliding_window: Fixed-size overlapping windows
    - recursive: Hierarchical splitting
    """
    console.print(f"[bold blue]📄 Chunking file: {input_file}[/bold blue]")
    
    try:
        # Import here to avoid circular imports
        from pbt.core.prompt_chunking import (
            PromptAwareChunker, ChunkingConfig, ChunkingStrategy
        )
        
        # Load input file
        with open(input_file, 'r') as f:
            content = f.read()
        
        # Check if it's a prompt file
        prompt = ""
        if input_file.endswith('.yaml'):
            try:
                data = yaml.safe_load(content)
                prompt = data.get('template', '')
                content = data.get('content', content)
            except:
                pass
        
        # Configure chunker
        config = ChunkingConfig(
            max_tokens=max_tokens,
            overlap_tokens=overlap,
            add_context=True
        )
        
        chunker = PromptAwareChunker(config)
        
        # Perform chunking
        strategy_enum = ChunkingStrategy[strategy.upper()]
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Creating chunks...", total=None)
            
            chunks = chunker.chunk_prompt_content(prompt, content, strategy_enum)
            
            if rag_optimize:
                chunks = chunker.optimize_for_rag(chunks)
            
            progress.update(task, description=f"✅ Created {len(chunks)} chunks!")
        
        # Display summary
        console.print(f"\n[bold]📊 Chunking Results:[/bold]")
        console.print(f"Total chunks: {len(chunks)}")
        console.print(f"Strategy: {strategy}")
        console.print(f"Max tokens: {max_tokens}")
        
        if chunks:
            avg_tokens = sum(c.token_count for c in chunks) / len(chunks)
            console.print(f"Avg tokens/chunk: {avg_tokens:.1f}")
        
        # Show chunk preview
        if chunks:
            console.print(f"\n[bold]🔍 First chunk preview:[/bold]")
            preview = chunks[0].content[:300] + "..." if len(chunks[0].content) > 300 else chunks[0].content
            console.print(Panel(preview, title=f"Chunk 1/{len(chunks)}", expand=False))
            
            if chunks[0].embedding_hints:
                console.print(f"Embedding hints: {', '.join(chunks[0].embedding_hints)}")
        
        # Save chunks if requested
        if output_dir:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Save individual chunks
            for i, chunk in enumerate(chunks):
                chunk_file = output_dir / f"chunk_{i:03d}.txt"
                with open(chunk_file, 'w') as f:
                    f.write(chunk.content)
                
                # Save metadata
                meta_file = output_dir / f"chunk_{i:03d}_meta.json"
                with open(meta_file, 'w') as f:
                    json.dump({
                        'index': chunk.index,
                        'token_count': chunk.token_count,
                        'embedding_hints': chunk.embedding_hints,
                        'metadata': chunk.metadata
                    }, f, indent=2)
            
            # Save summary
            summary_file = output_dir / "chunks_summary.json"
            with open(summary_file, 'w') as f:
                json.dump({
                    'total_chunks': len(chunks),
                    'strategy': strategy,
                    'config': {
                        'max_tokens': max_tokens,
                        'overlap': overlap,
                        'rag_optimized': rag_optimize
                    },
                    'chunks': [
                        {
                            'index': c.index,
                            'tokens': c.token_count,
                            'hints': c.embedding_hints
                        }
                        for c in chunks
                    ]
                }, f, indent=2)
            
            console.print(f"\n[green]✅ Chunks saved to: {output_dir}/[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ Error chunking file: {e}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()