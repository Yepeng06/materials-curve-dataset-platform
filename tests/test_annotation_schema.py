from backend.main import PreviewRequest, preview


REQUIRED_TOP_LEVEL = {
    "dataset_info",
    "image",
    "plot_area",
    "axis",
    "style",
    "legend",
    "curves",
    "quality_check",
}


def test_mcg_json_top_level_stable():
    resp = preview(PreviewRequest(mode="explicit", preview_count=3, seed=909))
    ann = resp["items"][0]["annotation"]
    assert REQUIRED_TOP_LEVEL.issubset(set(ann.keys()))
    dataset_info = ann["dataset_info"]
    assert dataset_info["generator_version"] == "V0fix-final-2"
    assert dataset_info["dataset_version"] == "preview"
    assert dataset_info["version"] == dataset_info["dataset_version"]


def test_curves_contain_curve_index_and_total_curves():
    resp = preview(PreviewRequest(mode="explicit", preview_count=3, seed=909, num_curves=3))
    curves = resp["items"][0]["annotation"]["curves"]
    for idx, curve in enumerate(curves):
        assert curve["curve_index"] == idx
        assert curve["total_curves"] == 3
