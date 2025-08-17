import os
import subprocess
import shutil

def push_model_to_hf(local_folder, repo_id):
    token = os.getenv("HF_TOKEN")
    if not token:
        raise RuntimeError("HF_TOKEN environment variable not set.")
    cli_path = shutil.which("huggingface-cli")
    if not cli_path:
        raise RuntimeError("Hugging Face CLI 'huggingface-cli' not found in PATH. Install with: pip install -U 'huggingface_hub[cli]' and ensure your Python Scripts directory is in your PATH.")
    # Authenticate with Hugging Face CLI
    subprocess.run([cli_path, "auth", "login", "--token", token], check=True)
    # Upload model using CLI
    result = subprocess.run([cli_path, "upload", repo_id, local_folder], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        raise RuntimeError("Hugging Face CLI upload failed.")

if __name__ == "__main__":
    local_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), "model")
    repo_id = "lordlebu/4000BCSaraswaty"
    push_model_to_hf(local_folder, repo_id)