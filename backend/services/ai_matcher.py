# Let the LLM pick which USDA candidate (if any) is truly the user's food.

from typing import List, Optional, Tuple

from config import OPENAI_MODEL
from models.schemas import FoodMatchSelection
from services.llm import client

SYSTEM_PROMPT = """\
You are matching a user's food description to an entry in a nutrition \
database. You will be given the food the user mentioned and a list of \
candidate database entries, each identified by its fdcId.

Select the candidate that is genuinely the same food as what the user \
described. Differences in cooking method (raw vs cooked), cut, or minor \
descriptive detail are acceptable to match. A different food entirely - \
for example a sausage/processed product when the user meant a plain cut \
of meat, or an unrelated ingredient that just has a similar name - must \
NOT be selected.

If none of the candidates are genuinely the same food, return null for \
selected_fdc_id.
"""


def select_best_match(query: str, candidates: List[Tuple[float, dict]], verbose: bool = False) -> Optional[Tuple[float, dict]]:
    if not candidates:
        return None

    listed_candidates = "\n".join(f"{food['fdcId']}: {food.get('description', '')}" for _, food in candidates)

    completion = client.beta.chat.completions.parse(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f'User\'s food: "{query}"\n\nCandidates:\n{listed_candidates}'},
        ],
        response_format=FoodMatchSelection,
    )

    result = completion.choices[0].message.parsed

    if result is None or result.selected_fdc_id is None:
        if verbose:
            reason = result.reasoning if result else "no response"
            print(f"    -> LLM found no confident match: {reason}")
        return None

    for score, food in candidates:
        if food["fdcId"] == result.selected_fdc_id:
            if verbose:
                print(f"    -> LLM selected fdc_id={result.selected_fdc_id}: {result.reasoning}")
            return score, food

    # LLM returned an id we didn't offer it
    if verbose:
        print(f"    -> LLM returned unknown fdc_id {result.selected_fdc_id}, ignoring")
    return None