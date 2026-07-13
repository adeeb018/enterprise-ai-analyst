from operator import index
from pathlib import Path
import json

from sqlalchemy import table

from src import graph
from src.config.paths import SCHEMA_JSON
from src.ingestion.schema_models import TableInfo
from src.graph.schema_graph import SchemaGraph
from src.relationship.relationship_index import RelationshipIndex
from src.relationship.inference_engine import (
    RelationshipInferenceEngine,
)

schema_path = SCHEMA_JSON

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

    # print_neighbors(
    #     graph,
    #     "mimiciv_hosp.admissions"
    # )
    # print_neighbors(
    #     graph,
    #     "mimiciv_hosp.patients"
    # )
    # print_neighbors(
    #     graph,
    #     "mimiciv_hosp.diagnoses_icd"
    # )
    # print_neighbors(
    #     graph,
    #     "mimiciv_hosp.labevents"
    # )

    # graph.print_tree(
    #     "mimiciv_hosp.diagnoses_icd",
    #     hops=2,
    # )

    index = RelationshipIndex()
    index.build(graph)

    engine = RelationshipInferenceEngine()

    relationships = engine.infer_relationships(
        graph,
        index,
    )

    print("=" * 60)
    print("INFERRED RELATIONSHIPS")
    print("=" * 60)

    for relationship in relationships:

        if relationship.source != "mimiciv_hosp.diagnoses_icd":
            continue

        print()

        print(
            f"{relationship.source}"
        )

        print("    ↓")

        print(
            f"{relationship.target}"
        )

        print(
            f"Confidence : {relationship.confidence}"
        )

        print("Evidence")

        for evidence in relationship.evidence:

            print(
                f"  - {evidence.rule}"
                f" ({evidence.score})"
            )

            print(
                f"      {evidence.explanation}"
            )

            if evidence.matched_columns:

                print(
                    f"      {', '.join(evidence.matched_columns)}"
                )

    # expanded = graph.expand(
    #     [
    #         "mimiciv_hosp.admissions",
    #     ],
    #     hops=3,
    # )

    # print("=" * 60)
    # print("EXPANSION")
    # print("=" * 60)

    # for item in expanded:

    #     print(
    #         f"{item.distance} | {item.node.id}"
    #     )

    #     if item.parent:
    #         print(
    #             f"    Parent : {item.parent}"
    #         )

    #     if item.via_edge:

    #         edge = item.via_edge

    #         print(
    #             "    Join   : "
    #             f"{edge.source}.{edge.source_column}"
    #             f" -> "
    #             f"{edge.target}.{edge.target_column}"
    #         )

    #         print(item.node.id)

    #         print(item.via_edge)

    # print("=" * 60)
    # print("GRAPH SUMMARY")
    # print("=" * 60)

    # print(f"Nodes : {len(graph.nodes)}")

    # edge_count = sum(
    #     len(node.outgoing)
    #     for node in graph.nodes.values()
    # )

    # print(f"Edges : {edge_count}")
    # node = graph.nodes["mimiciv_hosp.diagnoses_icd"]

    # print("=" * 60)
    # print(node.id)

    # print("\nOutgoing")

    # for edge in node.outgoing:

    #     print(
    #         f"{edge.source_column}"
    #         f" --> "
    #         f"{edge.target}"
    #         f".{edge.target_column}"
    #     )

    # print("\nIncoming")

    # for edge in node.incoming:

    #     print(
    #         f"{edge.source}"
    #         f".{edge.source_column}"
    #         f" --> "
    #         f"{edge.target_column}"
    #     )

if __name__ == "__main__":
    main()

