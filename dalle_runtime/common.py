import os
from pydantic import BaseSettings
from mlserver.logging import logger
from dalle_runtime.min_dalle.min_dalle_flax import generate_image_tokens_flax
from dalle_runtime.min_dalle.min_dalle_torch import detokenize_torch
from dalle_runtime.min_dalle.load_params import load_dalle_bart_flax_params
from dalle_runtime.min_dalle.min_dalle_flax import generate_image_tokens_flax
from dalle_runtime.min_dalle.generate_image import (
    load_dalle_bart_metadata,
    tokenize_text
)
import torch

DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "min_dalle")


HUGGINGFACE_TASK_TAG = "task"

ENV_PREFIX_DALLERUNTIME_SETTINGS = "MLSERVER_MODEL_DALLERUNTIME_"
HUGGINGFACE_PARAMETERS_TAG = "huggingface_parameters"
PARAMETERS_ENV_NAME = "PREDICTIVE_UNIT_PARAMETERS"


class DalleRuntimeSettings(BaseSettings):
    """
    Parameters that apply only to alibi huggingface models
    """

    class Config:
        env_prefix = ENV_PREFIX_DALLERUNTIME_SETTINGS

    lambda_value: str = ""


def dalle_text_to_image(text: str, seed: int):
    model_path = f'{DIR}/pretrained/dalle_bart_mini'

    logger.info(f"Loading bert metadata from {model_path}")
    config, vocab, merges = load_dalle_bart_metadata(model_path)

    logger.info(f"tokenizing text {text}")
    text_tokens = tokenize_text(text, config, vocab, merges)

    logger.info(f"Loading bert params from {model_path}")
    params_dalle_bart = load_dalle_bart_flax_params(model_path)

    logger.info("Generating images")
    image_tokens = generate_image_tokens_flax(
        text_tokens = text_tokens,
        seed = seed,
        config = config,
        params = params_dalle_bart,
    )

    logger.info("Detokenizing")
    model_output = detokenize_torch(torch.tensor(image_tokens), is_torch=False)

    return model_output

