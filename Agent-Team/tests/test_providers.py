from ai_team.providers.azure_foundry import normalize_azure_foundry_endpoint


def test_normalize_azure_foundry_endpoint() -> None:
    assert normalize_azure_foundry_endpoint("https://coding-eu-resource.services.ai.azure.com") == "https://coding-eu-resource.services.ai.azure.com/openai/v1"
    assert normalize_azure_foundry_endpoint("https://coding-eu-resource.services.ai.azure.com/openai/v1/") == "https://coding-eu-resource.services.ai.azure.com/openai/v1"
