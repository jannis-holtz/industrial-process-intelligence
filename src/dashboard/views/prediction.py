import pandas as pd
import streamlit as st

from src.dashboard.components import module_container


def render_prediction_placeholder() -> None:
    st.warning(
        "Prediction & Risk Monitoring is available, but the app is still calling the old placeholder."
    )


def _format_model_name(model_name: str | None) -> str:
    if not model_name:
        return "N/A"

    return str(model_name).replace("_", " ").title()


def _get_bucket_count(risk_predictions: pd.DataFrame, bucket: str) -> int:
    if "risk_bucket" not in risk_predictions.columns:
        return 0

    return int((risk_predictions["risk_bucket"] == bucket).sum())


def _clean_feature_name(feature: str) -> str:
    return (
        str(feature)
        .replace("num__", "")
        .replace("cat__", "")
        .replace("_", " ")
        .title()
    )


def _render_missing_outputs() -> None:
    st.markdown("## ⚠️ Prediction & Risk Monitoring")

    with module_container(
        title="Prediction Outputs Missing",
        subtitle="The dashboard view is ready, but model outputs are not available yet.",
        eyebrow="Pipeline Status",
    ):
        st.warning("Prediction outputs are not available yet.")

        st.markdown("Run the prediction pipeline first:")

        st.code(
            """
python scripts/14_create_prediction_dataset.py
python scripts/15_train_baseline_model.py
            """.strip(),
            language="bash",
        )


