from langscrape.utils import coerce_model_content_to_str


def test_coerce_model_content_to_str_with_reasoner_blocks():
    content = [
        {"type": "reasoning", "text": "Step 1. "},
        {"type": "reasoning", "text": ["Step 2. ", {"text": "Nested."}]},
        {"type": "answer", "text": "Final answer"},
    ]

    assert coerce_model_content_to_str(content) == "Step 1. Step 2. Nested.Final answer"


def test_coerce_model_content_to_str_dict_with_content_key():
    content = {"content": ["Alpha", {"text": "Beta"}]}

    assert coerce_model_content_to_str(content) == "AlphaBeta"
