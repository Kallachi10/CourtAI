from models import CaseData, Witness, Evidence, Clue, LegalRule, CaseObjective

CASE_DATABASE = {
    "case_001": CaseData(
        case_id="case_001",
        title="The Missing Necklace",
        description="A priceless diamond necklace worth $500,000 vanished during a high-society gala at the Grand Plaza Hotel. The defendant, Carlos Rivera, a renowned caterer, is accused of theft. The necklace was last seen in a display case at 8:30 PM, and the theft was discovered at 9:15 PM.",
        charges=["Grand Larceny"],
        witnesses=[
            Witness(
                name="Alice Monroe",
                role="Event Hostess",
                personality="nervous but mostly honest, wants to help",
                testimony=[
                    "I saw Carlos near the display case around 8:45 PM, just before the necklace disappeared.",
                    "There was a commotion in the kitchen around 8:50 PM - I heard loud voices.",
                    "The security guard was away from his post for about 10 minutes during that time."
                ],
                credibility=0.8,
                is_hostile=False,
                key_information=[
                    "Carlos was near the display case at the right time",
                    "Security guard was absent during the theft window",
                    "Kitchen commotion provides alibi opportunity"
                ],
                weaknesses=[
                    "Didn't actually see Carlos take the necklace",
                    "Timeline is somewhat vague",
                    "Could be mistaken about the time"
                ]
            ),
            Witness(
                name="Carlos Rivera",
                role="Caterer (Defendant)",
                personality="confident, defensive, slightly nervous",
                testimony=[
                    "I was preparing dessert in the kitchen from 8:30 to 9:00 PM. I never went near the necklace.",
                    "The kitchen staff can confirm I was there the whole time.",
                    "Anyone could have entered the room during the chaos - the door was unlocked."
                ],
                credibility=0.7,
                is_hostile=True,
                key_information=[
                    "Claims to have kitchen staff alibi",
                    "Points out unlocked door as opportunity for others",
                    "Provides specific timeline"
                ],
                weaknesses=[
                    "No independent verification of alibi",
                    "Defensive attitude might suggest guilt",
                    "Timeline could be fabricated"
                ]
            ),
            Witness(
                name="Detective Sarah Lin",
                role="Lead Investigator",
                personality="methodical, cooperative, thorough",
                testimony=[
                    "The security footage has a 10-minute gap from 8:40 to 8:50 PM - the cameras malfunctioned.",
                    "No fingerprints were found on the display case or the necklace box.",
                    "The glove found near the kitchen entrance is size 9, but Carlos wears size 11.",
                    "A guest, Mr. Thompson, was seen hurrying out of the building at 8:55 PM."
                ],
                credibility=0.9,
                is_hostile=False,
                key_information=[
                    "Security footage gap creates reasonable doubt",
                    "No fingerprints on evidence",
                    "Glove size doesn't match defendant",
                    "Suspicious guest left at right time"
                ],
                weaknesses=[
                    "Cannot definitively prove who took the necklace",
                    "Evidence is circumstantial"
                ]
            )
        ],
        evidence=[
            Evidence(
                id="E1",
                name="CCTV Footage",
                description="Security camera footage showing the display case area. The footage has a 10-minute gap from 8:40-8:50 PM due to a technical malfunction. Before and after the gap, the area appears normal.",
                relevance=0.9,
                admissibility=True,
                presented=False,
                category="physical",
                clue_hint="The missing footage creates reasonable doubt - someone could have taken the necklace during those 10 minutes without being recorded.",
                points_value=15
            ),
            Evidence(
                id="E2",
                name="Mystery Glove",
                description="A single black leather glove found near the kitchen entrance. The glove is size 9, but Carlos Rivera wears size 11. No fingerprints were found on the glove.",
                relevance=0.8,
                admissibility=True,
                presented=False,
                category="physical",
                clue_hint="The glove size mismatch suggests the thief was not Carlos, but someone else with smaller hands.",
                points_value=20
            ),
            Evidence(
                id="E3",
                name="Guest List & Exit Log",
                description="Complete list of guests and the hotel's exit log. Mr. James Thompson, a guest, was recorded leaving the building at 8:55 PM, just 5 minutes after the theft window.",
                relevance=0.7,
                admissibility=True,
                presented=False,
                category="documentary",
                clue_hint="Mr. Thompson's hasty exit at the perfect time makes him a prime suspect. He could have taken the necklace during the camera blackout.",
                points_value=25
            ),
            Evidence(
                id="E4",
                name="Kitchen Staff Statements",
                description="Statements from kitchen staff members. Two staff members confirm Carlos was in the kitchen from 8:30-9:00 PM, but their statements are somewhat inconsistent about exact times.",
                relevance=0.6,
                admissibility=True,
                presented=False,
                category="testimonial",
                clue_hint="While the staff provides an alibi, the inconsistencies in their timing could be exploited to create doubt about Carlos's whereabouts.",
                points_value=10
            )
        ],
        clues=[
            Clue(
                id="C1",
                description="The kitchen door was left unlocked during the entire event, providing easy access for anyone to enter and exit without being noticed.",
                discovered=False,
                relevance_score=0.8,
                category="opportunity",
                points_value=15
            ),
            Clue(
                id="C2",
                description="Mr. Thompson, a guest, was seen hurrying out of the building at 8:55 PM, just 5 minutes after the theft window ended. He was carrying a large bag.",
                discovered=False,
                relevance_score=0.9,
                category="timeline",
                points_value=25
            ),
            Clue(
                id="C3",
                description="The glove found near the kitchen entrance is size 9, but Carlos wears size 11. This physical evidence suggests the thief was someone else.",
                discovered=False,
                relevance_score=0.9,
                category="alibi",
                points_value=20
            ),
            Clue(
                id="C4",
                description="The security guard was away from his post for exactly 10 minutes during the theft window, creating the perfect opportunity for the crime.",
                discovered=False,
                relevance_score=0.7,
                category="opportunity",
                points_value=15
            )
        ],
        legal_rules=[
            LegalRule(
                id="L1",
                name="Burden of Proof",
                description="The prosecution must prove the defendant's guilt beyond a reasonable doubt. Any reasonable doubt must result in acquittal.",
                category="procedure",
                relevance_score=1.0
            ),
            LegalRule(
                id="L2",
                name="Admissibility of Evidence",
                description="Evidence must be relevant and properly authenticated to be admissible. Physical evidence must be properly handled and documented.",
                category="evidence",
                relevance_score=0.9
            ),
            LegalRule(
                id="L3",
                name="Reasonable Doubt",
                description="If there are multiple possible explanations for the evidence, and one suggests innocence, the defendant must be acquitted.",
                category="procedure",
                relevance_score=0.95
            )
        ],
        background="A high-profile theft at a glamorous event with multiple suspects and circumstantial evidence. The case hinges on timing, opportunity, and reasonable doubt.",
        difficulty="medium",
        objective=CaseObjective(
            title="Defend Carlos Rivera",
            description="You are the defense attorney for Carlos Rivera. Your task is to create reasonable doubt about his guilt and prove that someone else could have committed the theft.",
            lawyer_task="Demonstrate that Carlos Rivera is innocent by: 1) Establishing his alibi, 2) Showing others had opportunity, 3) Creating reasonable doubt about the evidence",
            win_conditions=[
                "Score at least 80 points",
                "Discover at least 3 clues",
                "Present at least 2 pieces of evidence",
                "Question at least 2 witnesses"
            ],
            max_steps=8,
            target_score=80
        )
    )
} 