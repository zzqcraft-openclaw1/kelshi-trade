from __future__ import annotations

from dataclasses import dataclass

from sklearn.metrics import accuracy_score, brier_score_loss, log_loss, roc_auc_score


@dataclass
class EvaluationResult:
    log_loss: float
    brier_score: float
    roc_auc: float
    accuracy: float


def evaluate_probabilities(y_true, y_prob, threshold: float = 0.5) -> EvaluationResult:
    y_pred = (y_prob >= threshold).astype(int)
    return EvaluationResult(
        log_loss=log_loss(y_true, y_prob),
        brier_score=brier_score_loss(y_true, y_prob),
        roc_auc=roc_auc_score(y_true, y_prob),
        accuracy=accuracy_score(y_true, y_pred),
    )
