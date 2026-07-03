
import sys
import os
import subprocess
import platform
import argparse
import webbrowser
import shutil
import hashlib


REQUIRED_PYTHON_MAJOR = 3
REQUIRED_PYTHON_MINOR = 13
REQUIRED_NODE_VERSION_STR = "v20.19.6"



class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_step(msg):
    print(f"{Colors.BLUE}ℹ {msg}{Colors.ENDC}")


def print_success(msg):
    print(f"{Colors.GREEN}✔ {msg}{Colors.ENDC}")


def print_error(msg):
    print(f"{Colors.FAIL}✖ {msg}{Colors.ENDC}")


def print_warning(msg):
    print(f"{Colors.WARNING}⚠ {msg}{Colors.ENDC}")


def get_base_dir():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))



def check_python(fix=False):
    current_ver = sys.version_info

    ok = (
        current_ver.major == REQUIRED_PYTHON_MAJOR
        and current_ver.minor == REQUIRED_PYTHON_MINOR
    )

    if ok:
        print_success(
            f"Python {current_ver.major}.{current_ver.minor} detected"
        )
        return True

    print_error(
        f"Python {REQUIRED_PYTHON_MAJOR}.{REQUIRED_PYTHON_MINOR} required. "
        f"Detected {current_ver.major}.{current_ver.minor}"
    )

    if not fix:
        return False

    print("\nOptions:")
    print("[1] Download Python 3.13")
    print("[2] Exit")

    choice = input("Select option [1-2]: ")

    if choice == "1":
        webbrowser.open(
            "https://www.python.org/downloads/release/python-3130/"
        )

    sys.exit(1)


def check_node(fix=False):
    try:
        result = subprocess.run(
            ["node", "-v"],
            capture_output=True,
            text=True,
            check=True
        )

        version = result.stdout.strip()

        if version == REQUIRED_NODE_VERSION_STR:
            print_success(f"Node.js {version} detected")
            return True

        print_error(
            f"Node.js {REQUIRED_NODE_VERSION_STR} required. Detected: {version}"
        )

    except Exception:
        print_error("Node.js not found")

    if not fix:
        return False

    print("\nOptions:")
    print("[1] Download required Node version")
    print("[2] Continue anyway (Risky)")
    print("[3] Exit")

    choice = input("Select option [1-3]: ")

    if choice == "1":
        webbrowser.open("https://nodejs.org/dist/v20.19.6/")
        sys.exit(0)

    if choice == "2":
        return True

    sys.exit(1)


def check_permissions(fix=False):
    if platform.system() != "Windows":
        return True

    try:
        result = subprocess.run(
            ["powershell", "-Command", "Get-ExecutionPolicy"],
            capture_output=True,
            text=True
        )

        policy = result.stdout.strip()

        if policy in ["Restricted", "AllSigned"]:
            print_warning(
                f"Execution Policy {policy} may block scripts."
            )

            if not fix:
                return False

            choice = input(
                "Set ExecutionPolicy to RemoteSigned? [y/N]: "
            )

            if choice.lower() == "y":
                subprocess.run(
                    [
                        "powershell",
                        "-Command",
                        "Set-ExecutionPolicy RemoteSigned -Scope CurrentUser"
                    ],
                    check=True
                )
                return True

            return False

        print_success(f"Execution Policy: {policy} (OK)")
        return True

    except Exception as e:
        print_warning(f"Permission check skipped: {e}")
        return True


def get_file_hash(path):
    if not os.path.exists(path):
        return None

    sha = hashlib.sha256()

    with open(path, "rb") as f:
        while True:
            data = f.read(65536)
            if not data:
                break
            sha.update(data)

    return sha.hexdigest()


def check_and_update_hash(marker, source):
    if not os.path.exists(source):
        return False, None

    current_hash = get_file_hash(source)
    old_hash = None

    if os.path.exists(marker):
        with open(marker) as f:
            old_hash = f.read().strip()

    if current_hash != old_hash:
        return True, current_hash

    return False, current_hash



def setup_backend():
    print("\n=== Backend Environment ===")

    root = get_base_dir()
    backend_dir = os.path.join(root, "Jarvis_code")
    venv_dir = os.path.join(backend_dir, "venv")

    if not os.path.exists(venv_dir):
        print_step("Creating virtual environment...")
        subprocess.run(
            [sys.executable, "-m", "venv", venv_dir],
            check=True
        )
        print_success("Virtual environment created")

    req_file = os.path.join(backend_dir, "requirements.txt")
    hash_file = os.path.join(venv_dir, ".requirements_hash")

    needs_update, new_hash = check_and_update_hash(
        hash_file,
        req_file
    )

    if needs_update:
        print_step("Updating backend dependencies...")

        try:
            # IMPORTANT FIX:
            # use python -m pip instead of pip.exe
            # avoids WinError 4551 policy blocks
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "-r",
                    "requirements.txt"
                ],
                cwd=backend_dir,
                check=True
            )

            with open(hash_file, "w") as f:
                f.write(new_hash)

            print_success("Backend dependencies installed")

        except subprocess.CalledProcessError:
            print_error("Backend dependency install failed")
            sys.exit(1)

    else:
        print_success("Backend dependencies up-to-date")



def setup_frontend():
    print("\n=== Frontend Environment ===")

    root = get_base_dir()
    frontend_dir = os.path.join(root, "agent-starter-react")
    node_modules = os.path.join(frontend_dir, "node_modules")

    if not shutil.which("pnpm"):
        print_warning("pnpm missing. Installing...")
        subprocess.run(
            "npm install -g pnpm",
            shell=True,
            check=True
        )

    pkg_file = os.path.join(frontend_dir, "package.json")
    hash_file = os.path.join(node_modules, ".package_hash")

    if not os.path.exists(node_modules):
        needs_update = True
        new_hash = get_file_hash(pkg_file)
    else:
        needs_update, new_hash = check_and_update_hash(
            hash_file,
            pkg_file
        )

    if needs_update:
        print_step("Installing frontend dependencies...")

        try:
            subprocess.run(
                "pnpm install",
                cwd=frontend_dir,
                shell=True,
                check=True
            )

            os.makedirs(node_modules, exist_ok=True)

            with open(hash_file, "w") as f:
                f.write(new_hash or "")

            print_success("Frontend ready")

        except subprocess.CalledProcessError:
            print_error("Frontend setup failed")
            sys.exit(1)

    else:
        print_success("Frontend dependencies up-to-date")



def launch():
    print("\n=== Starting JARVIS ===")

    root = get_base_dir()
    frontend_dir = os.path.join(root, "agent-starter-react")

    try:
        subprocess.run(
            "pnpm dev",
            cwd=frontend_dir,
            shell=True
        )

    except KeyboardInterrupt:
        print("Stopped.")



def main():
    parser = argparse.ArgumentParser(
        description="JARVIS CLI"
    )

    parser.add_argument(
        "command",
        choices=["start", "startr", "doctor", "help"]
    )

    if len(sys.argv) < 2:
        parser.print_help()
        return

    args = parser.parse_args()

    if args.command == "doctor":
        print("Running diagnostics...\n")

        print("Python:", "OK" if check_python(False) else "FAIL")
        print("Node:", "OK" if check_node(False) else "FAIL")
        print(
            "Permissions:",
            "OK" if check_permissions(False) else "WARN"
        )

    elif args.command in ["start", "startr"]:
        print("Initializing Bootstrap...")

        if not check_python(True):
            sys.exit(1)

        check_node(True)
        check_permissions(True)

        setup_backend()
        setup_frontend()
        launch()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
