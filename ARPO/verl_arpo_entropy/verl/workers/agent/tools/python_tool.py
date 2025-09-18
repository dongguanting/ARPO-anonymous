import ast
import subprocess
from typing import Tuple

from verl.workers.agent.tools.base_tool import BaseTool


class PythonTool(BaseTool):
    """Python code execution tool using local conda environment"""
    
    def __init__(self, conda_path: str, conda_env: str):
        """
        Initialize Python tool
        
        Args:
            conda_path: conda installation path
            conda_env: conda environment name
        """
        self.conda_path = conda_path
        self.conda_env = conda_env
        self.python_path = f"{conda_path}/envs/{conda_env}/bin/python"

    @property
    def name(self) -> str:
        return "python_interpreter"
    
    @property
    def trigger_tag(self) -> str:
        return "python"
    
    def execute(self, code: str, timeout: int = 120) -> str:
        """Execute Python code and return results"""
        result, report = self._run_code(code, timeout)
        
        if report == "Done":
            return result
        else:
            return report
    
    def _run_code(self, code: str, timeout: int) -> Tuple[str, str]:
        """Run Python code in conda environment and return results and status"""
        # Handle interactive code
        code = self._preprocess_code(code)
        
        try:
            # Use subprocess.run for synchronous command execution
            process = subprocess.run(
                [self.python_path, '-c', code],
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False 
            )

            if process.returncode == 0:
                return process.stdout.strip(), "Done"
            else:
                return "", process.stderr.strip()

        except subprocess.TimeoutExpired:
            return "", f"Execution timeout (exceeded {timeout} seconds)"
        except Exception as e:
            return "", f"Execution exception: {str(e)}"
    
    def _preprocess_code(self, code: str) -> str:
        """
        Preprocess Python code, handle interactive code
        Convert the last expression to a print statement (if not already print)
        """
        try:
            tree = ast.parse(code)
            if tree.body:
                last_expr = tree.body[-1]
                if isinstance(last_expr, ast.Expr):
                    # Only convert when the last expression is not a print call
                    if not (isinstance(last_expr.value, ast.Call) 
                            and isinstance(last_expr.value.func, ast.Name) 
                            and last_expr.value.func.id == 'print'):
                        print_call = ast.Expr(
                            value=ast.Call(
                                func=ast.Name(id='print', ctx=ast.Load()),
                                args=[last_expr.value],
                                keywords=[]
                            )
                        )
                        tree.body[-1] = print_call
                        code = ast.unparse(tree)
        except:
            pass  # Keep original code unchanged
        
        return code
