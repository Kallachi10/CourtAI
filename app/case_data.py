from models import CaseData, Witness, Evidence, Clue, LegalRule

CASE_DATABASE = {
    "case_001": CaseData(
        case_id="case_001",
        title="The Missing Necklace",
        description="A priceless necklace vanished during a high-society gala. The defendant, a renowned caterer, is accused of theft.",
        charges=["Grand Larceny"],
        witnesses=[
            Witness(
                name="Alice Monroe",
                role="Hostess",
                personality="nervous but mostly honest",
                testimony=[
                    "I saw the defendant near the display case just before the necklace disappeared.",
                    "There was a commotion in the kitchen around the same time."
                ],
                credibility=0.8,
                is_hostile=False
            ),
            Witness(
                name="Carlos Rivera",
                role="Caterer (Defendant)",
                personality="confident, defensive",
                testimony=[
                    "I was preparing dessert in the kitchen. I never went near the necklace.",
                    "Anyone could have entered the room during the chaos."
                ],
                credibility=0.7,
                is_hostile=True
            ),
            Witness(
                name="Detective Lin",
                role="Lead Investigator",
                personality="methodical, cooperative",
                testimony=[
                    "The security footage has a 10-minute gap during the time of the theft.",
                    "No fingerprints were found on the display case."
                ],
                credibility=0.9,
                is_hostile=False
            )
        ],
        evidence=[
            Evidence(
                id="E1",
                name="CCTV Footage",
                description="Security camera footage with a 10-minute gap.",
                relevance=0.9,
                admissibility=True,
                presented=False,
                category="physical"
            ),
            Evidence(
                id="E2",
                name="Glove",
                description="A single glove found near the kitchen entrance.",
                relevance=0.7,
                admissibility=True,
                presented=False,
                category="physical"
            ),
            Evidence(
                id="E3",
                name="Guest List",
                description="List of all guests present at the gala.",
                relevance=0.5,
                admissibility=True,
                presented=False,
                category="documentary"
            )
        ],
        clues=[
            Clue(
                id="C1",
                description="The kitchen door was left unlocked during the event.",
                discovered=False,
                relevance_score=0.8,
                category="opportunity"
            ),
            Clue(
                id="C2",
                description="A guest was seen hurrying out just before the theft was discovered.",
                discovered=False,
                relevance_score=0.7,
                category="timeline"
            ),
            Clue(
                id="C3",
                description="The glove does not match the defendant's hand size.",
                discovered=False,
                relevance_score=0.9,
                category="alibi"
            )
        ],
        legal_rules=[
            LegalRule(
                id="L1",
                name="Burden of Proof",
                description="The prosecution must prove the defendant's guilt beyond a reasonable doubt.",
                category="procedure",
                relevance_score=1.0
            ),
            LegalRule(
                id="L2",
                name="Admissibility of Evidence",
                description="Evidence must be relevant and properly authenticated to be admissible.",
                category="evidence",
                relevance_score=0.9
            )
        ],
        background="A high-profile theft at a glamorous event. Multiple suspects and a missing necklace.",
        difficulty="medium"
    )
} 