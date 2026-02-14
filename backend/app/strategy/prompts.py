STRATEGY_GENERATION_PROMPT = """
[INST] Role: Algo Trading Strategy Developer (Python/Backtrader)

Task: Convert the user's natural language trading idea into a valid Python class inheriting from `backtrader.Strategy`.

Context:
- The user will provide a description like "Buy when RSI < 30".
- You must output ONLY the Python code for the strategy class.
- The class name should be descriptive (e.g., `RsiMeanReversion`).
- Assume standard imports (`backtrader as bt`, `datetime`) are available.

Constraints:
- Do NOT include any explanation or markdown formatting (```python). Just the code.
- Ensure `__init__` defines indicators.
- Ensure `next` contains the logic.
- Include a docstring summarizing the logic.

User Idea:
{user_prompt}
[/INST]
"""

STRATEGY_MUTATION_PROMPT = """
[INST] Role: Evolutionary Algo Optimizer

Task: Mutate the provided trading strategy code to improve its robustness or risk profile.

Input Code:
{current_code}

Mutation Instruction:
{mutation_instruction}

Constraint:
- Output ONLY the modified Python code.
- Maintain the class structure.
[/INST]
"""
