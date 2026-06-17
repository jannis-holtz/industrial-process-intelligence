from src.dashboard.views.bottleneck_analysis import render_bottleneck_analysis_view
from src.dashboard.views.data_quality import render_data_quality_view
from src.dashboard.views.executive_overview import render_executive_overview
from src.dashboard.views.platform_layers import render_process_layers_view
from src.dashboard.views.prediction import render_prediction_risk_view
from src.dashboard.views.process_explorer import render_process_explorer_view
from src.dashboard.views.recommendations import render_recommendations_view
from src.dashboard.views.rework_detection import render_rework_detection_view
from src.dashboard.views.root_cause import render_root_cause_analysis_view
from src.dashboard.views.sla_compliance import render_sla_compliance_view
from src.dashboard.views.variant_intelligence import render_variant_intelligence_view


__all__ = [
    "render_bottleneck_analysis_view",
    "render_data_quality_view",
    "render_executive_overview",
    "render_prediction_risk_view",
    "render_process_explorer_view",
    "render_process_layers_view",
    "render_recommendations_view",
    "render_rework_detection_view",
    "render_root_cause_analysis_view",
    "render_sla_compliance_view",
    "render_variant_intelligence_view",
]