import os
import json
import numpy
from PIL import Image
from typing import Tuple, List
import torch

from .load_params import load_dalle_bart_flax_params
from .text_tokenizer import TextTokenizer
from .min_dalle_flax import generate_image_tokens_flax
from .min_dalle_torch import (
    generate_image_tokens_torch,
    detokenize_torch
)

DIR = os.path.dirname(os.path.abspath(__file__))

def load_dalle_bart_metadata(path: str) -> Tuple[dict, dict, List[str]]:
    print("parsing metadata from {}".format(path))
    for f in ['config.json', 'flax_model.msgpack', 'vocab.json', 'merges.txt']:
        assert(os.path.exists(os.path.join(path, f)))
    with open(path + '/config.json', 'r') as f: 
        config = json.load(f)
    with open(path + '/vocab.json') as f:
        vocab = json.load(f)
    with open(path + '/merges.txt') as f:
        merges = f.read().split("\n")[1:-1]
    return config, vocab, merges


def tokenize_text(
    text: str, 
    config: dict,
    vocab: dict,
    merges: List[str]
) -> numpy.ndarray:
    print("tokenizing text")
    tokens = TextTokenizer(vocab, merges)(text)
    print("text tokens", tokens)
    text_tokens = numpy.ones((2, config['max_text_length']), dtype=numpy.int32)
    text_tokens[0, :len(tokens)] = tokens
    text_tokens[1, :2] = [tokens[0], tokens[-1]]
    return text_tokens


def generate_image_from_text(
    text: str,
    is_mega: bool = False,
    is_torch: bool = False,
    seed: int = 0,
    image_token_count: int = 256
) -> Image.Image:
    model_name = 'mega' if is_mega else 'mini'
    model_path = f'{DIR}/pretrained/dalle_bart_{model_name}'
    config, vocab, merges = load_dalle_bart_metadata(model_path)
    text_tokens = tokenize_text(text, config, vocab, merges)
    params_dalle_bart = load_dalle_bart_flax_params(model_path)

    if is_torch:
        image_tokens = generate_image_tokens_torch(
            text_tokens = text_tokens,
            seed = seed,
            config = config,
            params = params_dalle_bart,
            image_token_count = image_token_count
        )
        if image_token_count == config['image_length']:
            image = detokenize_torch(image_tokens, is_torch=True)
            return Image.fromarray(image)
        else:
            print(list(image_tokens.to('cpu').detach().numpy()))
    else:
        image_tokens = generate_image_tokens_flax(
            text_tokens = text_tokens, 
            seed = seed,
            config = config,
            params = params_dalle_bart,
        )
        image = detokenize_torch(torch.tensor(image_tokens), is_torch=False)
        return Image.fromarray(image)
