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


def test_qwen_reference_edit_starts_from_noise():
    client = InvokeClient(base_url="http://127.0.0.1:9090")
    model = {"key":"m","hash":"h","name":"Qwen Image Edit 2511 (Q8_0)","base":"qwen-image","type":"main","submodel_type":None}
    vae = {"key":"v","hash":"h","name":"Qwen Image VAE","base":"qwen-image","type":"vae","submodel_type":None}
    encoder = {"key":"e","hash":"h","name":"Qwen2.5-VL Encoder (fp8 scaled)","base":"any","type":"qwen_vl_encoder","submodel_type":None}
    graph = client._build_qwen_image_edit_graph(
        image_name="source.png",
        prompt="change the background",
        model=model,
        vae_model=vae,
        encoder_model=encoder,
        width=768,
        height=1024,
        strength=0.72,
        steps=20,
        cfg_scale=4.0,
    )
    denoise = next(node for node in graph["nodes"].values() if node["type"] == "qwen_image_denoise")
    assert denoise["denoising_start"] == 0.0
    assert any(
        edge["destination"]["node_id"] == denoise["id"]
        and edge["destination"]["field"] == "reference_latents"
        for edge in graph["edges"]
    )
    assert not any(
        edge["destination"]["node_id"] == denoise["id"]
        and edge["destination"]["field"] == "latents"
        for edge in graph["edges"]
    )
