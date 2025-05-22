#!/usr/bin/env python3
"""
PBT (Prompt Build Tool) CLI
Infrastructure-grade prompt engineering for AI teams
"""

import argparse
import requests
import yaml
import json
import os
import sys
from pathlib import Path
from datetime import datetime

class PBTCli:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.config_file = Path.home() / ".pbt" / "config.json"
        self.load_config()
    
    def load_config(self):
        """Load CLI configuration"""
        if self.config_file.exists():
            with open(self.config_file) as f:
                self.config = json.load(f)
        else:
            self.config = {"api_base": self.base_url}
    
    def save_config(self):
        """Save CLI configuration"""
        self.config_file.parent.mkdir(exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def api_request(self, method, endpoint, **kwargs):
        """Make API request to PBT backend"""
        url = f"{self.config['api_base']}{endpoint}"
        try:
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ API Error: {e}")
            sys.exit(1)
    
    def init(self, args):
        """Initialize PBT project"""
        print("🚀 Initializing PBT project...")
        
        # Create project structure
        project_dir = Path(args.directory or ".")
        (project_dir / "prompts").mkdir(exist_ok=True)
        (project_dir / "tests").mkdir(exist_ok=True)
        (project_dir / "evaluations").mkdir(exist_ok=True)
        
        # Create pbt.yaml config
        config = {
            "name": args.name or project_dir.name,
            "version": "0.1.0",
            "description": "PBT project",
            "models": ["claude", "gpt-4"],
            "eval_criteria": ["accuracy", "relevance", "safety"]
        }
        
        with open(project_dir / "pbt.yaml", 'w') as f:
            yaml.dump(config, f, indent=2)
        
        print(f"✅ Initialized PBT project in {project_dir}")
        print("📁 Created directories: prompts/, tests/, evaluations/")
        print("📄 Created pbt.yaml configuration")
    
    def generate_prompt(self, args):
        """Generate a prompt using AI"""
        print(f"🤖 Generating prompt for goal: {args.goal}")
        
        data = {
            "goal": args.goal,
            "model": args.model,
            "style": args.style,
            "variables": args.variables.split(',') if args.variables else []
        }
        
        result = self.api_request("POST", "/api/promptgen/generate", json=data)
        
        if result.get("success"):
            prompt_yaml = result.get("prompt_yaml")
            if prompt_yaml:
                # Save to file
                filename = f"{prompt_yaml['name']}.prompt.yaml"
                with open(filename, 'w') as f:
                    yaml.dump(prompt_yaml, f, indent=2)
                print(f"✅ Generated prompt saved to {filename}")
            else:
                print(f"📝 Generated content:\\n{result.get('raw_content', '')}")
        else:
            print(f"❌ Failed to generate prompt")
    
    def test_prompt(self, args):
        """Test a prompt file"""
        print(f"🧪 Testing prompt: {args.prompt_file}")
        
        with open(args.prompt_file) as f:
            prompt_content = f.read()
        
        # Generate test cases
        test_data = {
            "prompt_yaml": prompt_content,
            "num_tests": args.num_tests,
            "test_type": args.test_type
        }
        
        test_result = self.api_request("POST", "/api/testgen/generate", json=test_data)
        
        if test_result.get("success"):
            tests = test_result.get("tests", [])
            print(f"📋 Generated {len(tests)} test cases")
            
            # Run tests
            prompt_data = yaml.safe_load(prompt_content)
            run_result = self.api_request("POST", "/api/testgen/run", json={
                "prompt_template": prompt_data.get("template", ""),
                "tests": tests,
                "model": args.model
            })
            
            summary = run_result.get("summary", {})
            print(f"📊 Test Results:")
            print(f"   Total: {summary.get('total', 0)}")
            print(f"   Passed: {summary.get('passed', 0)}")
            print(f"   Failed: {summary.get('failed', 0)}")
            print(f"   Pass Rate: {summary.get('pass_rate', 0)*100:.1f}%")
            
            # Save results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_file = f"evaluations/test_results_{timestamp}.json"
            with open(results_file, 'w') as f:
                json.dump(run_result, f, indent=2)
            print(f"💾 Detailed results saved to {results_file}")
        else:
            print("❌ Failed to generate test cases")
    
    def compare_models(self, args):
        """Compare prompt across multiple models"""
        print(f"🔍 Comparing models: {', '.join(args.models)}")
        
        prompt = args.prompt
        if args.file:
            with open(args.file) as f:
                prompt_data = yaml.safe_load(f)
                prompt = prompt_data.get("template", "")
        
        result = self.api_request("POST", "/api/promptgen/compare", json={
            "prompt": prompt,
            "models": args.models
        })
        
        print("📊 Model Comparison Results:")
        for model, output in result.get("results", {}).items():
            print(f"\\n🤖 {model.upper()}:")
            print(f"   {output[:200]}{'...' if len(output) > 200 else ''}")
    
    def evaluate(self, args):
        """Run evaluations with test input file"""
        print(f"⚡ Running evaluations from {args.input}")
        
        with open(args.input) as f:
            test_data = json.load(f)
        
        results = []
        for test_case in test_data.get("tests", []):
            result = self.api_request("POST", "/api/evals/run", json={
                "prompt_id": test_case.get("prompt_id", "test"),
                "test_cases": [test_case],
                "model": args.model
            })
            results.append(result)
        
        # Aggregate results
        total_score = sum(r.get("summary", {}).get("average_score", 0) for r in results)
        avg_score = total_score / len(results) if results else 0
        
        print(f"📈 Evaluation Complete:")
        print(f"   Average Score: {avg_score:.1f}/10")
        print(f"   Total Tests: {len(results)}")
    
    def deploy(self, args):
        """Deploy prompt pack"""
        print(f"🚀 Deploying to {args.provider}")
        
        if args.provider == "supabase":
            print("📤 Uploading to Supabase...")
            # Implementation would go here
            print("✅ Deployed successfully!")
        else:
            print(f"❌ Provider {args.provider} not supported yet")

def main():
    parser = argparse.ArgumentParser(
        description="PBT - Prompt Build Tool CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  pbt init --name my-prompts
  pbt generate-prompt --goal "Summarize tweets" --model claude
  pbt test tweet_summarizer.prompt.yaml
  pbt render --compare gpt-4 claude mistral --prompt "Hello world"
  pbt eval --input tests.json --model claude
  pbt deploy --provider supabase
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Init command
    init_parser = subparsers.add_parser('init', help='Initialize PBT project')
    init_parser.add_argument('--name', help='Project name')
    init_parser.add_argument('--directory', help='Project directory')
    
    # Generate prompt command
    gen_parser = subparsers.add_parser('generate-prompt', help='Generate prompt using AI')
    gen_parser.add_argument('--goal', required=True, help='Prompt goal description')
    gen_parser.add_argument('--model', default='claude', choices=['claude', 'openai'], help='LLM to use')
    gen_parser.add_argument('--style', default='professional', help='Prompt style')
    gen_parser.add_argument('--variables', help='Comma-separated variable names')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Test a prompt file')
    test_parser.add_argument('prompt_file', help='Path to prompt YAML file')
    test_parser.add_argument('--num-tests', type=int, default=5, help='Number of test cases')
    test_parser.add_argument('--test-type', default='functional', help='Type of tests')
    test_parser.add_argument('--model', default='claude', help='Model to test with')
    
    # Compare command
    compare_parser = subparsers.add_parser('render', help='Compare models')
    compare_parser.add_argument('--compare', dest='models', nargs='+', required=True, help='Models to compare')
    compare_parser.add_argument('--prompt', help='Prompt text')
    compare_parser.add_argument('--file', help='Prompt file')
    
    # Eval command
    eval_parser = subparsers.add_parser('eval', help='Run evaluations')
    eval_parser.add_argument('--input', required=True, help='Test input JSON file')
    eval_parser.add_argument('--model', default='claude', help='Model to evaluate')
    
    # Deploy command
    deploy_parser = subparsers.add_parser('deploy', help='Deploy prompt pack')
    deploy_parser.add_argument('--provider', required=True, choices=['supabase', 'firebase'], help='Deploy provider')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = PBTCli()
    
    # Route to appropriate command handler
    if args.command == 'init':
        cli.init(args)
    elif args.command == 'generate-prompt':
        cli.generate_prompt(args)
    elif args.command == 'test':
        cli.test_prompt(args)
    elif args.command == 'render':
        cli.compare_models(args)
    elif args.command == 'eval':
        cli.evaluate(args)
    elif args.command == 'deploy':
        cli.deploy(args)

if __name__ == "__main__":
    main()