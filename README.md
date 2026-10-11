# Sheet Music Scanner — YOLO + CRNN Optical Music Recognition

An end-to-end **Optical Music Recognition (OMR)** project that detects musical staves in a score image, recognizes notation symbols, and converts the recognized sequence into symbolic music and MIDI.

## Pipeline

```mermaid
flowchart LR
    A[Sheet-music image] --> B[YOLO staff detection]
    B --> C[Staff crops]
    C --> D[CRNN + CTC recognition]
    D --> E[Semantic symbol sequences]
    E --> F[Semantic-to-MEI conversion]
    F --> G[MEI / MIDI output]
```

The project contains four main components:

- **Preprocessing** — splits MusicXML/MXL scores, renders score images, generates semantic labels, packages datasets, and applies augmentation.
- **Staff detection** — uses YOLO to locate and crop individual staff regions from a score image.
- **Music-symbol recognition** — uses a CRNN with bidirectional LSTMs and CTC decoding to recognize semantic or agnostic symbol sequences.
- **Postprocessing** — converts semantic predictions to MEI/MIDI and provides an end-to-end demo pipeline.

## Repository structure

```text
.
├── preprocess/              # Dataset preparation and augmentation
├── yolo/                    # Staff detector training and evaluation
├── crnn/                    # CRNN training and evaluation
├── postprocess/             # Semantic-to-MEI/MIDI conversion
├── demo/                    # End-to-end inference pipeline
├── models/                  # Runtime model locations
├── assets/                  # Third-party runtime assets
├── results/                 # Representative training results
├── scripts/                 # Utility scripts
├── docs/                    # Project notes
└── requirements.txt
```

## Run the demo

The demo processes one score image through staff detection, CRNN recognition, and optional MIDI conversion.

### 1. Check runtime assets

```bash
python -m demo.run_pipeline --check-only
```

### 2. Run the full pipeline

```bash
python -m demo.run_pipeline \
  --image path/to/score.png \
  --yolo-model models/yolo/best.pt \
  --crnn-model models/crnn/best_model.pt \
  --tokenizer models/crnn/tokenizer.json \
  --converter-jar assets/omr-3.0-SNAPSHOT.jar
```

The pipeline produces:

```text
demo_output/
├── detection/
│   ├── <score>_detected.jpg     # Staff detections overlaid on the input image
│   └── cropped_staves/          # Individual staff crops
├── semantic/                    # CRNN semantic predictions
└── midi/                        # Final MIDI output
```

To stop after symbol recognition and skip MIDI conversion:

```bash
python -m demo.run_pipeline \
  --image path/to/score.png \
  --yolo-model models/yolo/best.pt \
  --crnn-model models/crnn/best_model.pt \
  --tokenizer models/crnn/tokenizer.json \
  --skip-midi
```

See [`demo/README.md`](demo/README.md) for the demo-specific setup.

> **Runtime asset note**  
> Trained model weights, the matching CRNN tokenizer, datasets, and the third-party semantic-converter JAR are not included in this repository. Their expected locations are documented in [`models/README.md`](models/README.md) and [`assets/README.md`](assets/README.md).

## Training

### YOLO staff detector

The detector is trained on one class: `musical-staff-line`.

```bash
python -m yolo.yolo_train --data yolo/data.yaml --epochs 300
```

Copy `yolo/data.example.yaml` to `yolo/data.yaml` and update the dataset paths before training.

### CRNN semantic recognition

The semantic recognizer combines convolutional feature extraction, bidirectional LSTMs, and CTC loss.

```bash
python -m crnn.train_crnn_semantic \
  --data-dir path/to/primus_style_dataset \
  --epochs 200 \
  --batch-size 48
```

The retained semantic training run reached its minimum validation loss at **epoch 181 (0.034795)**.

![Semantic CRNN training history](results/semantic_training_progress.png)

## Preprocessing

Example preprocessing commands:

```bash
python -m preprocess.split_measure --input-dir input_mxl --output-dir split_xml --measures-per-file 1
python -m preprocess.semantic --input-dir split_xml --output-dir semantic_labels
python -m preprocess.package --labels semantic_labels --images rendered_png --output dataset
python -m preprocess.addnoise --source dataset --output aug_dataset --noise-factor 0.3
```

Rendering MusicXML to PDF requires MuseScore. PDF rasterization may also require Poppler, depending on the platform.

## Training results

`results/` contains representative training curves and history files for the semantic and agnostic CRNN experiments. Large checkpoints and TensorBoard logs are omitted from the repository.

## Team contributions

- **Liang-Yu Cheng** — CRNN model training; preprocessing templates; YOLO evaluation; postprocessing for music generation.
- **Po-Chen Liu** — MusicXML measure splitting; music-domain consultation; music-generation evaluation.
- **Chih-Yu Hsieh** — YOLO research and implementation.
- **Yun-En Chung** — image-cropping improvements; data preprocessing; final presentation.
- **Jyun-Hung Wu** — measure-splitting and image-cropping improvements; preprocessing; CRNN evaluation.
- **Chi-Lun Chen** — automated labeling program for the CRNN dataset.
- **Shared** — dataset collection, project proposal preparation, and video presentation.

## Project release note

This repository is prepared for source review and academic portfolio presentation. It includes the implementation and representative training results, while large datasets, checkpoints, caches, and third-party binaries are kept outside the repository.

## License / third-party material

No new open-source license is added on behalf of the original project team. Third-party datasets, libraries, pretrained models, and the semantic converter remain subject to their respective terms.
