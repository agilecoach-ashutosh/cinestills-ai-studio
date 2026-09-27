from app.services.invoke_client import InvokeClient


def test_invoke_client_has_required_runtime_helpers():
    client = InvokeClient(base_url="http://127.0.0.1:9090")
    assert callable(client._raise_for_status)
    assert callable(client._find_value)
    assert callable(client.select_qwen_edit_components)
    assert callable(client._build_qwen_image_edit_graph)


def test_find_value_walks_nested_payloads():
    payload = {"session": {"results": [{"image_name": "result.png"}]}}
    assert InvokeClient._find_value(payload, "image_name") == "result.png"


def test_edit_path_no_longer_exposes_sdxl_selector():
    client = InvokeClient(base_url="http://127.0.0.1:9090")
    assert not hasattr(client, "select_sdxl_model")
