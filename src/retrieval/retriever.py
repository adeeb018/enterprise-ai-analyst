from .semantic_retriever import SemanticRetriever
from .value_retriever import ValueRetriever
from .retrieval_merger import RetrievalMerger


class Retriever:

    def __init__(self):

        self.semantic = SemanticRetriever()

        self.value = ValueRetriever()

        self.merger = RetrievalMerger()

    def retrieve(
        self,
        question: str,
        limit: int = 5,
    ):

        semantic = self.semantic.retrieve(
            question,
            limit,
        )

        value = self.value.retrieve(
            question,
            limit,
        )

        return self.merger.merge(
            semantic,
            value,
        )