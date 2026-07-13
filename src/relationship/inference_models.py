from dataclasses import dataclass, field


@dataclass
class RelationshipEvidence:
    """
    Evidence produced by a single inference rule.
    """
    rule: str
    score: float
    explanation: str
    matched_columns: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

@dataclass
class InferredRelationship:
    source: str
    target: str
    confidence: float
    evidence: list[RelationshipEvidence] = field(default_factory=list)