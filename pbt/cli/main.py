#!/usr/bin/env python3
"""
PBT CLI - Main entry point
"""

import typer
from typing import Optional, List
from pathlib import Path
import yaml
import json
import os
import sys
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
        raise typer.Exit()

@app.callback()
def main(
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
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path")
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

@app.command()
def test(
    prompt_file: Path = typer.Argument(..., help="Path to prompt YAML file"),
    num_tests: int = typer.Option(5, "--num-tests", "-n", help="Number of test cases to generate"),
    test_type: str = typer.Option("functional", "--test-type", help="Type of tests (functional, edge_case, performance)"),
    model: str = typer.Option("claude", "--model", help="Model to test with"),
    save_results: bool = typer.Option(True, "--save/--no-save", help="Save test results to file")
):
    """
    🧪 Test a prompt file
    
    Generates test cases and runs them against the prompt template.
    """
    if not prompt_file.exists():
        console.print(f"[red]❌ Prompt file not found: {prompt_file}[/red]")
        raise typer.Exit(1)
    
    console.print(f"[bold blue]🧪 Testing prompt: {prompt_file}[/bold blue]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        # Load prompt
        task1 = progress.add_task("Loading prompt...", total=None)
        with open(prompt_file) as f:
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
    summary = run_result.get("summary", {})
    results = run_result.get("results", [])
    
    console.print(f"\n[bold]📊 Test Results:[/bold]")
    
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

@app.command()
def compare(
    prompt: str = typer.Option(..., "--prompt", help="Prompt text to compare"),
    models: List[str] = typer.Option(["claude", "gpt-4"], "--models", help="Models to compare"),
    file: Optional[Path] = typer.Option(None, "--file", help="Load prompt from file")
):
    """
    🔍 Compare prompt across multiple models
    
    Runs the same prompt across different LLM providers and shows results.
    """
    if file:
        if not file.exists():
            console.print(f"[red]❌ File not found: {file}[/red]")
            raise typer.Exit(1)
        
        with open(file) as f:
            prompt_data = yaml.safe_load(f)
            prompt = prompt_data.get("template", "")
    
    console.print(f"[bold blue]🔍 Comparing across models: {', '.join(models)}[/bold blue]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Running comparisons...", total=len(models))
        
        generator = PromptGenerator()
        results = generator.compare_models(prompt, models)
        
        progress.update(task, advance=len(models), description="✅ Comparison complete!")
    
    # Display results
    console.print(f"\n[bold]📊 Model Comparison Results:[/bold]")
    
    for model, output in results.get("results", {}).items():
        console.print(f"\n[bold cyan]🤖 {model.upper()}:[/bold cyan]")
        
        # Truncate long outputs
        display_output = output
        if len(output) > 300:
            display_output = output[:300] + "..."
        
        console.print(Panel(display_output, title=f"{model} Response", expand=False))

@app.command()
def eval(
    input_file: Path = typer.Option(..., "--input", help="JSON file with test cases"),
    model: str = typer.Option("claude", "--model", help="Model to evaluate"),
    output_file: Optional[Path] = typer.Option(None, "--output", help="Save results to file")
):
    """
    ⚡ Run evaluations with test input file
    
    Loads test cases from JSON and runs comprehensive evaluations.
    """
    if not input_file.exists():
        console.print(f"[red]❌ Input file not found: {input_file}[/red]")
        raise typer.Exit(1)
    
    console.print(f"[bold blue]⚡ Running evaluations from: {input_file}[/bold blue]")
    
    with open(input_file) as f:
        test_data = json.load(f)
    
    evaluator = PromptEvaluator()
    results = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        tests = test_data.get("tests", [])
        task = progress.add_task("Running evaluations...", total=len(tests))
        
        for i, test_case in enumerate(tests):
            progress.update(task, description=f"Evaluating test {i+1}/{len(tests)}")
            
            result = evaluator.run_evaluation(test_case, model)
            results.append(result)
            
            progress.advance(task)
    
    # Calculate summary
    total_score = sum(r.get("summary", {}).get("average_score", 0) for r in results)
    avg_score = total_score / len(results) if results else 0
    
    console.print(f"\n[bold]📈 Evaluation Complete:[/bold]")
    console.print(f"Average Score: [{'green' if avg_score >= 8 else 'yellow' if avg_score >= 6 else 'red'}]{avg_score:.1f}/10[/]")
    console.print(f"Total Tests: {len(results)}")
    
    # Save results
    if output_file:
        with open(output_file, 'w') as f:
            json.dump({"results": results, "summary": {"average_score": avg_score}}, f, indent=2)
        console.print(f"💾 Results saved to: {output_file}")

@app.command()
def deploy(
    provider: str = typer.Option(..., "--provider", help="Deployment provider (supabase, firebase, huggingface)"),
    config_file: Optional[Path] = typer.Option(None, "--config", help="Deployment config file")
):
    """
    🚀 Deploy prompt pack
    
    Deploys prompt packs to various cloud providers.
    """
    console.print(f"[bold blue]🚀 Deploying to: {provider}[/bold blue]")
    
    deployer = PromptDeployer()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Deploying...", total=None)
        
        try:
            result = deployer.deploy(provider, config_file)
            progress.update(task, description="✅ Deployment complete!")
            
            console.print(f"[green]✅ Successfully deployed to {provider}![/green]")
            if result.get("url"):
                console.print(f"🔗 URL: {result['url']}")
                
        except Exception as e:
            console.print(f"[red]❌ Deployment failed: {e}[/red]")
            raise typer.Exit(1)

@app.command()
def serve(
    port: int = typer.Option(8000, "--port", help="Port to serve on"),
    host: str = typer.Option("127.0.0.1", "--host", help="Host to serve on"),
    reload: bool = typer.Option(False, "--reload", help="Enable auto-reload")
):
    """
    🌐 Start PBT server
    
    Starts the FastAPI server with web UI and API endpoints.
    """
    console.print(f"[bold blue]🌐 Starting PBT server on {host}:{port}[/bold blue]")
    
    try:
        import uvicorn
        from pbt.server.main import app
        
        uvicorn.run(
            "pbt.server.main:app",
            host=host,
            port=port,
            reload=reload
        )
    except ImportError:
        console.print("[red]❌ Server dependencies not installed. Install with: pip install 'pbt[server]'[/red]")
        raise typer.Exit(1)

if __name__ == "__main__":
    app()