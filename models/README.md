# Model Assets

Place the trained demo models in the following locations:

```text
models/
├── yolo/
│   └── best.pt
└── crnn/
    ├── best_model.pt
    └── tokenizer.json
```

The CRNN checkpoint and `tokenizer.json` must come from the **same training run**, because the tokenizer defines the class-to-symbol mapping used during decoding.

Model binaries are not included in this repository. The archived project copy did not contain a complete matching set of the final YOLO weight, CRNN checkpoint, and tokenizer required for inference.
