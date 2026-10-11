import argparse
import logging
import re
import shutil
import subprocess
from pathlib import Path

from music21 import converter, stream, tempo

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SEMANTIC_IMPORTER_CLASS = "es.ua.dlsi.im3.omr.encoding.semantic.SemanticImporter"


def natural_staff_key(path: Path):
    match = re.search(r"staff_(\d+)", path.stem)
    return int(match.group(1)) if match else path.stem


def extract_time_signature(content: str):
    match = re.search(r"timeSignature-[^,\s]+", content)
    return match.group(0) if match else None


def add_time_signature(content: str, time_signature: str) -> str:
    pattern = r"timeSignature-[^,\s]+"
    if re.search(pattern, content):
        return re.sub(pattern, time_signature, content)
    key_pattern = r"(keySignature-[^,\s]+)"
    if re.search(key_pattern, content):
        return re.sub(key_pattern, r"\1\t" + time_signature, content)
    return time_signature + "\t" + content


def semantic_to_mei(semantic_file: Path, output_mei: Path, converter_jar: Path) -> None:
    result = subprocess.run(
        ["java", "-cp", str(converter_jar), SEMANTIC_IMPORTER_CLASS, str(semantic_file), str(output_mei)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Semantic converter failed for {semantic_file.name}:\n{result.stderr.strip()}"
        )


def mei_to_midi(mei_file: Path, midi_file: Path, bpm: float) -> None:
    score = converter.parse(str(mei_file))
    score.insert(0, tempo.MetronomeMark(number=bpm))
    score.write("midi", fp=str(midi_file))


def combine_midis(midi_files, output_file: Path) -> None:
    combined = stream.Score()
    for midi_file in midi_files:
        parsed = converter.parse(str(midi_file))
        for part in parsed.parts:
            combined.append(part)
        if not parsed.parts:
            combined.append(parsed)
    combined.write("midi", fp=str(output_file))


def process_semantic_files(input_dir: str, output_dir: str, converter_jar: str, bpm: float, num_parts: int):
    if shutil.which("java") is None:
        raise RuntimeError("Java was not found on PATH; it is required for semantic-to-MEI conversion.")

    jar_path = Path(converter_jar)
    if not jar_path.is_file():
        raise FileNotFoundError(
            f"Semantic converter JAR not found: {jar_path}. "
            "See assets/README.md or run scripts/fetch_semantic_converter.py."
        )

    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    semantic_files = sorted(input_path.glob("*.semantic"), key=natural_staff_key)
    if not semantic_files:
        raise RuntimeError(f"No .semantic files found in {input_path}")
    if num_parts < 1:
        raise ValueError("--num-parts must be at least 1")

    first_content = semantic_files[0].read_text(encoding="utf-8")
    time_signature = extract_time_signature(first_content)
    if time_signature:
        for path in semantic_files[1:]:
            content = path.read_text(encoding="utf-8")
            path.write_text(add_time_signature(content, time_signature), encoding="utf-8")

    part_outputs = []
    for part_num in range(num_parts):
        selected = [path for index, path in enumerate(semantic_files) if index % num_parts == part_num]
        staff_midis = []
        for semantic_file in selected:
            mei_file = output_path / f"{semantic_file.stem}.mei"
            midi_file = output_path / f"{semantic_file.stem}.mid"
            semantic_to_mei(semantic_file, mei_file, jar_path)
            mei_to_midi(mei_file, midi_file, bpm)
            staff_midis.append(midi_file)
            mei_file.unlink(missing_ok=True)

        if staff_midis:
            part_file = output_path / f"part{part_num + 1}.mid"
            combine_midis(staff_midis, part_file)
            part_outputs.append(part_file)

    final_file = output_path / "combined_score.mid"
    combine_midis(part_outputs, final_file)
    logger.info("Created %s", final_file)
    return final_file


def main():
    parser = argparse.ArgumentParser(description="Convert recognized semantic sequences to MIDI.")
    parser.add_argument("--input-dir", default="demo_output/semantic")
    parser.add_argument("--output-dir", default="demo_output/midi")
    parser.add_argument("--converter-jar", required=True)
    parser.add_argument("--bpm", type=float, default=120.0)
    parser.add_argument("--num-parts", type=int, default=1)
    args = parser.parse_args()

    process_semantic_files(args.input_dir, args.output_dir, args.converter_jar, args.bpm, args.num_parts)


if __name__ == "__main__":
    main()
