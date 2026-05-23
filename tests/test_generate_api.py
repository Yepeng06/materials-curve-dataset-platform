import json
from pathlib import Path

from backend.main import GenerateRequest, generate


def test_generate_annotation_version_and_curve_fields():
    req = GenerateRequest(
        dataset_name="pytest_dataset",
        version="v0fix",
        total_count=3,
        split={"train": 0.34, "val": 0.33, "test": 0.33},
        mode="explicit",
        template_id="real_mainstream",
        num_curves=2,
        seed=456,
    )
    resp = generate(req)
    dataset_dir = Path(resp["dataset_path"])
    ann_files = sorted(dataset_dir.glob("annotations/*/*.json"))
    assert ann_files
    ann = json.loads(ann_files[0].read_text(encoding="utf-8"))
    ds = ann["dataset_info"]
    assert ds["generator_version"] == "V0fix-final-2"
    assert ds["dataset_version"] == "v0fix"
    assert ds["version"] == ds["dataset_version"]
    curves = ann["curves"]
    for idx, curve in enumerate(curves):
        assert curve["curve_index"] == idx
        assert curve["total_curves"] == 2
