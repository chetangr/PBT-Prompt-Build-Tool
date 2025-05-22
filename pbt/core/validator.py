"""
PBT Code Validator - Ensures generated code has no syntax errors
"""

import ast
import re
import subprocess
import tempfile
from pathlib import Path
from typing import List, Dict, Tuple, Optional


class CodeValidator:
    """Validates Python code for syntax errors and common issues"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def validate_python_code(self, code: str, filename: str = "generated_code.py") -> Dict[str, any]:
        """
        Comprehensive validation of Python code
        
        Args:
            code: The Python code to validate
            filename: Name for error reporting
            
        Returns:
            Dict with validation results
        """
        self.errors = []
        self.warnings = []
        
        # 1. Check for basic syntax errors
        syntax_valid = self._check_syntax(code, filename)
        
        # 2. Check indentation consistency
        indentation_valid = self._check_indentation(code)
        
        # 3. Check docstring formatting
        docstring_valid = self._check_docstrings(code)
        
        # 4. Check function structure
        structure_valid = self._check_function_structure(code)
        
        # 5. Compile check with py_compile
        compile_valid = self._check_compilation(code, filename)
        
        return {
            'valid': len(self.errors) == 0,
            'syntax_valid': syntax_valid,
            'indentation_valid': indentation_valid,
            'docstring_valid': docstring_valid,
            'structure_valid': structure_valid,
            'compile_valid': compile_valid,
            'errors': self.errors,
            'warnings': self.warnings,
            'line_count': len(code.split('\n'))
        }
    
    def _check_syntax(self, code: str, filename: str) -> bool:
        """Check for Python syntax errors using AST"""
        try:
            ast.parse(code, filename=filename)
            return True
        except SyntaxError as e:
            self.errors.append({
                'type': 'SyntaxError',
                'message': str(e),
                'line': e.lineno,
                'column': e.offset,
                'text': e.text
            })
            return False
        except Exception as e:
            self.errors.append({
                'type': 'ParseError',
                'message': str(e),
                'line': None,
                'column': None
            })
            return False
    
    def _check_indentation(self, code: str) -> bool:
        """Check for indentation consistency"""
        lines = code.split('\n')
        indentation_valid = True
        
        for i, line in enumerate(lines, 1):
            if line.strip():  # Skip empty lines
                # Check for mixed tabs and spaces
                if '\t' in line and ' ' in line.split('\t')[0]:
                    self.errors.append({
                        'type': 'IndentationError',
                        'message': 'Mixed tabs and spaces in indentation',
                        'line': i,
                        'text': line
                    })
                    indentation_valid = False
                
                # Check for proper indentation levels (multiples of 4)
                leading_spaces = len(line) - len(line.lstrip(' '))
                if leading_spaces % 4 != 0 and leading_spaces > 0:
                    self.warnings.append({
                        'type': 'IndentationWarning',
                        'message': 'Indentation is not a multiple of 4 spaces',
                        'line': i,
                        'text': line
                    })
        
        return indentation_valid
    
    def _check_docstrings(self, code: str) -> bool:
        """Check docstring formatting"""
        lines = code.split('\n')
        docstring_valid = True
        
        in_docstring = False
        docstring_start = None
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Check for docstring start
            if '"""' in stripped and not in_docstring:
                in_docstring = True
                docstring_start = i
                
                # Check if docstring is properly indented
                if line.startswith('"""'):
                    self.errors.append({
                        'type': 'DocstringError',
                        'message': 'Docstring must be indented inside function',
                        'line': i,
                        'text': line
                    })
                    docstring_valid = False
            
            elif '"""' in stripped and in_docstring:
                in_docstring = False
                docstring_start = None
        
        # Check for unclosed docstrings
        if in_docstring:
            self.errors.append({
                'type': 'DocstringError',
                'message': f'Unclosed docstring starting at line {docstring_start}',
                'line': docstring_start
            })
            docstring_valid = False
        
        return docstring_valid
    
    def _check_function_structure(self, code: str) -> bool:
        """Check function definition structure"""
        lines = code.split('\n')
        structure_valid = True
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Check function definitions
            if stripped.startswith('def '):
                # Check if function has proper colon
                if not line.rstrip().endswith(':'):
                    self.errors.append({
                        'type': 'FunctionError',
                        'message': 'Function definition must end with colon',
                        'line': i,
                        'text': line
                    })
                    structure_valid = False
                
                # Check if next non-empty line is indented
                next_line_idx = i
                while next_line_idx < len(lines) and not lines[next_line_idx].strip():
                    next_line_idx += 1
                
                if next_line_idx < len(lines):
                    next_line = lines[next_line_idx]
                    if next_line.strip() and not next_line.startswith('    '):
                        self.errors.append({
                            'type': 'FunctionError',
                            'message': 'Function body must be indented',
                            'line': next_line_idx + 1,
                            'text': next_line
                        })
                        structure_valid = False
        
        return structure_valid
    
    def _check_compilation(self, code: str, filename: str) -> bool:
        """Check if code compiles using py_compile"""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            # Try to compile
            result = subprocess.run(
                ['python3', '-m', 'py_compile', temp_file],
                capture_output=True,
                text=True
            )
            
            # Clean up temp file
            Path(temp_file).unlink()
            
            if result.returncode != 0:
                self.errors.append({
                    'type': 'CompilationError',
                    'message': result.stderr.strip(),
                    'line': None
                })
                return False
            
            return True
            
        except Exception as e:
            self.errors.append({
                'type': 'CompilationError',
                'message': f'Failed to check compilation: {str(e)}',
                'line': None
            })
            return False
    
    def fix_common_issues(self, code: str) -> str:
        """Automatically fix common syntax issues"""
        lines = code.split('\n')
        fixed_lines = []
        
        for line in lines:
            # Fix mixed indentation (convert tabs to spaces)
            line = line.expandtabs(4)
            
            # Fix docstring indentation issues
            if '"""' in line and line.strip().startswith('"""'):
                # If it's a standalone docstring line, ensure proper indentation
                leading_spaces = len(line) - len(line.lstrip())
                if leading_spaces == 0:
                    line = '    ' + line.strip()
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)


def validate_generated_code(code: str, filename: str = "generated_code.py") -> Dict[str, any]:
    """
    Validate generated Python code and return detailed results
    
    Args:
        code: Python code to validate
        filename: Filename for error reporting
        
    Returns:
        Dict with validation results and any fixes needed
    """
    validator = CodeValidator()
    
    # First validation pass
    result = validator.validate_python_code(code, filename)
    
    # If there are fixable errors, try to fix them
    if not result['valid']:
        fixed_code = validator.fix_common_issues(code)
        
        # Validate the fixed code
        fixed_result = validator.validate_python_code(fixed_code, filename)
        
        result['fixed_code'] = fixed_code
        result['fix_successful'] = fixed_result['valid']
        result['fixes_applied'] = not result['valid'] and fixed_result['valid']
    
    return result