# OMR Inference Pipeline

This directory contains the command-line interface used to connect the three inference stages of the original Optical Music Recognition project:

1. **Staff detection** — YOLO detects individual staff regions from a score image.
2. **Symbol recognition** — the CRNN converts each detected staff crop into a semantic symbol sequence.
3. **MIDI conversion** — the recognized semantic sequence is converted to MEI and then exported as MIDI.

The pipeline is included to preserve and document the original inference workflow.

This public repository is intended primarily for **source review and academic portfolio presentation**. It does not include the trained model weights, matching CRNN tokenizer, or third-party semantic converter required for standalone execution.

## Pipeline overview

```text
Sheet-music image
        │
        ▼
YOLO staff detection
        │
        ▼
Individual staff crops
        │
        ▼
CRNN symbol recognition
        │
        ▼
Semantic symbol sequences
        │
        ▼
Semantic-to-MEI conversion
        │
        ▼
MEI / MIDI output
```

## Expected runtime assets

The original inference workflow uses the following runtime assets:

```text
models/yolo/best.pt
models/crnn/best_model.pt
models/crnn/tokenizer.json
assets/omr-3.0-SNAPSHOT.jar
```

Their roles are:

- `models/yolo/best.pt` — trained YOLO staff detector.
- `models/crnn/best_model.pt` — trained CRNN semantic recognizer.
- `models/crnn/tokenizer.json` — tokenizer corresponding to the retained CRNN checkpoint.
- `assets/omr-3.0-SNAPSHOT.jar` — third-party semantic-to-MEI converter used by the MIDI conversion stage.

These files are not distributed in this repository.

## Runtime asset check

The interface can check whether the expected runtime assets are available:

```bash
python -m demo.run_pipeline --check-only
```

This command only validates the expected file locations. It does not run inference.

## Example pipeline invocation

With the corresponding runtime assets available, the original end-to-end inference workflow can be invoked with:

```bash
python -m demo.run_pipeline \
  --image path/to/score.png \
  --yolo-model models/yolo/best.pt \
  --crnn-model models/crnn/best_model.pt \
  --tokenizer models/crnn/tokenizer.json \
  --converter-jar assets/omr-3.0-SNAPSHOT.jar \
  --output demo_output
```

The command-line interface is retained to show how the project components were connected and executed.

## Output structure

A complete run produces an output directory with the following general structure:

```text
demo_output/
├── detection/
│   ├── <score>_detected.jpg
│   └── cropped_staves/
├── semantic/
└── midi/
```

### Detection output

```text
demo_output/detection/
```

contains:

- an annotated copy of the input score showing detected staff regions;
- individual cropped staff images used by the CRNN recognition stage.

### Semantic output

```text
demo_output/semantic/
```

contains the symbol sequences predicted for the detected staff regions.

These semantic sequences represent the intermediate output between image recognition and symbolic music conversion.

### MIDI output

```text
demo_output/midi/
```

contains the final symbolic music output generated after semantic-to-MEI conversion.

The MIDI stage requires the external semantic converter.

## Running without MIDI conversion

The detection and CRNN recognition stages can be invoked without the final MIDI conversion stage:

```bash
python -m demo.run_pipeline \
  --image path/to/score.png \
  --yolo-model models/yolo/best.pt \
  --crnn-model models/crnn/best_model.pt \
  --tokenizer models/crnn/tokenizer.json \
  --skip-midi \
  --output demo_output
```

This stops the pipeline after semantic symbol recognition.

## Pipeline stages

### 1. Staff detection

The input score image is passed to the trained YOLO detector.

The detector identifies staff regions and produces individual staff crops for downstream recognition.

Conceptually:

```text
Full score image
      │
      ▼
YOLO detector
      │
      ├── Annotated detection image
      │
      └── Cropped staff images
```

The detector was trained using a single object class representing musical staff regions.

### 2. CRNN symbol recognition

Each cropped staff image is passed independently to the CRNN recognizer.

The recognition model combines:

```text
Image
  │
  ▼
CNN feature extraction
  │
  ▼
Sequential feature representation
  │
  ▼
Bidirectional LSTM
  │
  ▼
CTC decoding
  │
  ▼
Semantic symbol sequence
```

The matching tokenizer is required because token indices depend on the vocabulary used during training.

### 3. Semantic-to-MIDI conversion

The predicted semantic representation is converted into symbolic music using the external semantic converter.

The conversion path is:

```text
Semantic prediction
        │
        ▼
Semantic-to-MEI converter
        │
        ▼
MEI
        │
        ▼
MIDI
```

This stage depends on the third-party converter JAR and is therefore not self-contained within this repository.

## Intended use of this directory

The files in this directory serve two purposes:

- to preserve the end-to-end inference interface used in the original project;
- to make the relationship between the detector, recognizer, and symbolic conversion stages easy to inspect.

This directory should therefore be read as a **reference implementation of the original inference workflow**, rather than as a standalone reproduction package.

The trained checkpoints, tokenizer, datasets, full environment snapshot, and third-party converter required for exact reproduction are intentionally outside the scope of this public source release.
