import os

from huggingface_hub import HfApi


def push_model_to_hf(local_folder, repo_id):
    token = os.getenv("HF_TOKEN")
    if not token:
        raise RuntimeError("HF_TOKEN environment variable not set.")
    api = HfApi(token=token)
    try:
        # Upload config and checkpoints folders
        api.upload_folder(
            folder_path=os.path.join(local_folder, "config"),
            repo_id=repo_id,
            repo_type="model",
        )
        api.upload_folder(
            folder_path=os.path.join(local_folder, "checkpoints"),
            repo_id=repo_id,
            repo_type="model",
        )
        print(f"Successfully pushed config and checkpoints to {repo_id}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    local_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), "model")
    repo_id = "lordlebu/4000BCSaraswaty"
    push_model_to_hf(local_folder, repo_id)
