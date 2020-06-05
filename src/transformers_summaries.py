import logging


def load_transformer_model(model_name: str):
    model = None
    # Load library only if expressly specified: in this way it isn't mandatory to install transformers
    from transformers import pipeline
    if model_name == "bart":
        model = pipeline('summarization')
    elif model_name == "t5":
        model = pipeline(task='summarization', model="t5-small")
    return model


def generate_transformers_summary(text, summarizer):
    """
    Given a transformer pipeline (BART or T5), generate a summary whose length
    is between min_length and max_length
    :param text: text to summarise
    :param summarizer: transformers pipeline to use for summarising text
    :return:
    """
    logging.info("generate_transformers_summary >>>")
    # Transform the text back into string
    text = "".join(text)
    # Compute the minimum and maximum length of a summary
    summary = summarizer(text, max_length=300, early_stopping=True, num_beams=1)
    summary = summary[0]['summary_text']
    logging.info("generate_transformers_summary <<<")
    return summary