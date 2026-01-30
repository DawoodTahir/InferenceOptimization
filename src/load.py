from unsloth import FastLanguageModel
import torch
def load():
    max_seq_length = 2048
    dtype = None
    load_in_4bit = True

    model , tokenizer = FastLanguageModel.from_pretrained(
        model_name = "unsloth/llama-3-8b-bnb-4bit",
        max_seq_length = max_seq_length,
        dtype = dtype,
        load_in_4bit = load_in_4bit
    )

    model = FastLanguageModel.get_peft_model(
        model,
        r=16,
        lora_alpha=32,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                        "gate_proj", "up_proj", "down_proj"],
        lora_dropout=0,
        use_gradient_checkpointing = "unsloth",
        random_state = 3407,
    )

    return model, tokenizer
