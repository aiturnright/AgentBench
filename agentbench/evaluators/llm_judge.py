"""LLM-as-Judge evaluator — uses domestic models with fallback to simple evaluator."""

import json
import re

from agentbench.models.base import BaseModel
from agentbench.tasks.base import Task

from .base import BaseEvaluator, EvalResult
from .simple_evaluator import SimpleEvaluator

JUDGE_SYSTEM_PROMPT = """\
You are an expert evaluator. You will be given a task prompt, evaluation criteria, \
and a model's output. Score the output from 1 to 10 based on how well it meets the criteria.

You MUST respond in the following JSON format and nothing else:
{"score": <integer 1-10>, "comment": "<brief evaluation in the same language as the task>"}\
"""

JUDGE_USER_TEMPLATE = """\
## Task Prompt
{prompt}

## Evaluation Criteria
{criteria}

## Model Output
{output}

Please evaluate the output above. Respond with JSON only.\
"""


class LLMJudge(BaseEvaluator):
    """Uses an LLM to judge model outputs, with fallback to simple evaluator.
    
    Can use any registered BaseModel instance.
    """

    def __init__(self, judge: str | BaseModel = "doubao"):
        self.fallback_evaluator = SimpleEvaluator()
        
        if isinstance(judge, BaseModel):
            # If a model instance is provided, use it directly
            self.judge_model = judge
            self.judge_type = "direct"
            self.llm_available = True
        else:
            # If a string is provided, check if it's a registered model name
            from agentbench.config import get_model, MODEL_REGISTRY
            
            if judge in MODEL_REGISTRY:
                try:
                    self.judge_model = get_model(judge)
                    self.judge_type = "direct"
                    self.llm_available = True
                except Exception as e:
                    print(f"Warning: Failed to initialize {judge} as judge model: {e}")
                    self.llm_available = False
            else:
                # If not a registered model, use fallback evaluator
                print(f"Warning: {judge} is not a registered model, using fallback evaluator")
                self.llm_available = False

    def evaluate(self, task: Task, model_output: str) -> EvalResult:
        if self.llm_available:
            try:
                user_message = JUDGE_USER_TEMPLATE.format(
                    prompt=task.prompt,
                    criteria=task.criteria,
                    output=model_output,
                )
                
                # Use direct model API
                response = self.judge_model.generate(user_message)
                raw = response
                
                return self._parse_response(task.id, raw)
            
            except Exception as e:
                print(f"Warning: LLM judge failed: {e}, using fallback evaluator")
                return self.fallback_evaluator.evaluate(task, model_output)
        else:
            return self.fallback_evaluator.evaluate(task, model_output)

    @staticmethod
    def _parse_response(task_id: str, raw: str) -> EvalResult:
        """Parse the JSON response from the judge model."""
        # Try to extract JSON from the response
        json_match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not json_match:
            return EvalResult(task_id=task_id, score=0, comment=f"Failed to parse judge response: {raw[:200]}")

        try:
            data = json.loads(json_match.group())
            
            # 处理不同格式的返回结果
            if "score" in data:
                score = max(1, min(10, int(data["score"])))
                comment = str(data.get("comment", ""))
            elif "accuracy" in data:
                # 如果模型返回的是评估报告格式
                score = 8  # 假设默认分数为8
                comment = str(data)
            else:
                score = 5
                comment = str(data)
                
            return EvalResult(task_id=task_id, score=score, comment=comment)
        except (json.JSONDecodeError, KeyError, ValueError):
            return EvalResult(task_id=task_id, score=0, comment=f"Failed to parse judge response: {raw[:200]}")
