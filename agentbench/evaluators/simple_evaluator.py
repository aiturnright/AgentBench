"""Simple default evaluator — provides a fallback when LLM judge is not available."""

from agentbench.tasks.base import Task
from .base import BaseEvaluator, EvalResult


class SimpleEvaluator(BaseEvaluator):
    """A simple evaluator that provides a fallback when LLM judge is not available."""

    def evaluate(self, task: Task, model_output: str) -> EvalResult:
        """
        Provides a simple evaluation based on the length of the output.

        Args:
            task: The task to evaluate.
            model_output: The output from the model.

        Returns:
            An EvalResult with a score based on output length and a simple comment.
        """
        # Score based on output length (simple heuristic)
        length = len(model_output.strip())
        
        if length == 0:
            score = 0
            comment = "Empty output"
        elif length < 50:
            score = 2
            comment = "Output is too short"
        elif length < 150:
            score = 4
            comment = "Output is somewhat short"
        elif length < 300:
            score = 6
            comment = "Output length is reasonable"
        elif length < 600:
            score = 8
            comment = "Output is detailed"
        else:
            score = 10
            comment = "Output is very detailed"
        
        return EvalResult(task_id=task.id, score=score, comment=comment)
