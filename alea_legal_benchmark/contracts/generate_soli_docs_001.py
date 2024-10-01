"""
Document example generation using SOLI taxonomic elements (soli_clauses_001).

Description: This script uses the SOLI knowledge graph and Llama 3.1 405B to generate
labeled synthetic document examples as follows:

1. Randomly sample a date between 1975 and 2025.
2. Randomly sample an area of law from the SOLI knowledge graph.
3. Randomly sample a location from the SOLI knowledge graph.
4. Randomly sample an industry from the SOLI knowledge graph.
5. Randomly sample a document type from the SOLI knowledge graph (https://soli.openlegalstandard.org/RBkL8I5saFF7mqpLTI7GxSh/html)
6. Generate a prompt with the sampled guidance and instructions.
7. Randomly sample a temperature between 0.1 and 0.8.
8. Use the Llama 3.1 405B model to generate a clause example.
9. Write the clause example to a JSONL file (`samples/contracts/soli_clauses_001/sample_<timestamp>.jsonl`).
"""

# imports
import datetime
import json
from pathlib import Path

# packages
import numpy.random
import tqdm
from alea_llm_client.llms.prompts.sections import format_instructions, format_prompt
from alea_llm_client import OpenAIModel

# project
from alea_legal_benchmark.utils.soli import (
    sample_date,
    sample_area_of_law,
    sample_location,
    sample_industry,
    sample_doc_type,
)


def sample_guidance() -> dict:
    """
    Sample guidance for generating synthetic contract documents based on Strategy 1.

    Returns:
        dict: A dictionary containing the guidance for generating synthetic contract documents.
    """

    return {
        "date": sample_date(),
        "area_of_law": sample_area_of_law(),
        "location": sample_location(),
        "industry": sample_industry(),
        "document_type": sample_doc_type(),
    }


def generate_samples(
    model_name: str = "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
    num_samples: int = 1000,
):
    """
    Generate synthetic contract documents based on Strategy 1.

    Args:
        model_name (str): The name of the model to use.
        num_samples (int): The number of samples to generate.

    Returns:
        None
    """

    # set up a together.ai endpoint
    TOGETHER_API_KEY = (Path.home() / ".alea" / "keys" / "together").read_text().strip()
    m = OpenAIModel(
        endpoint="https://api.together.xyz", model=model_name, api_key=TOGETHER_API_KEY
    )

    # get the output file path and ensure it exists
    output_file_path = (
        Path(__file__).parent.parent.parent / "samples" / "contracts" / "soli_docs_001"
    )
    output_file_path.mkdir(parents=True, exist_ok=True)
    output_file_name = (
        f"sample_{datetime.datetime.now().isoformat().replace(":", "")}.jsonl"
    )

    # open file and output
    with open(output_file_path / output_file_name, "at+") as output_file:
        prog_bar = tqdm.tqdm(range(num_samples))
        success_count = 0
        fail_count = 0
        for _ in prog_bar:
            try:
                guidance = sample_guidance()
                prompt = format_prompt(
                    {
                        "guidance": guidance,
                        "instructions": format_instructions(
                            [
                                "You are drafting a document.",
                                "Draw inspiration from the date, area_of_law, location, and industry provided.",
                                "Carefully adhere to the document_type provided.",
                                "Provide realistic or random information where needed.  Do not use blanks or placeholders like [Party] or _____.",
                                "Respond in JSON with the escaped Markdown document.",
                            ]
                        ),
                        "schema": """{"document": string}""",
                    }
                )

                # merge and output
                temperature = numpy.random.uniform(0.1, 0.8)
                response = m.chat(
                    prompt,
                    max_tokens=16384,
                    stop=["<|eot_id|>", "<|eom_id|>"],
                    temperature=temperature,
                )
                response_data = m.parse_json(response.text)

                if "document" not in response_data:
                    raise Exception("No document in response.")

                response_data.update(guidance)
                output_file.write(json.dumps(response_data) + "\n")
                output_file.flush()

                # update prog bar with success count
                success_count += 1
            except Exception as e:
                print(e)
                fail_count += 1
            finally:
                prog_bar.set_postfix(success_count=success_count, fail_count=fail_count)


if __name__ == "__main__":
    generate_samples()
