from contractor.models import BreakingChange


def test_breaking_change_fields():
    bc = BreakingChange(
        kind="endpoint_removed",
        path="/users/{id}",
        method="DELETE",
        location="DELETE /users/{id}",
        description="Endpoint DELETE /users/{id} was removed",
        base_value="DELETE /users/{id}",
        candidate_value="",
    )
    assert bc.kind == "endpoint_removed"
    assert bc.path == "/users/{id}"
    assert bc.method == "DELETE"
    assert bc.is_breaking is True
