from operator import index
from pathlib import Path
import json

from sqlalchemy import table

from src import graph
from src.config.paths import GRAPH_JSON, SCHEMA_JSON,ENRICHED_SCHEMA_JSON
from src.graph.graph_enricher import GraphEnricher
from src.graph.graph_exporter import GraphExporter
from src.graph.graph_loader import GraphLoader
from src.ingestion.schema_models import TableInfo
from src.graph.schema_graph import SchemaGraph
from src.relationship.relationship_index import RelationshipIndex
from src.relationship.inference_engine import (
    RelationshipInferenceEngine,
)

schema_path = ENRICHED_SCHEMA_JSON

def print_neighbors(graph, table_id):

    print("=" * 60)
    print(f"Neighbors of {table_id}")
    print("=" * 60)

    neighbors = graph.get_neighbors(table_id)

    if not neighbors:
        print("No neighbors")
        return

    for node in neighbors:
        print(node.id)

def main():

    schema = [
        TableInfo.model_validate(item)
        for item in json.loads(schema_path.read_text())
    ]

    graph = SchemaGraph.build(schema)

    index = RelationshipIndex()
    index.build(graph)

    engine = RelationshipInferenceEngine()

    relationships = engine.infer_relationships(
        graph,
        index,
    )


    exporter = GraphExporter()
    enricher = GraphEnricher()

    graph = enricher.enrich(graph, relationships)

    exporter.export(
        graph,
        GRAPH_JSON,
    )

    loader = GraphLoader()

    loaded = loader.load(
        GRAPH_JSON,
        schema=schema
    )

    print(len(graph.nodes))
    print(len(loaded.nodes))

    node = loaded.get_node(
        "mimiciv_hosp.diagnoses_icd"
    )

    for edge in node.outgoing:

        print(edge.relationship)

        print(edge.target)

        print(edge.confidence)

if __name__ == "__main__":
    main()

