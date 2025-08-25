import os

from huggingface_hub import HfApi


def push_model_to_hf(local_folder, repo_id):
    token = os.getenv("HF_TOKEN")
    if not token:
        raise RuntimeError("HF_TOKEN environment variable not set.")
    api = HfApi(token=token)
    try:
        # Upload the entire model folder (should contain all required files)
        api.upload_folder(
            folder_path=local_folder,
            repo_id=repo_id,
            repo_type="model",
        )
        print(f"Successfully pushed model folder to {repo_id}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    # Step 1: Export a valid model and tokenizer to the model/ directory
    from transformers import AutoModelForCausalLM, AutoTokenizer
    model_name = "gpt2"  # Replace with your fine-tuned model if you have one
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "model")
    tokenizer.save_pretrained(output_dir)
    model.save_pretrained(output_dir)

    # Step 2: Push the model folder to Hugging Face Hub
    repo_id = "lordlebu/4000BCSaraswaty"
    push_model_to_hf(output_dir, repo_id)