def render_prediction_risk_view(
    prediction_metrics: dict | None,
    risk_predictions: pd.DataFrame,
    feature_importance: pd.DataFrame,
    confusion_matrix: pd.DataFrame,
) -> None:
    st.markdown("## ⚠️ Prediction & Risk Monitoring")

    if prediction_metrics is None or risk_predictions.empty:
        _render_missing_outputs()
        return

    best_model = prediction_metrics.get("best_model")
    metrics_by_model = prediction_metrics.get("metrics", {})

    if best_model not in metrics_by_model:
        st.error("Invalid prediction metrics structure.")
        st.json(prediction_metrics)
        return

    best_metrics = metrics_by_model[best_model]

    roc_auc = float(best_metrics.get("roc_auc", 0))
    precision = float(best_metrics.get("precision", 0))
    recall = float(best_metrics.get("recall", 0))
    f1 = float(best_metrics.get("f1", 0))

    total_cases = len(risk_predictions)
    low_risk_cases = _get_bucket_count(risk_predictions, "Low")
    medium_risk_cases = _get_bucket_count(risk_predictions, "Medium")
    high_risk_cases = _get_bucket_count(risk_predictions, "High")

    low_share = low_risk_cases / total_cases if total_cases else 0
    medium_share = medium_risk_cases / total_cases if total_cases else 0
    high_share = high_risk_cases / total_cases if total_cases else 0

    # ==========================================================
    # 1. MANAGEMENT TAKEAWAY
    # ==========================================================
    with module_container(
        title="Management Takeaway",
        subtitle="Business interpretation of the SLA breach risk layer.",
        eyebrow="Executive Summary",
    ):
        st.markdown(
            f"""
            The baseline model identifies **{high_risk_cases:,} high-risk cases**
            (**{high_share:.2%}** of all cases) with elevated probability of breaching the
            120-day SLA threshold.

            The current model is useful as a **risk-prioritization layer**, not as a fully automated
            decision engine. With a ROC-AUC of **{roc_auc:.3f}**, it provides a moderate but usable
            signal for operational triage.
            """
        )

        st.info(
            "Recommended action: review high-risk cases first and combine the signal with bottleneck, rework and root-cause analysis."
        )

    # ==========================================================
    # 2. KPI STRIP
    # ==========================================================
    with module_container(
        title="Risk KPIs",
        subtitle="Compact view of model performance and operational risk exposure.",
        eyebrow="Risk Overview",
    ):
        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Best Model", _format_model_name(best_model))
        col2.metric("ROC-AUC", f"{roc_auc:.3f}")
        col3.metric("High-Risk Cases", f"{high_risk_cases:,}")
        col4.metric("High-Risk Share", f"{high_share:.2%}")

        col5, col6, col7 = st.columns(3)

        col5.metric("Precision", f"{precision:.3f}")
        col6.metric("Recall", f"{recall:.3f}")
        col7.metric("F1 Score", f"{f1:.3f}")

        st.caption(
            "Interpretation: recall is more important than precision here, because missing risky cases is more costly than reviewing some false positives."
        )

    # ==========================================================
    # 3. RISK BUCKETS WITHOUT NOISY CHART
    # ==========================================================
    with module_container(
        title="Risk Buckets",
        subtitle="How the case population is segmented by predicted SLA breach risk.",
        eyebrow="Risk Monitoring",
    ):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Low Risk", f"{low_risk_cases:,}", f"{low_share:.2%}")
            st.progress(min(low_share, 1.0))

        with col2:
            st.metric("Medium Risk", f"{medium_risk_cases:,}", f"{medium_share:.2%}")
            st.progress(min(medium_share, 1.0))

        with col3:
            st.metric("High Risk", f"{high_risk_cases:,}", f"{high_share:.2%}")
            st.progress(min(high_share, 1.0))

    # ==========================================================
    # 4. TOP RISK DRIVERS
    # ==========================================================
    with module_container(
        title="Top Risk Drivers",
        subtitle="Main factors behind predicted SLA breach risk.",
        eyebrow="Model Interpretation",
    ):
        if not feature_importance.empty and {"feature", "importance"}.issubset(
            feature_importance.columns
        ):
            top_features = feature_importance.head(5).copy()
            top_features["Risk Driver"] = top_features["feature"].map(_clean_feature_name)
            top_features["Importance"] = top_features["importance"].round(4)

            display_features = top_features[["Risk Driver", "Importance"]]

            st.dataframe(
                display_features,
                use_container_width=True,
                hide_index=True,
            )

            top_driver = display_features.iloc[0]["Risk Driver"]

            st.success(
                f"Main signal: **{top_driver}** is currently the strongest driver of predicted SLA breach risk."
            )

            st.caption(
                "Business interpretation: risk is mainly driven by case complexity and rework-related patterns."
            )
        else:
            st.info("Feature importance output is not available.")

    # ==========================================================
    # 5. TOP HIGH-RISK CASES
    # ==========================================================
    with module_container(
        title="Highest-Risk Cases",
        subtitle="Focused list of cases for operational follow-up.",
        eyebrow="Operational Prioritization",
    ):
        probability_column = "sla_breach_probability"

        if probability_column in risk_predictions.columns:
            display_columns = [
                column
                for column in [
                    "case_id",
                    "sla_breach_probability",
                    "risk_bucket",
                    "sla_breach_actual",
                ]
                if column in risk_predictions.columns
            ]

            top_risk_cases = (
                risk_predictions.sort_values(probability_column, ascending=False)
                .head(10)
                .copy()
            )

            top_risk_cases["sla_breach_probability"] = top_risk_cases[
                "sla_breach_probability"
            ].map(lambda value: f"{value:.2%}")

            top_risk_cases = top_risk_cases.rename(
                columns={
                    "case_id": "Case ID",
                    "sla_breach_probability": "Predicted SLA Breach Risk",
                    "risk_bucket": "Risk Bucket",
                    "sla_breach_actual": "Actual SLA Breach",
                }
            )

            renamed_display_columns = [
                {
                    "case_id": "Case ID",
                    "sla_breach_probability": "Predicted SLA Breach Risk",
                    "risk_bucket": "Risk Bucket",
                    "sla_breach_actual": "Actual SLA Breach",
                }[column]
                for column in display_columns
            ]

            st.dataframe(
                top_risk_cases[renamed_display_columns],
                use_container_width=True,
                hide_index=True,
            )

            st.caption(
                "Only the top 10 cases are shown to keep the view operationally focused."
            )
        else:
            st.info("SLA breach probability column is not available.")

    # ==========================================================
    # 6. TECHNICAL DETAILS ONLY ON DEMAND
    # ==========================================================
    with st.expander("Technical Details", expanded=False):
        st.markdown("### Model Evaluation")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("ROC-AUC", f"{roc_auc:.3f}")
        col2.metric("Precision", f"{precision:.3f}")
        col3.metric("Recall", f"{recall:.3f}")
        col4.metric("F1 Score", f"{f1:.3f}")

        st.markdown("### Confusion Matrix")

        if not confusion_matrix.empty:
            st.dataframe(confusion_matrix, use_container_width=True)
        else:
            matrix = best_metrics.get("confusion_matrix")

            if matrix:
                matrix_df = pd.DataFrame(
                    matrix,
                    index=["Actual No Breach", "Actual Breach"],
                    columns=["Predicted No Breach", "Predicted Breach"],
                )
                st.dataframe(matrix_df, use_container_width=True)
            else:
                st.info("Confusion matrix is not available.")

        st.markdown("### Governance Note")

        st.markdown(
            """
            The model is implemented as a transparent baseline using Logistic Regression and Random Forest.

            Final cycle time is intentionally excluded from the feature set to avoid target leakage,
            because the SLA breach label is derived from the 120-day cycle-time threshold.

            PyTorch LSTM and Transformer models remain future work unless they clearly outperform the baseline.
            """
        )