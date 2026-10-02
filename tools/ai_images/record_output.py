#!/usr/bin/env python3
"""Record one manually reviewed image-generation attempt in the AI manifest."""

import argparse
import hashlib
import json
import math
import os
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
SOURCE_MANIFEST = ROOT / "data" / "image-manifest.json"
AI_MANIFEST = ROOT / "tools" / "ai_images" / "manifest.json"
TOOL_REPORTED = "image_gen.imagegen (built-in)"
MODEL_REPORTED = "not reported by tool"
TOOL_VERSION_REPORTED = "not reported by tool"
MAX_ATTEMPTS = 3
CONTINUATION_ATTEMPTS = 2
WEBP_QUALITY = 90


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def timestamp(path):
    return datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def border_color(image):
    image = image.convert("RGB")
    pixels = []
    for x, y in ((0, 0), (image.width - 1, 0), (0, image.height - 1), (image.width - 1, image.height - 1)):
        pixels.append(image.getpixel((x, y)))
    return tuple(round(sum(pixel[channel] for pixel in pixels) / len(pixels)) for channel in range(3))


def pad_to_ratio(image, ratio):
    """Keep every generated pixel and extend the background when ratios differ."""
    image = image.convert("RGB")
    current = image.width / image.height
    if math.isclose(current, ratio, rel_tol=0.003, abs_tol=0.003):
        return image
    color = border_color(image)
    if current > ratio:
        height = math.ceil(image.width / ratio)
        canvas = Image.new("RGB", (image.width, height), color)
        canvas.paste(image, (0, (height - image.height) // 2))
    else:
        width = math.ceil(image.height * ratio)
        canvas = Image.new("RGB", (width, image.height), color)
        canvas.paste(image, ((width - image.width) // 2, 0))
    return canvas


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--id", required=True, help="Catalogue item id")
    parser.add_argument("--artifact", required=True, type=Path, help="Generated image file saved by the built-in tool")
    parser.add_argument("--decision", required=True, choices=("accepted", "rejected"), help="Manual visual review result")
    parser.add_argument("--reason", default="", help="Required rejection reason when decision is rejected")
    parser.add_argument(
        "--continue-failed", action="store_true",
        help="Allow up to two additional attempts for a previously failed item after the user's expanded request",
    )
    args = parser.parse_args()

    prompt = __import__("sys").stdin.read().strip()
    if not prompt:
        parser.error("prompt text is required on stdin")
    if args.decision == "rejected" and not args.reason.strip():
        parser.error("--reason is required for rejected attempts")

    artifact = args.artifact.resolve(strict=True)
    source_items = load_json(SOURCE_MANIFEST)
    source = next((item for item in source_items if item.get("id") == args.id and item.get("kind") == "catalogue-photo"), None)
    if source is None:
        parser.error(f"unknown catalogue-photo id: {args.id}")
    original_path = ROOT / Path(source["original"].replace("/", os.sep))
    if sha256_file(original_path) != source["original_sha256"]:
        parser.error(f"original checksum mismatch: {source['original']}")

    manifest = load_json(AI_MANIFEST)
    entry = next((item for item in manifest["images"] if item["id"] == args.id), None)
    if entry is None:
        parser.error(f"id missing from AI manifest: {args.id}")
    continuation = entry["status"] == "failed" and args.continue_failed
    if entry["status"] != "todo" and not continuation:
        parser.error(f"item is not pending: {args.id} ({entry['status']})")
    attempt_limit = MAX_ATTEMPTS + CONTINUATION_ATTEMPTS if continuation else MAX_ATTEMPTS
    if len(entry.get("attempts", [])) >= attempt_limit:
        parser.error(f"maximum attempts already recorded: {args.id}")

    with Image.open(artifact) as generated:
        generated.load()
        width, height = generated.size
        if width < source["width"] * 2 or height < source["height"] * 2:
            parser.error(f"generated image is smaller than 2x source dimensions: {width}x{height}")
        output = None
        output_hash = None
        output_size = None
        if args.decision == "accepted":
            output = ROOT / "generated" / "imagen" / source["album"] / (Path(source["original"]).stem + ".webp")
            if output.exists():
                parser.error(f"refusing to overwrite existing generated image: {output.relative_to(ROOT)}")
            original_ratio = source["width"] / source["height"]
            ratio = 1.5 if math.isclose(original_ratio, 1.5, rel_tol=0.01, abs_tol=0.01) else original_ratio
            final = pad_to_ratio(generated, ratio)
            target_size = (source["width"] * 2, source["height"] * 2)
            if final.size != target_size:
                final = final.resize(target_size, Image.Resampling.LANCZOS)
            output.parent.mkdir(parents=True, exist_ok=True)
            temporary = None
            try:
                with tempfile.NamedTemporaryFile(prefix=".ai-image-", suffix=".webp", dir=output.parent, delete=False) as temp:
                    temporary = Path(temp.name)
                    final.save(temp, "WEBP", quality=WEBP_QUALITY, method=6)
                    temp.flush()
                    os.fsync(temp.fileno())
                if output.exists():
                    parser.error(f"refusing to overwrite existing generated image: {output.relative_to(ROOT)}")
                os.rename(temporary, output)
                temporary = None
            finally:
                if temporary is not None:
                    temporary.unlink(missing_ok=True)
            output_hash = sha256_file(output)
            with Image.open(output) as webp:
                output_size = list(webp.size)

    attempt_number = len(entry.get("attempts", [])) + 1
    generated_hash = sha256_file(artifact)
    decision = args.decision
    attempt = {
        "attempt": attempt_number,
        "prompt_used": prompt,
        "tool_reported": TOOL_REPORTED,
        "model_reported": MODEL_REPORTED,
        "tool_version_reported": TOOL_VERSION_REPORTED,
        "generation_time": timestamp(artifact),
        "generated_artifact_id": artifact.name,
        "generated_artifact_sha256": generated_hash,
        "generated_artifact_pixel_size": [width, height],
        "decision": decision,
    }
    if args.reason:
        attempt["rejection_reason"] = args.reason.strip()
    if output is not None:
        attempt.update({
            "webp_quality": WEBP_QUALITY,
            "output_path": output.relative_to(ROOT).as_posix(),
            "output_sha256": output_hash,
            "output_pixel_size": output_size,
        })
    entry.setdefault("attempts", []).append(attempt)
    entry.update({
        "prompt_used": prompt,
        "tool_reported": TOOL_REPORTED,
        "model_reported": MODEL_REPORTED,
        "tool_version_reported": TOOL_VERSION_REPORTED,
        "generation_time": attempt["generation_time"],
    })
    if output is not None:
        entry.update({
            "status": "done",
            "output_path": output.relative_to(ROOT).as_posix(),
            "output_sha256": output_hash,
            "output_pixel_size": output_size,
            "output_bytes": output.stat().st_size,
            "webp_quality": WEBP_QUALITY,
        })
    elif attempt_number == attempt_limit:
        entry.update({"status": "failed", "output_path": None, "output_sha256": None})
    write_json(AI_MANIFEST, manifest)
    print(f"{args.id}: {decision}; attempt {attempt_number}/{attempt_limit}; status={entry['status']}")


if __name__ == "__main__":
    main()
