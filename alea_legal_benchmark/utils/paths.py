"""
Path utilities for the benchmark and samples.
"""

from functools import cache

# imports
from pathlib import Path


@cache
def get_project_root_path() -> Path:
    """
    Get the project root.

    Returns:
        Path
    """
    return Path(__file__).parent.parent.parent


@cache
def get_samples_root_path() -> Path:
    """
    Get the samples root.

    Returns:
        Path
    """
    return get_project_root_path() / "samples"


def get_experiments() -> list[str]:
    """
    Get the experiments.

    Returns:
        list[str]
    """
    return [path.name for path in get_samples_root_path().iterdir() if path.is_dir()]


def get_experiment_files(experiment_id: str) -> list[Path]:
    """
    Get the experiment files from a sample path.

    Args:
        experiment_id (str): The experiment ID.

    Returns:
        Path
    """
    return list((get_samples_root_path() / experiment_id).glob("*.jsonl"))


if __name__ == "__main__":
    print(get_project_root_path())
    print(get_samples_root_path())
    print(get_experiments())
    print(get_experiment_files("contracts/soli_clauses_001"))
