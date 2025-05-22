"""
PBT Code Converter - Automatically convert Python agent code to use PBT
"""

import os
import re
import ast
import yaml
from pathlib import Path
from typing import List, Dict, Tuple
from .documentation import DocumentationGenerator
from .validator import validate_generated_code


class PromptExtractor:
    """Extract prompts from Python code"""
    
    def __init__(self, python_file: str):
        self.python_file = Path(python_file)
        self.prompts = []
        self.code_content = ""
        
    def extract_prompts(self) -> List[Dict]:
        """Extract all prompts from Python file"""
        with open(self.python_file, 'r') as f:
            self.code_content = f.read()
        
        # Use regex to find prompt patterns since they're simple
        prompts = self._regex_extraction()
        
        return prompts
    
    def _regex_extraction(self) -> List[Dict]:
        """Extract prompts using regex patterns"""
        prompts = []
        
        # Find all functions with agent in name
        agent_functions = re.findall(r'def\s+(\w*agent\w*)\s*\([^)]*\):', self.code_content)
        
        for func_name in agent_functions:
            # Find the function body
            func_pattern = rf'def\s+{func_name}\s*\([^)]*\):(.*?)(?=\ndef|\nif\s+__name__|\Z)'
            func_match = re.search(func_pattern, self.code_content, re.DOTALL)
            
            if func_match:
                func_body = func_match.group(1)
                
                # Look for f-string prompts
                fstring_pattern = r'prompt\s*=\s*f["\']([^"\']*)["\']'
                fstring_match = re.search(fstring_pattern, func_body)
                
                if fstring_match:
                    template = fstring_match.group(1)
                    # Convert {variable} to {{ variable }}
                    template = re.sub(r'\{(\w+)\}', r'{{ \1 }}', template)
                    
                    prompts.append({
                        'name': func_name.replace('_agent', ''),
                        'function': func_name,
                        'content': template,
                        'variables': re.findall(r'\{\{\s*(\w+)\s*\}\}', template)
                    })
        
        return prompts


