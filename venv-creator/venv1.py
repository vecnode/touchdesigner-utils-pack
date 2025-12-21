# 21-12-2025 vecnode
# Updated: Persistent terminal with PID tracking and venv management

import sys
import os
import subprocess
import shutil
import re
import time


class TerminalManager:
    """Manages a persistent terminal process and allows command execution"""
    
    def __init__(self, shell='powershell', visible=True):
        """
        Initialize terminal manager
        Args:
            shell: 'powershell' or 'cmd'
            visible: Whether to show a visible terminal window
        """
        self.shell = shell
        self.visible = visible
        self.process = None
        self.pid = None
        self.project_folder = get_project_folder()
        
    def launch_terminal(self):
        """Launch a persistent terminal process and track its PID"""
        try:
            # Windows-specific: CREATE_NEW_CONSOLE flag to show a visible window
            creation_flags = 0
            if self.visible:
                creation_flags = subprocess.CREATE_NEW_CONSOLE
            
            if self.shell.lower() == 'powershell':
                # Launch PowerShell with -NoExit to keep it open
                # Use -NoProfile for faster startup
                self.process = subprocess.Popen(
                    ['powershell.exe', '-NoExit', '-NoProfile', '-Command', 
                     f'cd "{self.project_folder}"; Write-Host "Terminal PID: $PID"'],
                    creationflags=creation_flags,
                    cwd=self.project_folder
                )
            else:  # cmd
                # Launch cmd with /K to keep it open
                self.process = subprocess.Popen(
                    ['cmd.exe', '/K', f'cd /d "{self.project_folder}" && echo Terminal PID: %PID%'],
                    creationflags=creation_flags,
                    cwd=self.project_folder
                )
            
            self.pid = self.process.pid
            print(f"Terminal launched successfully. PID: {self.pid}")
            print(f"Terminal window is {'visible' if self.visible else 'hidden'}")
            
            return True
        except Exception as e:
            print(f"Failed to launch terminal: {e}")
            return False
    
    def execute_command(self, command, wait=True, timeout=60):
        """
        Execute a command in a new subprocess (not in the visible terminal)
        The visible terminal is for monitoring; commands run directly
        Args:
            command: Command string to execute
            wait: Whether to wait for command completion
            timeout: Timeout in seconds
        Returns:
            tuple: (success, output_lines)
        """
        try:
            if self.shell.lower() == 'powershell':
                cmd_list = ['powershell.exe', '-Command', command]
            else:  # cmd
                cmd_list = ['cmd.exe', '/C', command]
            
            if wait:
                # Use Popen with polling to avoid blocking TouchDesigner
                process = subprocess.Popen(
                    cmd_list,
                    cwd=self.project_folder,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                # Poll process without blocking TouchDesigner
                start_time = time.time()
                while process.poll() is None:
                    elapsed = time.time() - start_time
                    if elapsed > timeout:
                        process.kill()
                        print(f"Command timed out after {timeout} seconds")
                        return False, []
                    time.sleep(0.01)  # Small delay to allow TouchDesigner to process events
                
                # Process completed, get output
                stdout, stderr = process.communicate()
                output_lines = stdout.splitlines() if stdout else []
                error_lines = stderr.splitlines() if stderr else []
                
                if process.returncode == 0:
                    return True, output_lines
                else:
                    print(f"Command failed with return code {process.returncode}")
                    if error_lines:
                        print("Error output:", "\n".join(error_lines))
                    return False, output_lines + error_lines
            else:
                # Don't wait, just launch
                subprocess.Popen(
                    cmd_list,
                    cwd=self.project_folder,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                return True, []
                
        except Exception as e:
            print(f"Error executing command: {e}")
            return False, []
    
    def execute_command_in_terminal(self, command):
        """
        Execute a command that will be visible in the terminal window
        This creates a new process that runs in the same directory
        """
        try:
            if self.shell.lower() == 'powershell':
                subprocess.Popen(
                    ['powershell.exe', '-NoExit', '-Command', command],
                    creationflags=subprocess.CREATE_NEW_CONSOLE if self.visible else 0,
                    cwd=self.project_folder
                )
            else:  # cmd
                subprocess.Popen(
                    ['cmd.exe', '/K', command],
                    creationflags=subprocess.CREATE_NEW_CONSOLE if self.visible else 0,
                    cwd=self.project_folder
                )
            return True
        except Exception as e:
            print(f"Error executing command in terminal: {e}")
            return False
    
    def get_pid(self):
        """Get the terminal process PID"""
        return self.pid
    
    def is_running(self):
        """Check if terminal process is still running"""
        return self.process and self.process.poll() is None
    
    def close(self):
        """Close the terminal process"""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except:
                try:
                    self.process.kill()
                except:
                    pass
            print(f"Terminal {self.pid} closed")


def get_project_folder():
    """Directory of the currently running .toe file"""
    return os.getcwd()


def get_python_version():
    """Python version used by TouchDesigner"""
    return sys.version


def get_python_executable_path():
    """Path to the Python executable running this script (TouchDesigner's Python)"""
    return sys.executable


def get_touchdesigner_python_version():
    """Get TouchDesigner's Python version (major.minor)"""
    version_info = sys.version_info
    return f"{version_info.major}.{version_info.minor}"


def find_system_python():
    """
    Find system Python executable matching TouchDesigner's Python version (3.9)
    Returns path to system Python or None if not found
    """
    target_version = get_touchdesigner_python_version()  # e.g., "3.9"
    td_full_version = sys.version.split()[0]  # Full version string
    print(f"TouchDesigner Python version: {td_full_version} ({target_version})")
    print(f"Looking for Python {target_version} to match TouchDesigner's Python version")
    
    # Try common Python executable names
    python_names = ['python.exe', 'python3.exe', 'python']
    
    # First, try to find python in PATH and check version
    # Exclude TouchDesigner paths explicitly
    td_paths = ['TouchDesigner', 'Derivative', 'Program Files\\Derivative', 'Program Files (x86)\\Derivative']
    
    for python_name in python_names:
        try:
            result = subprocess.run(
                ['where', python_name] if os.name == 'nt' else ['which', python_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                for python_path in result.stdout.strip().split('\n'):
                    python_path = python_path.strip()
                    # Verify it's not TouchDesigner's Python - check both case variations
                    python_path_lower = python_path.lower()
                    is_td_python = any(td_path.lower() in python_path_lower for td_path in td_paths)
                    
                    if not is_td_python:
                        # Check version
                        try:
                            version_result = subprocess.run(
                                [python_path, '--version'],
                                capture_output=True,
                                text=True,
                                timeout=5
                            )
                            if version_result.returncode == 0:
                                version_str = version_result.stdout.strip()
                                # Check if version matches (e.g., "Python 3.9.x")
                                if target_version in version_str:
                                    print(f"Found matching Python {target_version}: {python_path}")
                                    print(f"  System Python version: {version_str}")
                                    return python_path
                        except:
                            continue
        except:
            continue
    
    # Try common installation paths, prioritizing Python 3.9
    version_dirs = [
        f'Python{target_version.replace(".", "")}',  # Python39
        'Python39',  # Explicit fallback
        'Python310',
        'Python311',
        'Python312',
    ]
    
    common_bases = [
        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs', 'Python'),
        os.path.join(os.environ.get('PROGRAMFILES', ''), 'Python'),
        'C:\\Python39',
        'C:\\Python310',
        'C:\\Python311',
        'C:\\Python312',
    ]
    
    # First pass: try to find exact version match
    for base_path in common_bases:
        if not base_path or not os.path.exists(base_path):
            continue
        # Check version-specific directories first
        for version_dir in version_dirs:
            version_path = os.path.join(base_path, version_dir) if base_path.endswith('Python') else base_path
            if os.path.exists(version_path):
                for python_name in python_names:
                    python_path = os.path.join(version_path, python_name)
                    if os.path.exists(python_path):
                        if 'TouchDesigner' not in python_path and 'Derivative' not in python_path:
                            # Verify version
                            try:
                                version_result = subprocess.run(
                                    [python_path, '--version'],
                                    capture_output=True,
                                    text=True,
                                    timeout=5
                                )
                                if version_result.returncode == 0 and target_version in version_result.stdout:
                                    version_str = version_result.stdout.strip()
                                    print(f"Found matching Python {target_version}: {python_path}")
                                    print(f"  System Python version: {version_str}")
                                    return python_path
                            except:
                                continue
    
    # Second pass: any Python that's not TouchDesigner's
    for base_path in common_bases:
        if not base_path or not os.path.exists(base_path):
            continue
        for python_name in python_names:
            python_path = os.path.join(base_path, python_name)
            if os.path.exists(python_path):
                python_path_lower = python_path.lower()
                is_td_python = any(td_path.lower() in python_path_lower for td_path in td_paths)
                
                if not is_td_python:
                    # Get version for display
                    try:
                        version_result = subprocess.run(
                            [python_path, '--version'],
                            capture_output=True,
                            text=True,
                            timeout=5
                        )
                        version_str = version_result.stdout.strip() if version_result.returncode == 0 else "unknown"
                    except:
                        version_str = "unknown"
                    print(f"Found system Python (version may differ): {python_path}")
                    print(f"  System Python version: {version_str}")
                    print(f"  Warning: May not match TouchDesigner's Python {target_version}")
                    return python_path
    
    # Last resort: try py launcher with version specification
    print("Trying Python launcher (py) with version specification...")
    try:
        # Try py -3.9 first
        result = subprocess.run(
            ['py', '-3.9', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"Found Python via launcher: py -3.9")
            print(f"  Python version: {result.stdout.strip()}")
            return ['py', '-3.9']  # Return as list for subprocess
    except:
        pass
    
    print("ERROR: Could not find a suitable system Python installation.")
    print("Please install Python 3.9 from python.org or Microsoft Store.")
    print("TouchDesigner's Python cannot be used to create virtual environments.")
    return None


def check_venv_python_version():
    """Check Python version of existing venv"""
    venv_path = os.path.join(get_project_folder(), 'venv')
    python_exe = os.path.join(venv_path, 'Scripts', 'python.exe')
    
    if not os.path.exists(python_exe):
        return None, None
    
    try:
        result = subprocess.run(
            [python_exe, '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version_str = result.stdout.strip()
            # Extract version like "3.9.5" -> "3.9"
            match = re.search(r'(\d+\.\d+)', version_str)
            if match:
                return match.group(1), version_str
            return None, version_str
    except:
        pass
    
    return None, None


def check_venv_exists():
    """Check if venv/ exists and if Python version matches TouchDesigner"""
    venv_path = os.path.join(get_project_folder(), 'venv')
    if not os.path.exists(os.path.join(venv_path, 'Scripts', 'activate.bat')):
        print("No virtual environment found at:", venv_path)
        return False
    
    print("Virtual environment exists at:", venv_path)
    
    # Check if Python version matches
    venv_version, venv_full_version = check_venv_python_version()
    td_version = get_touchdesigner_python_version()
    td_full_version = sys.version.split()[0]
    
    if venv_version:
        print(f"Venv Python version: {venv_full_version} ({venv_version})")
        print(f"TouchDesigner Python version: {td_full_version} ({td_version})")
        if venv_version != td_version:
            print(f"WARNING: Python version mismatch! Venv was created with Python {venv_version}, but TouchDesigner uses Python {td_version}")
            print("The venv needs to be recreated with the correct Python version.")
            return False
        else:
            print("✓ Python versions match!")
    
    return True


def create_venv(terminal_manager=None, force_recreate=False):
    """
    Create a virtual environment in the project folder using system Python
    Args:
        terminal_manager: Optional TerminalManager instance for logging
        force_recreate: If True, delete existing venv and recreate
    Returns:
        bool: Success status
    """
    venv_path = os.path.join(get_project_folder(), 'venv')
    
    # Check if venv exists and version matches
    if not force_recreate and check_venv_exists():
        print("Virtual environment already exists with correct Python version")
        return True
    
    # If venv exists but version doesn't match, delete it
    if os.path.exists(venv_path):
        print("Removing existing venv with incompatible Python version...")
        try:
            shutil.rmtree(venv_path)
            print("Old venv removed")
        except Exception as e:
            print(f"Warning: Could not remove old venv: {e}")
            return False
    
    # Find system Python matching TouchDesigner's version (not TouchDesigner's Python)
    system_python = find_system_python()
    
    if system_python is None:
        print("Cannot create venv: No suitable system Python found")
        return False
    
    try:
        print(f"Creating virtual environment at: {venv_path}")
        
        # Handle py launcher (returns list) vs direct path (string)
        if isinstance(system_python, list):
            python_cmd = system_python + ['-m', 'venv', venv_path]
            display_python = ' '.join(system_python)
        else:
            python_cmd = [system_python, '-m', 'venv', venv_path]
            display_python = system_python
        
        print(f"Using Python: {display_python}")
        
        # Get full version of system Python for display (quick, non-blocking)
        try:
            version_cmd = system_python if isinstance(system_python, list) else [system_python]
            version_process = subprocess.Popen(
                version_cmd + ['--version'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            # Quick poll for version (should be instant)
            version_start = time.time()
            while version_process.poll() is None:
                if time.time() - version_start > 2:
                    break
                time.sleep(0.01)
            if version_process.returncode == 0:
                stdout_ver, _ = version_process.communicate()
                if stdout_ver:
                    print(f"  System Python version: {stdout_ver.strip()}")
        except:
            pass
        
        # Use system Python to create venv via subprocess (non-blocking)
        # This avoids using TouchDesigner's Python which doesn't have venv launchers
        print("  Starting venv creation (non-blocking)...")
        process = subprocess.Popen(
            python_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=get_project_folder()
        )
        
        # Poll process without blocking TouchDesigner
        timeout = 60
        start_time = time.time()
        while process.poll() is None:
            if time.time() - start_time > timeout:
                process.kill()
                print("Virtual environment creation timed out")
                return False
            time.sleep(0.01)  # Small delay to allow TouchDesigner to process events
        
        # Process completed, get output
        stdout, stderr = process.communicate()
        
        if process.returncode == 0:
            print("Virtual environment created successfully")
            # Verify the created venv's Python version
            venv_python = os.path.join(venv_path, 'Scripts', 'python.exe')
            if os.path.exists(venv_python):
                try:
                    # Quick version check (non-blocking)
                    venv_version_process = subprocess.Popen(
                        [venv_python, '--version'],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    # Poll briefly for version
                    venv_version_start = time.time()
                    while venv_version_process.poll() is None:
                        if time.time() - venv_version_start > 2:
                            break
                        time.sleep(0.01)
                    if venv_version_process.returncode == 0:
                        stdout_ver, _ = venv_version_process.communicate()
                        print(f"  Created venv Python version: {stdout_ver.strip()}")
                except:
                    pass
            
            if terminal_manager:
                # Log to terminal window
                terminal_manager.execute_command_in_terminal(
                    f'Write-Host "Virtual environment created at {venv_path}" -ForegroundColor Green'
                )
            
            return True
        else:
            print(f"Failed to create virtual environment:")
            if stderr:
                print(stderr)
            return False
            
    except Exception as e:
        print(f"Failed to create virtual environment: {e}")
        return False


def install_numpy_in_venv(terminal_manager=None):
    """
    Install numpy in the virtual environment (compatible with Python 3.9)
    Args:
        terminal_manager: Optional TerminalManager instance for logging/execution
    Returns:
        bool: Success status
    """
    venv_path = os.path.join(get_project_folder(), 'venv')
    pip_executable = os.path.join(venv_path, 'Scripts', 'pip.exe')
    
    if not os.path.exists(pip_executable):
        print("pip executable not found in venv")
        return False
    
    # Determine numpy version based on TouchDesigner's Python version
    td_version = get_touchdesigner_python_version()
    td_full_version = sys.version.split()[0]
    print(f"TouchDesigner Python version: {td_full_version} ({td_version})")
    
    if td_version == "3.9":
        # NumPy 2.x requires Python 3.10+, so use 1.x for Python 3.9
        numpy_version = "numpy<2.0"  # Install latest 1.x version
        print(f"Installing numpy 1.x (compatible with Python {td_version})...")
    else:
        numpy_version = "numpy"  # Use latest version
        print(f"Installing latest numpy (compatible with Python {td_version})...")
    
    try:
        
        # Option 1: Use terminal manager to execute (visible in terminal)
        if terminal_manager:
            pip_path = pip_executable.replace('\\', '/')
            command = f'& "{pip_path}" install "{numpy_version}"'
            success, output = terminal_manager.execute_command(command, wait=True, timeout=300)
            
            if success:
                print("numpy installed successfully")
                # Extract and print numpy version from output
                for line in output:
                    print(line)
                    if "Successfully installed numpy" in line or "numpy-" in line:
                        # Try to extract version
                        version_match = re.search(r'numpy-([\d.]+)', line)
                        if version_match:
                            print(f"  Installed numpy version: {version_match.group(1)}")
                return True
            else:
                print("Failed to install numpy via terminal manager")
                return False
        else:
            # Option 2: Direct subprocess execution (non-blocking)
            print("  Starting numpy installation (non-blocking)...")
            process = subprocess.Popen(
                [pip_executable, 'install', numpy_version],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Poll process without blocking TouchDesigner
            timeout = 300  # 5 minute timeout
            start_time = time.time()
            while process.poll() is None:
                elapsed = time.time() - start_time
                if elapsed > timeout:
                    process.kill()
                    print("numpy installation timed out")
                    return False
                # Show progress every 5 seconds
                if int(elapsed) % 5 == 0 and elapsed > 0:
                    print(f"  Installing... ({int(elapsed)}s elapsed)")
                time.sleep(0.01)  # Small delay to allow TouchDesigner to process events
            
            # Process completed, get output
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                print("numpy installed successfully")
                if stdout:
                    print(stdout)
                # Extract and print numpy version from output
                if stdout:
                    version_match = re.search(r'Successfully installed numpy-([\d.]+)', stdout)
                    if version_match:
                        print(f"  Installed numpy version: {version_match.group(1)}")
                return True
            else:
                print(f"Failed to install numpy:")
                if stderr:
                    print(stderr)
                return False
            
    except Exception as e:
        print(f"Error installing numpy: {e}")
        return False


def add_venv_to_sys_path():
    """Add the virtual environment's site-packages directory to sys.path"""
    project_folder = get_project_folder()
    venv_path = os.path.join(project_folder, 'venv')
    site_packages_path = os.path.join(venv_path, 'Lib', 'site-packages')
    
    if os.path.exists(site_packages_path):
        if site_packages_path not in sys.path:
            sys.path.insert(0, site_packages_path)  # Insert at beginning for priority
            print(f"Added {site_packages_path} to sys.path")
            return True
        else:
            print("Path already exists in sys.path")
            return True
    else:
        print(f"Site-packages directory not found: {site_packages_path}")
        return False


def test_numpy_import():
    """Test if numpy can be imported"""
    try:
        import numpy as np
        print("✓ Successfully imported numpy")
        print(f"  NumPy version: {np.__version__}")
        print(f"  NumPy location: {np.__file__}")
        return True
    except ImportError as e:
        print(f"✗ Failed to import numpy: {e}")
        return False
    except Exception as e:
        print(f"✗ An error occurred while importing numpy: {e}")
        return False


def setup_venv_with_numpy(launch_terminal=True, shell='powershell'):
    """
    Complete setup: launch terminal, create venv, install numpy, add to sys.path
    Args:
        launch_terminal: Whether to launch a persistent terminal
        shell: 'powershell' or 'cmd'
    Returns:
        tuple: (terminal_manager, success)
    """
    terminal_manager = None
    
    if launch_terminal:
        terminal_manager = TerminalManager(shell=shell)
        if not terminal_manager.launch_terminal():
            return None, False
    
    # Create venv
    if not create_venv(terminal_manager):
        return terminal_manager, False
    
    # Install numpy
    if not install_numpy_in_venv(terminal_manager):
        return terminal_manager, False
    
    # Add to sys.path
    if not add_venv_to_sys_path():
        return terminal_manager, False
    
    # Test import
    test_numpy_import()
    
    return terminal_manager, True




print("=" * 60)
print("Virtual Environment Setup with NumPy")
print("=" * 60)
print(f"Python Version: {get_python_version()}")
print(f"Python Executable: {get_python_executable_path()}")
print(f"Project Folder: {get_project_folder()}")
print("=" * 60)

# Launch terminal and setup venv with numpy
terminal_manager, success = setup_venv_with_numpy(launch_terminal=True, shell='powershell')

if success:
    print("\n✓ Setup completed successfully!")
    if terminal_manager:
        print(f"Terminal PID: {terminal_manager.get_pid()}")
        print("You can now execute commands on the terminal using terminal_manager.execute_command()")
else:
    print("\n✗ Setup failed. Check errors above.")

# Keep terminal open
# In actual usage, you might want to keep terminal_manager alive
# terminal_manager.close()  # Uncomment to close terminal

