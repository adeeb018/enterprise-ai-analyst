import json

from src.config.paths import ENRICHED_SCHEMA_JSON, GRAPH_JSON
from src.graph.graph_enricher import GraphEnricher
from src.graph.graph_exporter import GraphExporter
from src.graph.schema_graph import SchemaGraph
from src.ingestion.schema_models import TableInfo
from src.relationship.inference_engine import RelationshipInferenceEngine
from src.relationship.relationship_index import RelationshipIndex


class GraphProcessor:

    def process(self):

        schema = [
            TableInfo.model_validate(item)
            for item in json.loads(
                ENRICHED_SCHEMA_JSON.read_text()
            )
        ]

        graph = SchemaGraph.build(schema)

        index = RelationshipIndex()

        index.build(graph)

        relationships = RelationshipInferenceEngine().infer_relationships(
            graph,
            index,
        )

        graph = GraphEnricher().enrich(
            graph,
            relationships,
        )

        GraphExporter().export(
            graph,
            GRAPH_JSON,
        )