class PBTConverter:
    """Convert Python agent code to use PBT"""
    
    def __init__(self, input_file: str, output_dir: str = None):
        self.input_file = Path(input_file)
        self.output_dir = Path(output_dir) if output_dir else self.input_file.parent
        self.prompts_dir = self.output_dir / "agents"
        self.doc_generator = DocumentationGenerator(style="google")
        
    def convert(self) -> Dict[str, str]:
        """Convert Python file to PBT format"""
        # Extract prompts from original file
        extractor = PromptExtractor(self.input_file)
        prompts = extractor.extract_prompts()
        
        # Create prompts directory
        self.prompts_dir.mkdir(exist_ok=True)
        
        # Generate YAML files
        yaml_files = self._create_yaml_files(prompts)
        
        # Generate converted Python file
        converted_python = self._create_converted_python(prompts)
        
        return {
            'yaml_files': yaml_files,
            'python_file': converted_python,
            'prompts_extracted': len(prompts)
        }
    
    def _create_yaml_files(self, prompts: List[Dict]) -> List[str]:
        """Create YAML files for extracted prompts"""
        yaml_files = []
        
        for prompt in prompts:
            # Generate filename
            name = prompt['name']
            filename = f"{name}.prompt.yaml"
            filepath = self.prompts_dir / filename
            
            # Create YAML content
            yaml_content = {
                'name': name.title(),
                'version': '1.0',
                'model': 'gpt-4',
                'template': prompt['content']
            }
            
            # Add test cases if variables exist
            if prompt.get('variables'):
                yaml_content['tests'] = [{
                    'input': {var: f'sample_{var}' for var in prompt['variables']},
                    'expected_contains': ['response']
                }]
            
            # Write YAML file
            with open(filepath, 'w') as f:
                yaml.dump(yaml_content, f, default_flow_style=False)
            
            yaml_files.append(str(filepath))
        
        return yaml_files
    
    def _create_converted_python(self, prompts: List[Dict]) -> str:
        """Create converted Python file - preserving original structure"""
        # Read original file
        with open(self.input_file, 'r') as f:
            original_content = f.read()
        
        # Add comprehensive file header documentation
        file_purpose = f"PBT-converted agent workflow from {self.input_file.name}"
        file_header = self.doc_generator.generate_file_header(
            self.input_file.stem + "_converted.py", 
            file_purpose
        )
        
        # Start with file header + original content
        converted_content = file_header + original_content
        
        # Find where to insert PBT imports (after last import/from statement)
        lines = converted_content.split('\n')
        insert_index = 0
        
        for i, line in enumerate(lines):
            if line.strip().startswith(('import ', 'from ')):
                insert_index = i + 1
            elif line.strip() == '' and insert_index > 0:
                continue  # Skip empty lines after imports
            elif insert_index > 0:
                break
        
        # Insert PBT imports and runners with documentation
        pbt_lines = [
            'from pbt.runtime import PromptRunner',
            '',
            '# =============================================================================',
            '# PBT (Prompt Build Tool) Integration',
            '# =============================================================================',
            '# The following PromptRunner instances load YAML prompt templates from the',
            '# agents/ directory. Each runner manages a specific prompt template and',
            '# handles LLM communication through the PBT runtime.',
            '',
            '# Initialize PBT PromptRunner instances'
        ]
        
        for prompt in prompts:
            name = prompt['name']
            pbt_lines.append(f'# Runner for {name} prompt template')
            pbt_lines.append(f'{name}_runner = PromptRunner("agents/{name}.prompt.yaml")')
            pbt_lines.append('')
        
        pbt_lines.append('# =============================================================================')
        pbt_lines.append('')
        
        # Insert PBT lines
        lines[insert_index:insert_index] = pbt_lines
        converted_content = '\n'.join(lines)
        
        # Replace agent functions
        for prompt in prompts:
            func_name = prompt['function']
            
            # Find the original function
            func_pattern = rf'(def\s+{func_name}\s*\([^)]*\):)(.*?)(?=\ndef|\nif\s+__name__|\Z)'
            func_match = re.search(func_pattern, converted_content, re.DOTALL)
            
            if func_match:
                func_signature = func_match.group(1)
                
                # Extract parameters from signature
                param_pattern = rf'def\s+{func_name}\s*\(([^)]*)\):'
                param_match = re.search(param_pattern, func_signature)
                params = param_match.group(1) if param_match else ''
                param_names = [p.strip() for p in params.split(',') if p.strip()]
                
                # Generate new function body with comprehensive documentation
                var_dict = ', '.join([f'"{name}": {name}' for name in param_names])
                runner_name = prompt['name']
                
                # Generate comprehensive docstring
                purpose = f"AI agent for {runner_name} operations using PBT prompt templates"
                docstring = self.doc_generator.generate_function_docstring(
                    func_name, param_names, purpose
                )
                
                # Generate function body with detailed comments
                function_body = f"""    # Prepare input variables for the PBT prompt template
    # Each variable corresponds to a placeholder in the YAML template
    variables = {{{var_dict}}}
    
    # Execute the prompt using PBT runtime
    # This loads the template from agents/{runner_name}.prompt.yaml and processes it
    # with the configured LLM model (Claude, GPT-4, etc.)
    return {runner_name}_runner.run(variables)"""
                
                # Properly indent the docstring
                indented_docstring = '\n'.join(['    ' + line if line.strip() else line 
                                               for line in docstring.split('\n')])
                
                new_function = f"""{func_signature}
{indented_docstring}
{function_body}"""
                
                # Replace the entire function
                converted_content = re.sub(func_pattern, new_function, converted_content, flags=re.DOTALL)
        
        # Remove hardcoded openai.api_key line
        converted_content = re.sub(r'openai\.api_key\s*=\s*[\'"][^\'"]*[\'"]', '', converted_content)
        
        # Clean up extra blank lines
        final_content = re.sub(r'\n{3,}', '\n\n', converted_content)
        
        # Validate the generated code before writing
        validation_result = validate_generated_code(final_content, f"{self.input_file.stem}_converted.py")
        
        if not validation_result['valid']:
            print(f"⚠️  Code validation found issues:")
            for error in validation_result['errors']:
                print(f"   Line {error.get('line', '?')}: {error['message']}")
            
            # Try to use fixed code if available
            if validation_result.get('fixes_applied'):
                print("✅ Automatically fixed syntax issues")
                final_content = validation_result['fixed_code']
            else:
                print("❌ Could not automatically fix all issues")
        
        # Write converted file
        output_file = self.output_dir / f"{self.input_file.stem}_converted.py"
        with open(output_file, 'w') as f:
            f.write(final_content)
        
        # Final validation check
        if validation_result['valid'] or validation_result.get('fix_successful'):
            print(f"✅ Generated valid Python code: {output_file}")
        else:
            print(f"⚠️  Generated code may have issues: {output_file}")
            print("   Please review the generated file manually")
        
        return str(output_file)


def convert_agent_file(input_file: str, output_dir: str = None) -> Dict[str, str]:
    """Main conversion function"""
    converter = PBTConverter(input_file, output_dir)
    return converter.convert()