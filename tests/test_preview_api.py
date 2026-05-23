from backend.main import PreviewRequest, preview


def test_preview_response_structure_and_paths():
    resp = preview(PreviewRequest(mode="explicit", preview_count=3, seed=101, num_curves=2, curve_shape="irregular"))
    assert resp["status"] == "ok"
    assert resp["items"]
    first = resp["items"][0]
    assert "image_path" in first
    assert "annotation_path" in first
    assert "csv_paths" in first
    assert len(first["csv_paths"]) == 2


def test_preview_explicit_actual_parameters_keep_manual_values():
    req = PreviewRequest(mode="explicit", seed=321, num_curves=4, curve_shape="three_stage", noise_level=0.03)
    resp = preview(req)
    actual = resp["items"][0]["annotation"]["style"]["actual_parameters"]
    assert actual["num_curves"] == 4
    assert actual["curve_shape"] == "three_stage"
    assert actual["noise_level"] == 0.03


def test_preview_probabilistic_enforced_fields_non_empty():
    resp = preview(PreviewRequest(mode="probabilistic", preview_count=3, seed=2026, template_id="real_mainstream"))
    style = resp["items"][0]["annotation"]["style"]
    assert style["template_enforced_fields"]
