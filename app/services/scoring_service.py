from typing import Any, Dict, Optional
import numpy as np

from app.config.scoring_config import VARIABLE_CONFIG


def clip_score(score: float) -> float:
    return max(0.0, min(1.0, score))


def compute_hybrid_min_max(
    historical_data: Dict[str, list],
    lower_percentile: float = 5,
    upper_percentile: float = 95,
) -> Dict[str, Dict[str, float]]:
    min_max_table = {}

    for variable, values in historical_data.items():
        clean_values = [
            v for v in values
            if isinstance(v, (int, float)) and v is not None
        ]

        if len(clean_values) < 2:
            continue

        min_val = np.percentile(clean_values, lower_percentile)
        max_val = np.percentile(clean_values, upper_percentile)

        if min_val == max_val:
            continue

        min_max_table[variable] = {
            "min": float(min_val),
            "max": float(max_val),
        }

    return min_max_table


def normalize_increase(
    value: Optional[float],
    min_val: float,
    max_val: float,
) -> Optional[float]:
    if value is None or max_val == min_val:
        return None

    score = (value - min_val) / (max_val - min_val)
    return clip_score(score)


def normalize_decrease(
    value: Optional[float],
    min_val: float,
    max_val: float,
) -> Optional[float]:
    if value is None or max_val == min_val:
        return None

    score = (max_val - value) / (max_val - min_val)
    return clip_score(score)


def normalize_categorical(
    value: Optional[str],
    scores: Dict[str, float],
    default_score: float = 0.5,
) -> float:
    if value is None:
        return default_score

    value_clean = str(value).strip().upper()

    normalized_scores = {
        str(k).strip().upper(): v
        for k, v in scores.items()
    }

    return normalized_scores.get(value_clean, default_score)


def compute_user_weights(user_ranks: Dict[str, int]) -> Dict[str, float]:
    valid_ranks = {
        variable: rank
        for variable, rank in user_ranks.items()
        if isinstance(rank, int) and 1 <= rank <= 5
    }

    total_rank = sum(valid_ranks.values())

    if total_rank == 0:
        return {}

    return {
        variable: rank / total_rank
        for variable, rank in valid_ranks.items()
    }


def special_score(variable: str, value: Any) -> Optional[float]:
    if value is None:
        return None

    if variable == "numBedrooms":
        if value <= 1:
            return 0.3
        elif value == 2:
            return 0.7
        elif value == 3:
            return 1.0
        elif value == 4:
            return 0.9
        else:
            return 0.7

    if variable == "numBathrooms":
        if value <= 1:
            return 0.4
        elif value == 2:
            return 0.8
        elif value == 3:
            return 1.0
        else:
            return 0.9

    if variable == "numFloors":
        if value == 1:
            return 0.8
        elif value == 2:
            return 1.0
        elif value == 3:
            return 0.7
        else:
            return 0.5

    if variable == "medianHomeValue":
        if value < 150000:
            return 0.4
        elif value <= 400000:
            return 1.0
        elif value <= 700000:
            return 0.7
        else:
            return 0.5

    return 0.5


def score_variable(
    variable: str,
    value: Any,
    min_max_table: Dict[str, Dict[str, float]],
) -> Optional[float]:
    config = VARIABLE_CONFIG.get(variable)

    if config is None:
        return None

    rule_type = config.get("type")

    if rule_type == "increase":
        bounds = min_max_table.get(variable)
        if bounds is None:
            return None

        return normalize_increase(
            value=value,
            min_val=bounds["min"],
            max_val=bounds["max"],
        )

    if rule_type == "decrease":
        bounds = min_max_table.get(variable)
        if bounds is None:
            return None

        return normalize_decrease(
            value=value,
            min_val=bounds["min"],
            max_val=bounds["max"],
        )

    if rule_type == "categorical":
        return normalize_categorical(
            value=value,
            scores=config.get("scores", {}),
            default_score=config.get("default", 0.5),
        )

    if rule_type == "special":
        return special_score(variable, value)

    return None


def get_score_label(score: float) -> str:
    if score >= 80:
        return "Strong Potential"
    elif score >= 65:
        return "Good Potential"
    elif score >= 50:
        return "Moderate Potential"
    else:
        return "Low Potential"


def compute_investment_score(
    enriched_data: Dict[str, Dict[str, Any]],
    user_ranks: Dict[str, int],
    min_max_table: Dict[str, Dict[str, float]],
) -> Dict[str, Any]:
    weights = compute_user_weights(user_ranks)

    variable_scores = {}
    weighted_scores = {}

    final_score = 0.0
    total_used_weight = 0.0

    for variable, weight in weights.items():
        config = VARIABLE_CONFIG.get(variable)

        if config is None:
            continue

        category = config.get("category")
        value = enriched_data.get(category, {}).get(variable)

        score = score_variable(
            variable=variable,
            value=value,
            min_max_table=min_max_table,
        )

        if score is None:
            continue

        variable_scores[variable] = round(score, 4)
        weighted_scores[variable] = round(score * weight, 4)

        final_score += score * weight
        total_used_weight += weight

    if total_used_weight > 0:
        final_score = final_score / total_used_weight
    else:
        final_score = 0.0

    investment_score = round(final_score * 100, 2)

    return {
        "investmentScore": investment_score,
        "scoreLabel": get_score_label(investment_score),
        "variableScores": variable_scores,
        "weights": weights,
        "weightedScores": weighted_scores,
    }
