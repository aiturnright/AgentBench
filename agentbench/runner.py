"""Evaluation runner — orchestrates the full benchmark pipeline."""

import sys

from agentbench.config import get_model
from agentbench.evaluators.base import EvalResult
from agentbench.evaluators.llm_judge import LLMJudge
from agentbench.models.base import BaseModel
from agentbench.results.reporter import print_report, save_json
from agentbench.tasks.base import Task
from agentbench.tasks.loader import load_tasks


def run_benchmark(
    model_names: list[str],
    tasks_path: str,
    output_path: str = "results/output.json",
    judge_model: str = "doubao",
) -> dict[str, list[EvalResult]]:
    """Run the full evaluation pipeline.

    Args:
        model_names: List of model short names (e.g. ['doubao', 'tongyi']).
        tasks_path: Path to the benchmark JSON file.
        output_path: Where to save the JSON results.
        judge_model: Model for the LLM judge. Can be:
            - A registered model name (e.g. 'doubao', 'tongyi')

    Returns:
        Mapping of model name -> list of EvalResult.
    """
    # Load tasks
    tasks = load_tasks(tasks_path)
    print(f"Loaded {len(tasks)} tasks from {tasks_path}")

    # Initialize judge
    judge = LLMJudge(judge_model)

    # Initialize models
    models: list[BaseModel] = []
    for name in model_names:
        try:
            models.append(get_model(name))
        except ValueError as e:
            print(f"Warning: {e}", file=sys.stderr)

    if not models:
        print("Error: No valid models specified.", file=sys.stderr)
        sys.exit(1)

    # Run evaluation
    all_results: dict[str, list[EvalResult]] = {}

    for model in models:
        print(f"\n--- Evaluating: {model.name} ---")
        model_results: list[EvalResult] = []

        for task in tasks:
            print(f"  Task {task.id}: generating...", end=" ", flush=True)
            try:
                output = model.generate(task.prompt)
            except Exception as e:
                print(f"ERROR: {e}")
                model_results.append(EvalResult(task_id=task.id, score=0, comment=f"Generation failed: {e}"))
                continue

            print("judging...", end=" ", flush=True)
            try:
                result = judge.evaluate(task, output)
                result.model_output = output
            except Exception as e:
                print(f"ERROR: {e}")
                result = EvalResult(task_id=task.id, score=0, comment=f"Evaluation failed: {e}", model_output=output)

            model_results.append(result)
            print(f"score={result.score}")

        all_results[model.name] = model_results

    # Report
    print_report(all_results)
    save_json(all_results, output_path)

    return all_results
