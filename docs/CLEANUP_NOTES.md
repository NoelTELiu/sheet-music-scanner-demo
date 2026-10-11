# Cleanup notes

This repository was prepared from an archived academic project folder for public portfolio review.

## Removed from the public mirror

- two 134-byte Git LFS pointer files named `omr-3.0-SNAPSHOT.jar` (the real object was ~112 MB);
- two large CRNN checkpoint files (~85 MB and ~91 MB);
- `__pycache__` bytecode;
- TensorBoard event logs;
- a ~4 MB dataset split manifest containing machine-specific dataset paths;
- duplicated demo copy of the semantic CRNN training script;
- stale hard-coded paths to local Windows/WSL installations.

## Correctness-oriented cleanup

- demo model paths are command-line arguments instead of frozen experiment paths;
- the demo no longer falls back to generic `yolov8s.pt`, which is not a staff detector;
- CRNN inference requires a matching tokenizer explicitly;
- semantic preprocessing now emits tab-separated tokens, matching the tokenizer and downstream converter;
- postprocessing receives the converter JAR path explicitly and invokes Java directly;
- preprocessing scripts use command-line arguments instead of executing local example paths at import time;
- the agnostic test imports the actual `train_crnn_agnostic.py` module rather than a missing historical filename.
