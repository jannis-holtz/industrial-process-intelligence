import json
from pathlib import Path

import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


PROCESSED_DIR = Path("data/processed")
OUTPUT_DIR = Path("outputs/ml")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

INPUT_PATH = PROCESSED_DIR / "prediction_dataset.csv"

TARGET = "sla_breach"
ID_COL = "case_id"

RANDOM_STATE = 42
TEST_SIZE = 0.25


LEAKAGE_COLUMNS = [
    # These columns define or directly reveal the SLA label and must not be used as model inputs.
    "cycle_time_days",
    "case_cycle_time_days",
    "duration_days",
    "throughput_time_days",
    "sla_breach_actual",
    "sla_breach_probability",
    "risk_bucket",
]


def evaluate_model(name: str, model: Pipeline, X_test: pd.DataFrame, y_test: pd.Series) -> dict:
    y_pred = model.predict(X_test)

    if hasattr(model, "predict_proba"):
        y_score = model.predict_proba(X_test)[:, 1]
    else:
        y_score = y_pred

    return {
        "model": name,
        "roc_auc": float(roc_auc_score(y_test, y_score)),
        "precision": float(precision_score(y_test, y_pred, zero_division=0)),
        "recall": float(recall_score(y_test, y_pred, zero_division=0)),
        "f1": float(f1_score(y_test, y_pred, zero_division=0)),
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
        "classification_report": classification_report(
            y_test,
            y_pred,
            zero_division=0,
            output_dict=True,
        ),
    }


def build_preprocessor(X: pd.DataFrame) -> tuple[ColumnTransformer, list[str], list[str]]:
    numeric_features = X.select_dtypes(
        include=["int64", "float64", "int32", "float32", "bool"]
    ).columns.tolist()

    categorical_features = X.select_dtypes(
        include=["object", "category"]
    ).columns.tolist()

    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numeric_features),
            ("cat", categorical_transformer, categorical_features),
        ],
        remainder="drop",
    )

    return preprocessor, numeric_features, categorical_features


def export_feature_importance(best_model: Pipeline, output_path: Path) -> None:
    model_step = best_model.named_steps["model"]

    try:
        feature_names = best_model.named_steps["preprocessor"].get_feature_names_out()

        if hasattr(model_step, "feature_importances_"):
            importances = model_step.feature_importances_
        elif hasattr(model_step, "coef_"):
            importances = abs(model_step.coef_[0])
        else:
            print("Feature importance export skipped: model has no importances or coefficients.")
            return

        feature_importance = (
            pd.DataFrame(
                {
                    "feature": feature_names,
                    "importance": importances,
                }
            )
            .sort_values("importance", ascending=False)
            .reset_index(drop=True)
        )

        feature_importance.to_csv(output_path, index=False)

    except Exception as exc:
        print(f"Feature importance export skipped: {exc}")


def main() -> None:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Missing input file: {INPUT_PATH}. "
            "Run scripts/14_create_prediction_dataset.py first."
        )

    df = pd.read_csv(INPUT_PATH)

    if TARGET not in df.columns:
        raise ValueError(f"Target column missing: {TARGET}")

    if df[TARGET].nunique() < 2:
        raise ValueError(
            f"Target column {TARGET} has only one class. "
            "Model training requires both breach and non-breach cases."
        )

    drop_cols = [TARGET]

    if ID_COL in df.columns:
        drop_cols.append(ID_COL)

    leakage_cols_present = [col for col in LEAKAGE_COLUMNS if col in df.columns]
    drop_cols.extend(leakage_cols_present)

    drop_cols = sorted(set(drop_cols))

    X = df.drop(columns=drop_cols)
    y = df[TARGET].astype(int)

    if X.empty or len(X.columns) == 0:
        raise ValueError(
            "No model features available after removing ID, target and leakage columns. "
            "Add non-leaking case-level features such as event_count, unique_activity_count, "
            "has_rework, vendor category, variant_id or invoice-before-GR flag."
        )

    print("Training baseline SLA breach models")
    print(f"Input rows: {len(df):,}")
    print(f"Target breach rate: {y.mean():.2%}")
    print(f"Dropped columns: {drop_cols}")
    print(f"Feature columns: {list(X.columns)}")

    preprocessor, numeric_features, categorical_features = build_preprocessor(X)

    print(f"Numeric features: {numeric_features}")
    print(f"Categorical features: {categorical_features}")

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    models = {
        "logistic_regression": LogisticRegression(
            max_iter=1000,
            class_weight="balanced",
            random_state=RANDOM_STATE,
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=200,
            max_depth=12,
            min_samples_leaf=20,
            class_weight="balanced",
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
    }

    results = {}
    trained_models = {}

    for name, estimator in models.items():
        pipeline = Pipeline(
            steps=[
                ("preprocessor", preprocessor),
                ("model", estimator),
            ]
        )

        pipeline.fit(X_train, y_train)

        results[name] = evaluate_model(
            name=name,
            model=pipeline,
            X_test=X_test,
            y_test=y_test,
        )
        trained_models[name] = pipeline

    best_model_name = max(results, key=lambda model_name: results[model_name]["roc_auc"])
    best_model = trained_models[best_model_name]
    best_metrics = results[best_model_name]

    metrics_payload = {
        "best_model": best_model_name,
        "target": TARGET,
        "label_definition": "cycle_time_days > 120",
        "test_size": TEST_SIZE,
        "random_state": RANDOM_STATE,
        "dropped_columns": drop_cols,
        "leakage_columns_removed": leakage_cols_present,
        "feature_columns": list(X.columns),
        "numeric_features": numeric_features,
        "categorical_features": categorical_features,
        "metrics": results,
    }

    with open(OUTPUT_DIR / "model_metrics.json", "w", encoding="utf-8") as file:
        json.dump(metrics_payload, file, indent=2)

    y_score = best_model.predict_proba(X)[:, 1]

    risk_predictions = pd.DataFrame(
        {
            "case_id": df[ID_COL] if ID_COL in df.columns else range(len(df)),
            "sla_breach_actual": y,
            "sla_breach_probability": y_score,
            "risk_bucket": pd.cut(
                y_score,
                bins=[0, 0.3, 0.7, 1.0],
                labels=["Low", "Medium", "High"],
                include_lowest=True,
            ),
        }
    )

    risk_predictions.to_csv(OUTPUT_DIR / "risk_predictions.csv", index=False)

    cm = pd.DataFrame(
        best_metrics["confusion_matrix"],
        index=["Actual 0", "Actual 1"],
        columns=["Predicted 0", "Predicted 1"],
    )
    cm.to_csv(OUTPUT_DIR / "confusion_matrix.csv")

    export_feature_importance(
        best_model=best_model,
        output_path=OUTPUT_DIR / "feature_importance.csv",
    )

    print("Baseline models trained.")
    print(f"Best model: {best_model_name}")
    print(json.dumps(best_metrics, indent=2))


if __name__ == "__main__":
    main()