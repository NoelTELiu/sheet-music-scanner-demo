# OMR Demo Pipeline

The demo runs a score image through three stages:

1. **Staff detection** — YOLO detects staff regions and saves each staff as a crop.
2. **Symbol recognition** — the CRNN converts each staff crop into a semantic symbol sequence.
3. **MIDI conversion** — the semantic sequence is converted to MEI and then written as MIDI.

## Check required files

```bash
python -m demo.run_pipeline --check-only
```

Expected runtime files:

```text
models/yolo/best.pt
models/crnn/best_model.pt
models/crnn/tokenizer.json
assets/omr-3.0-SNAPSHOT.jar     # only required for MIDI conversion
```

## Run the full demo

```bash
python -m demo.run_pipeline \
  --image path/to/score.png \
  --yolo-model models/yolo/best.pt \
  --crnn-model models/crnn/best_model.pt \
  --tokenizer models/crnn/tokenizer.json \
  --converter-jar assets/omr-3.0-SNAPSHOT.jar \
  --output demo_output
```

## Recognition only

Use `--skip-midi` to run staff detection and CRNN recognition without the MEI/MIDI conversion stage.

```bash
python -m demo.run_pipeline \
  --image path/to/score.png \
  --yolo-model models/yolo/best.pt \
  --crnn-model models/crnn/best_model.pt \
  --tokenizer models/crnn/tokenizer.json \
  --skip-midi
```

## Output

```text
demo_output/
├── detection/
│   ├── <score>_detected.jpg
│   └── cropped_staves/
├── semantic/
└── midi/
```

The repository does not include the trained runtime weights or matching CRNN tokenizer. Add the corresponding project assets to the paths above before running inference.
