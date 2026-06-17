from urllib.parse import quote

import streamlit as st


def module_navigation_link(label: str, target_view: str) -> None:
    href = f"?view={quote(target_view)}#top"

    st.markdown(
        f"""
        <a class="module-button-link" href="{href}" target="_self">
            {label}
        </a>
        """,
        unsafe_allow_html=True,
    )


def render_module_preview_grid() -> None:
    st.markdown("## Intelligence Modules")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            <div class="module-card-small">
                <div class="module-title">🧭 Variant Intelligence</div>
                <div class="module-subtitle">Identify frequent and inefficient process paths.</div>
                <p style="color:#cbd5e1;font-size:0.78rem;">
                    Start → Purchase Order → Goods Receipt → Invoice Receipt → Clear Invoice
                </p>
                <p style="color:#38bdf8;font-size:0.78rem;">
                    Active: variant ranking by frequency and cycle time.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        module_navigation_link("Explore Variants →", "🧭 Variant Intelligence")

    with col2:
        st.markdown(
            """
            <div class="module-card-small">
                <div class="module-title">⏱️ Bottleneck Analysis</div>
                <div class="module-subtitle">Measure waiting times between process steps.</div>
                <p style="color:#cbd5e1;font-size:0.78rem;">
                    Focus: transitions with high frequency and high average waiting time.
                </p>
                <p style="color:#38bdf8;font-size:0.78rem;">
                    Active: bottleneck impact ranking + delay cost estimate.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        module_navigation_link("Explore Bottlenecks →", "⏱️ Bottleneck Analysis")

    with col3:
        st.markdown(
            """
            <div class="module-card-small">
                <div class="module-title">🔎 Root Cause</div>
                <div class="module-subtitle">Find drivers behind slow or exceptional cases.</div>
                <p style="color:#cbd5e1;font-size:0.78rem;">
                    Dimensions: item category, company, vendor, document type and activities.
                </p>
                <p style="color:#38bdf8;font-size:0.78rem;">
                    Active: slow-case signal ranking.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        module_navigation_link("Explore Root Causes →", "🔎 Root Cause")

    st.markdown('<div class="module-grid-spacer"></div>', unsafe_allow_html=True)

    col4, col5, col6 = st.columns(3)

    with col4:
        st.markdown(
            """
            <div class="module-card-small">
                <div class="module-title">🎯 Recommendations</div>
                <div class="module-subtitle">Translate findings into prioritized actions.</div>
                <p style="color:#cbd5e1;font-size:0.78rem;">
                    Active: rule-based recommendations from bottleneck and variant signals.
                </p>
                <p style="color:#38bdf8;font-size:0.78rem;">
                    Active: action priority ranking.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        module_navigation_link("View Recommendations →", "🎯 Recommendations")

    with col5:
        st.markdown(
            """
            <div class="module-card-small">
                <div class="module-title">⚠️ Prediction & Risk</div>
                <div class="module-subtitle">Predict cases likely to exceed cycle-time thresholds.</div>
                <p style="color:#cbd5e1;font-size:0.78rem;">
                    Baseline first, PyTorch LSTM later for sequence modeling.
                </p>
                <p style="color:#38bdf8;font-size:0.78rem;">
                    Planned: risk score and model comparison.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        module_navigation_link("Open Prediction Center →", "⚠️ Prediction & Risk")

    with col6:
        st.markdown(
            """
            <div class="module-card-small">
                <div class="module-title">🧱 Platform Layers</div>
                <div class="module-subtitle">Explain how raw process data becomes decisions.</div>
                <p style="color:#cbd5e1;font-size:0.78rem;">
                    Data Layer → Analytics Layer → Prediction Layer → Recommendation Layer.
                </p>
                <p style="color:#38bdf8;font-size:0.78rem;">
                    Available as architecture view.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        module_navigation_link("View Platform Layers →", "🧱 Platform Layers")