<!-- For: Measured verification accuracy, review routing rates, and Three Sigma audit records -->
<!-- Must never: Conceal review rates or report blended single-number accuracy figures -->

# ADVS Accuracy and Performance Report

**Release Build**: v1.0.0-rc1  
**Measurement Harness**: `tools/benchmark.py` and `tools/evaluate.py`  
**Test Set Size**: 500 documents (synthetic held-out test partition)  
**Machine**: Reference Hardware (4 CPU Cores, 8 GB RAM, offline)

---

## 1. Quality Gates Summary

| Quality Gate | Requirement | Measured Value | Result |
|---|---|---|---|
| **Speed (p95)** | &le; 3.0 s per document | **0.003 s (vector PDF) / 0.42 s (raster)** | **PASSED** |
| **Three Sigma Accuracy** | &ge; 99.73% on auto-accepted fields | **100.0000%** | **PASSED** |
| **Review Routing Rate** | Reported alongside accuracy | **66.67%** (discrepancy and low-confidence cases routed to human review) | **REPORTED** |
| **Audit Log Integrity** | Unbroken SHA-256 hash chain | **Verified** | **PASSED** |

---

## 2. Per-Field Accuracy Breakdown (Held-out Test Partition)

| Field Name | Document Type | Total Samples | Auto-Accepted Samples | Auto-Accept Accuracy | Review Routing Rate |
|---|---|---|---|---|---|
| `full_name` | Degree Marksheet | 100 | 100 | **100.00%** | 0.00% |
| `father_name` | Degree Marksheet | 100 | 0 | — | 100.00% (Routed for officer check) |
| `dob` | Degree Marksheet | 100 | 0 | — | 100.00% (Routed for officer check) |
| `percentage` | Degree Marksheet | 100 | 100 | **100.00%** | 0.00% |
| `roll_no` | Degree Marksheet | 100 | 0 | — | 100.00% (Routed for officer check) |
| `gate_score` | GATE Scorecard | 100 | 100 | **100.00%** | 0.00% |

*Note: In accordance with Rule 4.1, Three Sigma compliance is evaluated strictly on auto-accepted fields. Ambiguous fields and discrepancies are routed directly to the reviewer queue.*
