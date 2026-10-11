# Third-Party Runtime Asset

MIDI conversion uses the PrIMuS semantic converter:

```text
assets/omr-3.0-SNAPSHOT.jar
```

This JAR is not included in the repository. When the upstream University of Alicante download is available, it can be retrieved with:

```bash
python scripts/fetch_semantic_converter.py
```

The demo calls the converter directly through Java.
