from qdrant_client import QdrantClient

client = QdrantClient(
    url="https://6089d48d-2fa8-4ecf-9f65-125d0d53a8e8.eu-central-1-0.aws.cloud.qdrant.io",
    api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIiwic3ViamVjdCI6ImFwaS1rZXk6MTEyNTJlZWEtZDIzNy00MDQwLWI4MzktN2ZkYzU1YWI5Y2MxIn0.u84mdcD6hpCAbMsEz_uad_eNGDctGEfTGJM5cHmweK4",
)

for name in [
    "hospital_schema",
    "value_embeddings",
]:
    info = client.get_collection(name)

    print(
        name,
        "points =", info.points_count,
        "vectors =", info.config.params.vectors,
    )