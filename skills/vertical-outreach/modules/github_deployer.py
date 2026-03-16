"""GitHub Pages deployment module."""
import os
import subprocess
from pathlib import Path


class GitHubPagesDeployer:
    def __init__(self, token: str, repo_name: str, calculator_path: Path):
        self.token = token
        self.repo_name = repo_name
        self.calculator_path = calculator_path
        self.username = "justicewastaken"  # Will detect from git config if needed

    def deploy(self) -> str:
        """Deploy calculator to GitHub Pages and return public URL."""
        print("  Deploying calculator to GitHub Pages...")

        # Create a temporary git repo
        temp_dir = self.calculator_path.parent / f".tmp_{self.repo_name}"
        temp_dir.mkdir(exist_ok=True)

        try:
            # Copy calculator file
            import shutil
            shutil.copy(self.calculator_path, temp_dir / "index.html")

            # Initialize git
            os.chdir(temp_dir)
            subprocess.run(["git", "init"], check=True, capture_output=True)
            subprocess.run(["git", "config", "user.email", "automation@openclaw.ai"], check=True, capture_output=True)
            subprocess.run(["git", "config", "user.name", "OpenClaw Automation"], check=True, capture_output=True)

            # Add remote with token auth
            remote_url = f"https://{self.token}@github.com/{self.username}/{self.repo_name}.git"
            subprocess.run(["git", "remote", "add", "origin", remote_url], check=True, capture_output=True)

            # Add, commit, push
            subprocess.run(["git", "add", "."], check=True, capture_output=True)
            subprocess.run(["git", "commit", "-m", "Deploy calculator"], check=True, capture_output=True)
            subprocess.run(["git", "push", "-u", "origin", "master"], check=True, capture_output=True)

            # Enable Pages (requires API call)
            pages_url = f"https://api.github.com/repos/{self.username}/{self.repo_name}/pages"
            import requests
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github.v3+json"
            }
            data = {"source": {"branch": "master", "path": "/"}}
            response = requests.post(pages_url, headers=headers, json=data, timeout=30)

            if response.status_code in [201, 204]:
                return f"https://{self.username}.github.io/{self.repo_name}/"
            else:
                print(f"  ⚠️  Pages enable failed: {response.status_code}")
                return f"https://{self.username}.github.io/{self.repo_name}/ (may need manual enable)"

        except subprocess.CalledProcessError as e:
            print(f"  ❌ Git error: {e}")
            return "deployment_failed"
        except Exception as e:
            print(f"  ❌ Deployment error: {e}")
            return "deployment_failed"
        finally:
            # Cleanup
            os.chdir("/root/.openclaw/workspace")
            import shutil
            if temp_dir.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)
