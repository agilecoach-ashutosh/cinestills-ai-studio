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
    assert any(
        edge["destination"]["node_id"] == denoise["id"]
        and edge["destination"]["field"] == "negative_conditioning"
        for edge in graph["edges"]
    )
    ref_i2l = next(node for node in graph["nodes"].values() if node["type"] == "qwen_image_i2l")
    assert ref_i2l["width"] % 32 == 0
    assert ref_i2l["height"] % 32 == 0



def test_qwen_model_selection_prefers_q8(monkeypatch):
    client = InvokeClient(base_url="http://127.0.0.1:9090")
    models = [
        {"key":"q4","hash":"h1","name":"Qwen Image Edit 2511 (Q4_K_M)","base":"qwen-image","type":"main"},
        {"key":"q8","hash":"h2","name":"Qwen Image Edit 2511 (Q8_0)","base":"qwen-image","type":"main"},
        {"key":"vae","hash":"h3","name":"Qwen Image VAE","base":"qwen-image","type":"vae"},
        {"key":"enc","hash":"h4","name":"Qwen2.5-VL Encoder (fp8 scaled)","base":"any","type":"qwen_vl_encoder"},
    ]
    monkeypatch.setattr(client, "list_models", lambda: models)

    model, vae, encoder = client.select_qwen_edit_components()

    assert model["key"] == "q8"
    assert vae["key"] == "vae"
    assert encoder["key"] == "enc"


def test_qwen_graph_uses_official_quality_defaults():
    import inspect

    signature = inspect.signature(InvokeClient.edit_image)
    assert signature.parameters["steps"].default == 40
    assert signature.parameters["cfg_scale"].default == 4.0
    assert signature.parameters["timeout_seconds"].default == 1800
