"""CLI entry point for AgentBench."""

import argparse

from agentbench.runner import run_benchmark


def main():
    parser = argparse.ArgumentParser(description="AgentBench - AI Agent Evaluation Platform")
    parser.add_argument(
        "--models",
        type=str,
        default="openai",
        help="Comma-separated model names (e.g. openai,anthropic)",
    )
    parser.add_argument(
        "--tasks",
        type=str,
        default="benchmarks/text_generation.json",
        help="Path to the benchmark JSON file",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="results/output.json",
        help="Path for the output JSON file",
    )
    parser.add_argument(
        "--judge",
        type=str,
        default="openai/gpt-5.2",
        help="Model for the LLM judge. Can be: 1) OpenAI format model ID (e.g. openai/gpt-5.2), requires OPENROUTER_API_KEY; 2) Registered model name (e.g. doubao, wenxin), uses that model's API for evaluation",
    )

    args = parser.parse_args()

    model_names = [m.strip() for m in args.models.split(",")]
    run_benchmark(
        model_names=model_names,
        tasks_path=args.tasks,
        output_path=args.output,
        judge_model=args.judge,
    )


if __name__ == "__main__":
    main()
