import httpx

def api_client() -> httpx.Client:
    return httpx.Client(base_url="https://data.cityofchicago.org/resource")