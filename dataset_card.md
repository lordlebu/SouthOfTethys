@dataset{lordlebu_southoftethys_2025,
  title={SouthOfTethys: A Procedural Fantasy World Dataset},
  author={lordlebu},
  year={2025},
  url={https://huggingface.co/datasets/lordlebu/SouthOfTethys}
}

## Related Models

- [4000BCSaraswaty](https://huggingface.co/lordlebu/4000BCSaraswaty): A Hugging Face model trained on SouthOfTethys data.

import os
from huggingface_hub import HfApi

api = HfApi(token=os.getenv("HF_TOKEN"))
api.upload_folder(
    folder_path="C:/Users/lordl/OneDrive/Documents/GitHub/SouthOfTethys/model",  # update this path
    repo_id="lordlebu/4000BCSaraswaty",
    repo_type="model",
)