"""
FLARE-X — Flame Learning, Analysis, Risk & Extinction Explorer
==============================================================

An interpretable analysis layer for archived NASA microgravity combustion
imagery. NASA-data-driven research prototype. Not a NASA product, not
NASA-endorsed, not NASA-validated, not a certification system.

The scientific pipeline in this package runs standalone. It has no
dependency on any language model, web application or network service.
"""

from .provenance import (ClaimLevel, Measurement, ProvenanceChain,
                         ProvenanceNode, not_verified, file_digest,
                         PIPELINE_VERSION)
from .segmentation import (SegmentationConfig, SegmentationResult,
                           segment_flame, estimate_background,
                           radiance_proxy, sootiness_index,
                           sweep_threshold_sensitivity)
from .morphology import DuctGeometry, FlameFeatures, extract_features
from .timeseries import (CombustionState, StateSegment, StateRules,
                         detect_change_points, label_states,
                         align_to_reference_events, confusion_matrix,
                         classification_report_from_labels)
from .extinction import (EPITerm, EPIConfig, EPIResult, compute_epi,
                         validate_monotonicity, DEFAULT_TERMS, DISCLAIMER)
from .pipeline import RunMetadata, RunResult, analyse_run

__version__ = PIPELINE_VERSION
__all__ = [
    "ClaimLevel", "Measurement", "ProvenanceChain", "ProvenanceNode",
    "not_verified", "file_digest", "PIPELINE_VERSION",
    "SegmentationConfig", "SegmentationResult", "segment_flame",
    "estimate_background", "radiance_proxy", "sootiness_index",
    "sweep_threshold_sensitivity",
    "DuctGeometry", "FlameFeatures", "extract_features",
    "CombustionState", "StateSegment", "StateRules", "detect_change_points",
    "label_states", "align_to_reference_events", "confusion_matrix",
    "classification_report_from_labels",
    "EPITerm", "EPIConfig", "EPIResult", "compute_epi",
    "validate_monotonicity", "DEFAULT_TERMS", "DISCLAIMER",
    "RunMetadata", "RunResult", "analyse_run",
    "__version__",
]
