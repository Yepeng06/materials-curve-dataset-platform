from generator.sampler import sample_parameters


def test_explicit_manual_parameters_win():
    template = {
        "default_parameters": {"num_curves": 2, "curve_shape": "near_linear", "noise_level": 0.01},
        "probability_distributions": {},
    }
    out = sample_parameters(
        "explicit",
        {"num_curves": 5, "curve_shape": "irregular", "noise_level": 0.05, "seed": 1234},
        template_data=template,
    )
    assert out["actual_parameters"]["num_curves"] == 5
    assert out["actual_parameters"]["curve_shape"] == "irregular"
    assert out["actual_parameters"]["noise_level"] == 0.05


def test_probabilistic_template_enforced_fields_present():
    template = {
        "default_parameters": {"num_curves": 2},
        "probability_distributions": {
            "num_curves": {"3": 1.0},
            "curve_shape": {"three_stage": 1.0},
            "line_style": {"dashed": 1.0},
            "marker": {"square": 1.0},
            "legend_position": {"outside_right": 1.0},
            "grid": {"true": 1.0},
        },
    }
    out = sample_parameters("probabilistic", {"seed": 7, "num_curves": 1}, template_data=template)
    enforced = out["template_enforced_fields"]
    assert enforced
    assert enforced["num_curves"] == "3"
    assert enforced["curve_shape"] == "three_stage"


def test_template_defaults_applied_recorded_in_explicit():
    out = sample_parameters("explicit", {"template_defaults_applied": True, "seed": 42}, template_data={})
    assert out["template_defaults_applied"] is True
