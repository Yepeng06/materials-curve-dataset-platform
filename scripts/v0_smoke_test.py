from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.main import PreviewRequest, GenerateRequest, preview, generate


def _assert(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def run() -> None:
    preview_root = ROOT / "examples" / "previews"
    dataset_root = ROOT / "datasets"

    print("[1/3] preview explicit/probabilistic checks")
    explicit = preview(PreviewRequest(mode="explicit", preview_count=3, seed=1234))
    probabilistic = preview(PreviewRequest(mode="probabilistic", preview_count=6, seed=1234))
    _assert(explicit["preview_count"] == 3, "explicit preview_count should be 3")
    _assert(probabilistic["preview_count"] == 6, "probabilistic preview_count should be 6")

    for payload in (explicit, probabilistic):
        for item in payload["items"]:
            image = ROOT / item["image_path"]
            ann = ROOT / item["annotation_path"]
            _assert(image.exists(), f"missing image: {image}")
            _assert(ann.exists(), f"missing annotation: {ann}")
            for csv in item["csv_paths"]:
                _assert((ROOT / csv).exists(), f"missing csv: {csv}")

    print("[2/3] generate dataset total_count=6 checks")
    result = generate(
        GenerateRequest(
            dataset_name="smoke",
            version="v0",
            total_count=6,
            mode="probabilistic",
            seed=4321,
            split={"train": 0.7, "val": 0.2, "test": 0.1},
        )
    )

    dataset_dir = ROOT / result["dataset_path"]
    _assert(dataset_dir.exists(), "dataset directory should exist")
    for split in ["train", "val", "test"]:
        for bucket in ["images", "annotations", "csv"]:
            _assert((dataset_dir / bucket / split).exists(), f"missing {bucket}/{split}")

    for required in ["config.yaml", "distribution.yaml", "seed.json", "summary.json", "quality_report.json", "README.md"]:
        _assert((dataset_dir / required).exists(), f"missing {required}")

    print("[3/3] seed reproducibility checks")
    a = preview(PreviewRequest(mode="probabilistic", preview_count=3, seed=2026))
    b = preview(PreviewRequest(mode="probabilistic", preview_count=3, seed=2026))
    c = preview(PreviewRequest(mode="probabilistic", preview_count=3, seed=2027))

    a_sampled = [x["annotation"]["style"].get("sampled_parameters", {}) for x in a["items"]]
    b_sampled = [x["annotation"]["style"].get("sampled_parameters", {}) for x in b["items"]]
    c_sampled = [x["annotation"]["style"].get("sampled_parameters", {}) for x in c["items"]]

    _assert(a_sampled == b_sampled, "same seed should have same sampled params")
    _assert(a_sampled != c_sampled, "different seed should change sampled params")

    print("SMOKE TEST PASS")
    print(json.dumps({"preview_dir": str(preview_root), "dataset_dir": str(dataset_root), "latest_dataset": result["dataset_path"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    run()
