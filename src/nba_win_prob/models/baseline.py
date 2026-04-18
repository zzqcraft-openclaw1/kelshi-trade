from sklearn.calibration import CalibratedClassifierCV
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler


def build_model() -> Pipeline:
    base = LogisticRegression(max_iter=2000)
    calibrated = CalibratedClassifierCV(base, method="sigmoid", cv=3)
    return Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            ("model", calibrated),
        ]
    )
