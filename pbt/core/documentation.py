"""
PBT Documentation Generator - Automatic documentation and comments for all PBT operations
"""

import os
import re
from typing import Dict, List, Optional
from pathlib import Path


class DocumentationGenerator:
    """Generates comprehensive documentation and comments for PBT code"""
    
    def __init__(self, style: str = "google"):
        """
        Initialize documentation generator
        
        Args:
            style: Documentation style (google, numpy, sphinx)
        """
        self.style = style
        
    def generate_function_docstring(self, func_name: str, params: List[str], 
                                  purpose: str, return_type: str = "str") -> str:
        """
        Generate comprehensive docstring for a function
        
        Args:
            func_name: Name of the function
            params: List of parameter names
            purpose: Brief description of function purpose
            return_type: Expected return type
            
        Returns:
            str: Formatted docstring
        """
        if self.style == "google":
            return self._generate_google_docstring(func_name, params, purpose, return_type)
        elif self.style == "numpy":
            return self._generate_numpy_docstring(func_name, params, purpose, return_type)
        else:
            return self._generate_sphinx_docstring(func_name, params, purpose, return_type)
    
    def _generate_google_docstring(self, func_name: str, params: List[str], 
                                 purpose: str, return_type: str) -> str:
        """Generate Google-style docstring"""
        func_title = func_name.replace('_', ' ').title()
        
        docstring = f'''"""
{func_title} - {purpose}

This function is part of a PBT (Prompt Build Tool) workflow and provides
{purpose.lower()}. It integrates with PBT's prompt management system
for consistent, testable, and version-controlled prompt execution.

Args:'''
        
        for param in params:
            param_desc = self._generate_param_description(param)
            docstring += f'\n    {param} (str): {param_desc}'
        
        docstring += f'''

Returns:
    {return_type}: The processed output from the LLM model
    
Raises:
    ValueError: If required parameters are missing or invalid
    RuntimeError: If the PBT runtime encounters an error
    
Example:
    >>> result = {func_name}({self._generate_example_args(params)})
    >>> print(result)
    
Note:
    This function requires proper PBT configuration and valid API keys.
    See the project documentation for setup instructions.
"""'''
        
        return docstring
    
    def _generate_numpy_docstring(self, func_name: str, params: List[str], 
                                purpose: str, return_type: str) -> str:
        """Generate NumPy-style docstring"""
        func_title = func_name.replace('_', ' ').title()
        
        docstring = f'''"""
    {func_title} - {purpose}
    
    This function is part of a PBT (Prompt Build Tool) workflow.
    
    Parameters
    ----------'''
        
        for param in params:
            param_desc = self._generate_param_description(param)
            docstring += f'\n    {param} : str\n        {param_desc}'
        
        docstring += f'''
    
    Returns
    -------
    {return_type}
        The processed output from the LLM model
        
    Examples
    --------
    >>> result = {func_name}({self._generate_example_args(params)})
    >>> print(result)
    """'''
        
        return docstring
    
    def _generate_sphinx_docstring(self, func_name: str, params: List[str], 
                                 purpose: str, return_type: str) -> str:
        """Generate Sphinx-style docstring"""
        func_title = func_name.replace('_', ' ').title()
        
        docstring = f'''"""
    {func_title} - {purpose}
    
    This function is part of a PBT (Prompt Build Tool) workflow.
    '''
        
        for param in params:
            param_desc = self._generate_param_description(param)
            docstring += f'\n    :param {param}: {param_desc}\n    :type {param}: str'
        
        docstring += f'''
    :returns: The processed output from the LLM model
    :rtype: {return_type}
    
    :raises ValueError: If required parameters are missing or invalid
    :raises RuntimeError: If the PBT runtime encounters an error
    """'''
        
        return docstring
    
    def _generate_param_description(self, param: str) -> str:
        """Generate intelligent parameter descriptions"""
        param_lower = param.lower()
        
        descriptions = {
            'content': 'The main content to be processed by the prompt',
            'text': 'Input text for processing',
            'summary': 'A summary or condensed version of content',
            'critique': 'Critical analysis or feedback',
            'feedback': 'User or system feedback',
            'query': 'A query or question to be processed',
            'prompt': 'The prompt text or template',
            'message': 'A message or communication',
            'data': 'Input data for processing',
            'input': 'General input for the function',
            'context': 'Contextual information for processing'
        }
        
        # Check for exact matches
        if param_lower in descriptions:
            return descriptions[param_lower]
        
        # Check for partial matches
        for key, desc in descriptions.items():
            if key in param_lower:
                return desc
        
        # Default description
        return f'Input parameter for the {param} field'
    
    def _generate_example_args(self, params: List[str]) -> str:
        """Generate example arguments for function calls"""
        examples = []
        for param in params:
            param_lower = param.lower()
            if 'content' in param_lower:
                examples.append(f'{param}="Sample content to process"')
            elif 'summary' in param_lower:
                examples.append(f'{param}="Brief summary text"')
            elif 'critique' in param_lower:
                examples.append(f'{param}="Constructive feedback"')
            else:
                examples.append(f'{param}="sample_{param.lower()}"')
        
        return ', '.join(examples)
    
    def generate_inline_comments(self, code_block: str, context: str) -> str:
        """
        Add intelligent inline comments to code blocks
        
        Args:
            code_block: The code to add comments to
            context: Context about what the code does
            
        Returns:
            str: Code with added comments
        """
        lines = code_block.split('\n')
        commented_lines = []
        
        for line in lines:
            stripped = line.strip()
            
            # Add comments for common patterns
            if 'variables = {' in stripped:
                commented_lines.append(line)
                commented_lines.append('    # Prepare input variables for the PBT prompt template')
            elif '.run(variables)' in stripped:
                commented_lines.append('    # Execute the prompt using PBT runtime and return the result')
                commented_lines.append(line)
            elif 'PromptRunner(' in stripped:
                commented_lines.append(line + '  # Load prompt template from YAML file')
            else:
                commented_lines.append(line)
        
        return '\n'.join(commented_lines)
    
    def generate_file_header(self, filename: str, purpose: str, author: str = "PBT Generated") -> str:
        """
        Generate comprehensive file header documentation
        
        Args:
            filename: Name of the file
            purpose: Purpose of the file
            author: Author name
            
        Returns:
            str: File header with documentation
        """
        return f'''"""
{filename} - {purpose}

This file was generated by PBT (Prompt Build Tool) and contains AI agent
functions that have been converted to use PBT's prompt management system.

PBT provides:
- Version-controlled prompt templates in YAML format
- Testable and reusable prompt components
- Multi-model support (Claude, GPT-4, etc.)
- Automatic environment variable management
- Professional documentation and testing

Author: {author}
Generated by: PBT (Prompt Build Tool)
Documentation: https://github.com/your-org/prompt-build-tool

Usage:
    Ensure you have a .env file with your API keys:
    - ANTHROPIC_API_KEY=your-anthropic-key
    - OPENAI_API_KEY=your-openai-key
    
    Run the functions directly or integrate into your workflow.

Dependencies:
    - pbt (Prompt Build Tool)
    - anthropic (for Claude models)
    - openai (for GPT models)
"""

'''