from mdt.core.result import CommandResult


def test_command_result_defaults() -> None:
    result = CommandResult(success=True)

    assert result.success is True
    assert result.output == ""
    assert result.error is None
    assert result.data == {}
    assert result.exit_requested is False


def test_command_result_field_values() -> None:
    result = CommandResult(
        success=False,
        output="oops",
        error="failed",
        data={"code": 123},
        exit_requested=True,
    )

    assert result.success is False
    assert result.output == "oops"
    assert result.error == "failed"
    assert result.data == {"code": 123}
    assert result.exit_requested is True

