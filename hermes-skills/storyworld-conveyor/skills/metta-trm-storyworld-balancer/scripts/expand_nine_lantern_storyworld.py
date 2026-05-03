#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from copy import deepcopy
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[5]
STORY_SCRIPTS = REPO_ROOT / "codex-skills" / "storyworld-building" / "scripts"
CONVEYOR_SCRIPTS = REPO_ROOT / "hermes-skills" / "storyworld-conveyor" / "scripts"
DEFAULT_SOURCE = REPO_ROOT / "hermes-skills" / "storyworld-conveyor" / "working_worlds" / "nine_lantern_27b_lattice_mc_tuned" / "nine_lantern_27b_lattice_mc_tuned.json"
DEFAULT_OUT = REPO_ROOT / "hermes-skills" / "storyworld-conveyor" / "working_worlds" / "nine_lantern_expanded_kalam_exam"


VARS = ["Veil_Disclosure", "Solitude_Consensus", "Discord_Ijma", "Letter_Spirit"]
CHARS = ["char_witness", "char_diplomat", "char_magician", "char_corpse"]


SCENES: list[dict[str, Any]] = [
    {
        "id": "page_001_gate_of_translation",
        "title": "The Gate of Translation",
        "act": "act1",
        "body": "Yusuf Lin reaches the court-school before dawn with a travel-stained certificate, a dictionary copied by hand, and three names folded into one sleeve. The porter reads his Arabic slowly, then asks for the Chinese name his family used before conversion. Examiner Safiya al-Qanun waits behind a screen, listening for panic. Master Ilyas turns an unlit lantern in his palm. The first question is not doctrine. It is whether a man can translate himself without becoming false evidence.",
        "theme": "identity and legal language",
        "options": [
            ("procedure", "Present the certificate and ask Safiya to verify each witness."),
            ("reason", "Translate your own name as an argument about intention."),
            ("precedent", "Recite the older conversion forms exactly as copied."),
        ],
        "secret": ("witness", "Notice who benefits from asking the name twice."),
    },
    {
        "id": "page_002_wudu_ledger",
        "title": "The Wudu Ledger",
        "act": "act1",
        "body": "In the ablution court, a ledger records who washed, who watched, and who corrected whom. A poor water carrier has been accused of invalidating the students' preparation by touching the basin after a long night in the market. The rule looks simple until Yusuf sees the carrier's hands: ink from court summons, not grime. Safiya asks for a ruling that the school can enforce. Ilyas asks whether purity without mercy is only another stain.",
        "theme": "procedure, mercy, and public order",
        "options": [
            ("procedure", "Separate ritual validity from the carrier's legal dignity."),
            ("mercy", "Treat public humiliation as the impurity needing repair."),
            ("precedent", "Apply the basin rule without naming the carrier's poverty."),
        ],
    },
    {
        "id": "page_003_tawhid_diagram",
        "title": "The Diagram of Unity",
        "act": "act1",
        "body": "A chalk diagram fills the wall: circles for attributes, a line for speech, a blank center marked tawhid. The students whisper that a foreign convert should avoid this question and answer only what has been transmitted. Safiya points to the blank center. Ilyas lights one lantern and asks why one flame casts many shadows. Yusuf must explain divine unity without turning God into arithmetic or letting rhetoric dissolve every useful distinction.",
        "theme": "tawhid and divine attributes",
        "options": [
            ("reason", "Argue that unity governs attributes without erasing meaning."),
            ("transmission", "Quote the safest formula and refuse further division."),
            ("community", "Ask the class which distinction preserves worship."),
        ],
        "secret": ("witness", "Mark that every answer reveals the examiner's unity too."),
    },
    {
        "id": "page_004_treaty_room",
        "title": "The Treaty Room",
        "act": "act1",
        "body": "Safiya places a blood-spotted treaty beside a murder scroll. The dead envoy brokered peace by telling each faction a different true thing at a different time. If Yusuf condemns him, the treaty may collapse. If he excuses him, testimony becomes theater. Master Ilyas hangs the unlit lantern over the scroll and calls the arrangement beautiful. Safiya calls it dangerous. The examination wants a frame before it allows a verdict.",
        "theme": "truth staging and public peace",
        "options": [
            ("procedure", "Reconstruct the treaty sequence before assigning moral blame."),
            ("disclosure", "Name staged truth as a legal hazard to the city."),
            ("symbol", "Treat the murder as theater designed to preserve peace."),
        ],
    },
    {
        "id": "page_005_testimony_broker",
        "title": "The Silk Broker's Testimony",
        "act": "act1",
        "body": "A silk broker testifies through an interpreter who keeps smoothing the sharp edges from his speech. The broker saw the envoy meet a soldier, a widow, and a judge's clerk, but his dates use a market calendar Yusuf learned as a child. The room waits for Safiya's official translator. Yusuf hears the older rhythm underneath. If he speaks, he risks looking partial. If he stays silent, the testimony becomes clean and wrong.",
        "theme": "testimony, translation, and legitimacy",
        "options": [
            ("procedure", "Ask for both calendars to be entered into evidence."),
            ("identity", "Admit you understand the broker's market idiom directly."),
            ("consensus", "Let the official translator finish before correcting him."),
        ],
    },
    {
        "id": "page_006_created_recitation",
        "title": "The Created Recitation",
        "act": "act1",
        "body": "The second lantern burns beside a recitation slate. Safiya asks whether the spoken syllables before Yusuf are created, while the boys in the back wait to see if he will stumble into scandal. Ilyas offers a gentler trap: call the voice eternal and watch the school applaud. Yusuf knows the doctrine is not a slogan here. A qadi must decide what kind of speech can enter evidence, bind a vow, or break a life.",
        "theme": "createdness of recited speech",
        "options": [
            ("reason", "Distinguish eternal meaning from created courtroom utterance."),
            ("transmission", "Refuse the trap and cite the accepted school formula."),
            ("mercy", "Ask what harm the question is being used to do."),
        ],
        "secret": ("witness", "Ask why the examiner needs your fear on record."),
    },
    {
        "id": "page_007_scales_of_adl",
        "title": "The Scales of Adl",
        "act": "act2",
        "body": "In the hall of weights, three scales hang from one beam. One carries a child's broken cup, one a soldier's order, and one an unsigned decree. Safiya names the doctrine of divine justice and asks whether a ruler may punish obedience when the order itself was corrupt. Ilyas says the scales will balance if Yusuf stops touching them. The question is not only about God. It is about whether law can blame a hand for a command.",
        "theme": "divine justice and human blame",
        "options": [
            ("justice", "Hold command and obedience apart until intention is tested."),
            ("order", "Protect public order by making the soldier answer first."),
            ("mercy", "Start with the child harmed by the lawful command."),
        ],
    },
    {
        "id": "page_008_qadar_courtyard",
        "title": "The Qadar Courtyard",
        "act": "act2",
        "body": "A prisoner kneels in the courtyard claiming that decree moved his hand before theft did. The crowd laughs because fatalism is easier to punish than hunger. Safiya asks Yusuf to separate qadar from excuse without pretending freedom is simple. Ilyas scatters date stones across the tiles, each landing like an event that could have been otherwise. The prisoner watches Yusuf more closely than the examiners do.",
        "theme": "qadar, free will, and responsibility",
        "options": [
            ("justice", "Treat decree as context, not acquittal."),
            ("mercy", "Investigate hunger before naming the will corrupt."),
            ("precedent", "Apply theft doctrine and leave metaphysics outside sentencing."),
        ],
        "secret": ("witness", "Observe that the prisoner studies your freedom as evidence."),
    },
    {
        "id": "page_009_widow_deposition",
        "title": "The Widow's Deposition",
        "act": "act2",
        "body": "The envoy's widow refuses the women's screen and stands in the open court. She admits she burned one letter, kept another, and lied to protect a child who is not hers. Safiya's clerks begin sorting the confession into admissible and inadmissible parts. Ilyas listens for the unburned letter in her breathing. Yusuf must decide whether broken testimony becomes useless, or whether a fractured witness can still carry a true burden.",
        "theme": "partial truth and witness repair",
        "options": [
            ("procedure", "Record each admitted lie before accepting any claim."),
            ("mercy", "Protect the child first and return to the letter later."),
            ("disclosure", "Ask what truth the burned letter was meant to hide."),
        ],
    },
    {
        "id": "page_010_corpse_testimony",
        "title": "The Sleeping Precedent Speaks",
        "act": "act2",
        "body": "The corpse does not speak in words but in angles. The blade entered at a slant that suggests retreat, yet the wound depth claims pursuit. Yusuf feels the weight of precedent pressing against his ribs: not dead matter, but sleeping law waiting to be invoked. Safiya watches without blinking. Ilyas's lanterns cast shadows that move when no one approaches them. Formula demands measurement; testimony requires a living witness; purpose asks what the dead still need from the living.",
        "theme": "precedent, evidence, and purpose",
        "options": [
            ("procedure", "Demand sequence, motive, angle, and instrument in order."),
            ("purpose", "Ask what kind of judgment lets the dead rest."),
            ("precedent", "Let the old rule speak before the living improvise."),
        ],
    },
    {
        "id": "page_011_missing_seat",
        "title": "The Empty Ninth Seat",
        "act": "act2",
        "body": "Eight lanterns burn above the tribunal. The ninth hangs dark, its chain swaying though no wind touches it. Safiya says the missing seat is not an oversight. Ilyas watches Yusuf's face for the moment he invents an unseen master to complete the pattern. The examination was never about filling chairs. It asks whether absence can be evidence, authority, conspiracy, or honest uncertainty.",
        "theme": "hidden authority and witness relation",
        "options": [
            ("symbol", "Name the missing seat as the arranger behind the case."),
            ("procedure", "Refuse hidden authority and judge from admitted evidence."),
            ("community", "Ask who is excluded when the court calls itself complete."),
        ],
        "secret": ("witness", "Write that the empty seat is watching the judge."),
    },
    {
        "id": "page_012_market_riot",
        "title": "The Market Riot",
        "act": "act2",
        "body": "Outside the school, rumor turns the examination into a riot. Some claim Yusuf will free the envoy's killer because foreigners protect foreigners. Others claim Safiya needs a public conviction before sunset. A boy throws a stone and misses the window. The court can close its doors, stage a calming announcement, or let the crowd hear dangerous complexity. Yusuf learns that public order is never outside the law; it is one of law's hungriest clients.",
        "theme": "public order and disclosure",
        "options": [
            ("order", "Let Safiya issue a narrow calming statement."),
            ("disclosure", "Tell the crowd what remains genuinely uncertain."),
            ("mercy", "Bring the injured stone-thrower inside as witness."),
        ],
    },
    {
        "id": "page_013_archive_of_jurists",
        "title": "The Archive of Jurists",
        "act": "act3",
        "body": "The archive smells of dust, lamp oil, and victorious arguments. Safiya gives Yusuf three opinions that all cite the same jurist toward incompatible ends. Ilyas says dead scholars are easiest to ventriloquize because they no longer object. The Sleeping Precedent rests open on a stand, daring Yusuf to confuse inheritance with obedience. A qadi must receive the dead without making them govern every living wound.",
        "theme": "inherited authority and legal reasoning",
        "options": [
            ("precedent", "Rank the opinions by closeness to the original wound."),
            ("reason", "Extract a principle rather than a winning quotation."),
            ("community", "Ask which precedent the city can still understand."),
        ],
    },
    {
        "id": "page_014_dream_deposition",
        "title": "The Dream Deposition",
        "act": "act3",
        "body": "A caravan guard swears he dreamed the envoy pointing toward the killer. Half the room wants to laugh; the other half wants the dream because it simplifies everything. Safiya asks whether dreams can guide investigation without becoming evidence. Ilyas insists the sleeping mind is only another witness with poor manners. Yusuf remembers nights when language arrived first as image, then as law, then as fear.",
        "theme": "imagination and evidentiary limits",
        "options": [
            ("procedure", "Use the dream only to seek ordinary corroboration."),
            ("symbol", "Treat the dream as a map of the court's desire."),
            ("reason", "Explain why meaning is not the same as proof."),
        ],
    },
    {
        "id": "page_015_safiya_sealed_memo",
        "title": "Safiya's Sealed Memo",
        "act": "act3",
        "body": "Safiya leaves a sealed memo where Yusuf can find it, then pretends not to notice. The outside of the paper names three political consequences of each verdict. Opening it would reveal pressure that should not govern the law but already does. Leaving it sealed preserves innocence that may be false. Ilyas says every unopened letter is a little idol. Yusuf has to decide whether administrative knowledge corrupts judgment or makes it accountable.",
        "theme": "political pressure and administrative law",
        "options": [
            ("procedure", "Enter the memo into the record before reading it."),
            ("veil", "Leave it sealed and judge only the admitted case."),
            ("disclosure", "Read it aloud and make pressure answerable."),
        ],
        "secret": ("witness", "Note that Safiya is testing what you do unwatched."),
    },
    {
        "id": "page_016_ilyas_theater",
        "title": "Ilyas's Theater of Law",
        "act": "act3",
        "body": "Ilyas transforms the classroom into the murder scene with chalk, cloth, and students moving as witnesses. The performance makes contradictions visible that the ledger flattened. It also makes the audience love the version that is easiest to stage. Safiya permits the exercise because Yusuf must learn how demonstration can reveal and seduce at once. The lanterns throw enormous shadows. For a moment the law seems truer when it admits it is theater.",
        "theme": "symbolic demonstration and seduction",
        "options": [
            ("symbol", "Use the performance to reveal hidden relations."),
            ("procedure", "Separate theatrical insight from admissible fact."),
            ("mercy", "Ask which actor the crowd wants punished most."),
        ],
    },
    {
        "id": "page_017_trial_of_scribe",
        "title": "The Trial of the Scribe",
        "act": "act3",
        "body": "A scribe confesses to changing one word in the treaty. The changed word prevented immediate war, then made the later murder almost inevitable. He insists he preserved the spirit by betraying the letter. Safiya asks whether correct doctrine can excuse forged procedure. Ilyas asks whether a city saved by a lie owes the liar gratitude or punishment. Yusuf sees his own translations waiting inside the accusation.",
        "theme": "letter, spirit, and forgery",
        "options": [
            ("justice", "Punish the forgery while preserving what truth it saved."),
            ("letter", "Let corrupted procedure invalidate the treaty's authority."),
            ("spirit", "Treat the saved lives as evidence for mitigation."),
        ],
    },
    {
        "id": "page_018_exile_caravan",
        "title": "The Exile Caravan",
        "act": "act3",
        "body": "At dusk, a caravan prepares to leave with families who speak Yusuf's childhood language. They ask whether the new qadi will remember them when court Arabic turns their grief into mistakes. Safiya says a judge cannot be advocate for his own people. Ilyas says every judge advocates for the world that made his metaphors. Yusuf must decide whether distance proves fairness, or whether pretending to have no origin is just another false oath.",
        "theme": "identity, legitimacy, and impartiality",
        "options": [
            ("procedure", "Promise equal process, not special rescue."),
            ("identity", "Admit origin openly so bias can be watched."),
            ("mercy", "Create a translation rule for future litigants."),
        ],
        "secret": ("witness", "Ask them what kind of judge they think you became."),
    },
    {
        "id": "page_019_night_of_ledger",
        "title": "The Night Ledger",
        "act": "act3",
        "body": "Before the verdict, Yusuf sits alone with every note he was not supposed to connect: the repeated name, the unlit lantern, the created utterance, the prisoner's gaze, Safiya's planted memo, the caravan's question. The ledger no longer looks like a record of others. It looks like a record of what judgment has made visible in him. The final exam may not be asking what law says. It may be asking who is changed enough to say it.",
        "theme": "clue convergence and self-witness",
        "options": [
            ("procedure", "Organize the notes into admissible and inadmissible columns."),
            ("reason", "Trace which choices changed the judge, not only the case."),
            ("community", "Imagine the verdict as instruction to the city."),
        ],
    },
    {
        "id": "page_020_verdict_lattice",
        "title": "The Verdict Lattice",
        "act": "act3",
        "body": "At the last session, the lanterns descend until their chains ring beside Yusuf's ears. Each flame now carries one route through the case: public consensus, dangerous symbol, dead precedent, living witness, shared fault, civic amnesia, or refusal of the frame. Safiya asks for a verdict. Ilyas asks for a story people will obey. The Sleeping Precedent waits for its old office. Yusuf hears the deeper question: what sort of reasons may rule a city after this judgment exists?",
        "theme": "final lattice choice",
        "options": [],
    },
]


ENDING_TEXT = {
    "page_end_diplomat_state": (
        "The Narrow Light",
        "Safiya accepts Yusuf's verdict and files it through the ministry before rumor can eat it. The city receives order, not revelation: reparations, sealed names, public calm, and a new rule for multilingual testimony. Yusuf becomes a qadi the state can use. He knows the judgment saved lives by narrowing truth until it fit inside procedure.",
    ),
    "page_end_magician_legend": (
        "The Lantern That Burned Cold",
        "Ilyas carries the verdict into story before the clerks finish writing. Students will repeat how Yusuf made law visible through dread, and the market will obey because the tale is easier than the record. The murder becomes a ritual warning. Yusuf passes, but his court inherits a dangerous gift: justice that works by frightening imagination.",
    ),
    "page_end_corpse_reenthroned": (
        "The Precedent Returns",
        "The Sleeping Precedent is returned to office with new seals and old authority. Yusuf passes by admitting that the dead sometimes protect the living from fashionable mercy. Yet the old rule hardens as soon as it touches power. The treaty survives, the widow is contained, and future judges learn to call inheritance humility.",
    ),
    "page_end_witness_mask": (
        "The Human Measure",
        "Yusuf names the witness relation but stops short of claiming the missing seat. Safiya records the answer as competent and dangerous. The court accepts that every judgment changes the judge who utters it, then builds a procedure for watching that change. Yusuf becomes a qadi under supervision, neither free nor false.",
    ),
    "page_end_shared_fault": (
        "The Fracture That Held",
        "No faction receives innocence. Yusuf distributes fault among envoy, clerk, court, crowd, and treaty-makers, forcing the city to preserve contradiction in public law. Safiya dislikes the administrative burden; Ilyas admires the wound left open. The verdict becomes a difficult curriculum: disagreement can serve justice when it is made answerable.",
    ),
    "page_end_city_forgets": (
        "The Amnesty of Silence",
        "The city chooses peace by forgetting the clean shape of guilt. Records are sealed, the crowd disperses, and the treaty survives under a careful lie. Yusuf passes quietly because quiet is what the hour required. Years later, he will still know which mercy was real and which was only exhaustion dressed as law.",
    ),
    "page_end_outside_causality": (
        "The Court Beyond",
        "Yusuf refuses the exam's frame and leaves without certificate or condemnation. In the market quarter he begins hearing cases no school wanted: translators, carriers, widows, caravan children, men with two names. The tribunal calls him unfinished. The city calls him useful. His law does not defeat the old court; it creates a place outside its appetite.",
    ),
    "page_end_ninth_lantern_secret": (
        "Secret Ending: The Ninth Lantern Sits",
        "Yusuf does not solve the examination. He identifies its hidden instrument: the court was measuring how judgment arranges the witness who dares to judge. He lights the ninth lantern from his own corrected ledger, then requires Safiya and Ilyas to enter their pressures as testimony. The qadi is appointed only after the court becomes evidence too.",
    ),
}


OPTION_PROFILES = {
    "procedure": {"primary": "Solitude_Consensus", "secondary": "Veil_Disclosure", "tertiary": "Letter_Spirit", "deltas": [0.04, -0.02, 0.03]},
    "reason": {"primary": "Letter_Spirit", "secondary": "Discord_Ijma", "tertiary": "Veil_Disclosure", "deltas": [0.05, 0.03, 0.02]},
    "precedent": {"primary": "Letter_Spirit", "secondary": "Solitude_Consensus", "tertiary": "Veil_Disclosure", "deltas": [-0.04, 0.03, -0.02]},
    "transmission": {"primary": "Letter_Spirit", "secondary": "Solitude_Consensus", "tertiary": "Discord_Ijma", "deltas": [-0.03, 0.04, -0.02]},
    "community": {"primary": "Solitude_Consensus", "secondary": "Discord_Ijma", "tertiary": "Veil_Disclosure", "deltas": [0.05, 0.04, 0.02]},
    "consensus": {"primary": "Solitude_Consensus", "secondary": "Discord_Ijma", "tertiary": "Veil_Disclosure", "deltas": [0.05, 0.04, 0.02]},
    "mercy": {"primary": "Veil_Disclosure", "secondary": "Solitude_Consensus", "tertiary": "Letter_Spirit", "deltas": [0.03, 0.03, 0.04]},
    "justice": {"primary": "Discord_Ijma", "secondary": "Letter_Spirit", "tertiary": "Solitude_Consensus", "deltas": [0.04, 0.03, 0.02]},
    "order": {"primary": "Solitude_Consensus", "secondary": "Veil_Disclosure", "tertiary": "Discord_Ijma", "deltas": [0.04, -0.03, -0.02]},
    "disclosure": {"primary": "Veil_Disclosure", "secondary": "Discord_Ijma", "tertiary": "Letter_Spirit", "deltas": [0.06, 0.02, 0.03]},
    "symbol": {"primary": "Veil_Disclosure", "secondary": "Letter_Spirit", "tertiary": "Discord_Ijma", "deltas": [-0.04, 0.05, 0.03]},
    "identity": {"primary": "Veil_Disclosure", "secondary": "Solitude_Consensus", "tertiary": "Discord_Ijma", "deltas": [0.05, -0.02, 0.04]},
    "veil": {"primary": "Veil_Disclosure", "secondary": "Solitude_Consensus", "tertiary": "Letter_Spirit", "deltas": [-0.05, 0.02, -0.02]},
    "letter": {"primary": "Letter_Spirit", "secondary": "Discord_Ijma", "tertiary": "Solitude_Consensus", "deltas": [-0.06, -0.02, 0.03]},
    "spirit": {"primary": "Letter_Spirit", "secondary": "Veil_Disclosure", "tertiary": "Discord_Ijma", "deltas": [0.06, 0.02, 0.03]},
    "purpose": {"primary": "Letter_Spirit", "secondary": "Veil_Disclosure", "tertiary": "Discord_Ijma", "deltas": [0.06, 0.02, 0.03]},
    "witness": {"primary": "Veil_Disclosure", "secondary": "Letter_Spirit", "tertiary": "Solitude_Consensus", "deltas": [0.08, 0.07, -0.04]},
}


PROFILE_SURFACES = {
    "procedure": ("administrable procedure", "a rule the clerks can repeat", "the people harmed by neat categories"),
    "reason": ("disciplined reasoning", "a principle stronger than quotation", "the risk of sounding foreign to frightened students"),
    "precedent": ("inherited authority", "continuity with the dead jurists", "mercy trapped inside old wording"),
    "transmission": ("safe transmission", "protection from doctrinal scandal", "the question Safiya planted underneath the formula"),
    "community": ("public intelligibility", "a verdict the city can recognize", "minority grief flattened into consensus"),
    "consensus": ("public intelligibility", "a verdict the city can recognize", "minority grief flattened into consensus"),
    "mercy": ("repair before punishment", "a human face for the rule", "the suspicion that mercy is favoritism"),
    "justice": ("answerable blame", "a way to punish without lying", "the command that made obedience look innocent"),
    "order": ("civic order", "quiet streets before sunset", "truth narrowed until it stops bleeding"),
    "disclosure": ("dangerous disclosure", "pressure forced into the record", "peace made harder by public knowledge"),
    "symbol": ("symbolic demonstration", "a pattern the crowd can feel", "spectacle becoming its own evidence"),
    "identity": ("declared origin", "bias made watchable instead of hidden", "the accusation that Yusuf judges for his own"),
    "veil": ("lawful concealment", "space for peace to survive", "a secret that may rot into policy"),
    "letter": ("literal authority", "a boundary no rhetoric can cross", "living harm left outside the text"),
    "spirit": ("living purpose", "room for law to heal what it names", "procedure weakened by beautiful intention"),
    "purpose": ("living purpose", "room for law to heal what it names", "procedure weakened by beautiful intention"),
    "witness": ("self-witness", "the examiner pulled into evidence", "authority losing the comfort of invisibility"),
}


def now_ts() -> float:
    return float(time.time())


def string_constant(text: str) -> dict[str, Any]:
    return {"pointer_type": "String Constant", "script_element_type": "Pointer", "value": text}


def num_const(value: float) -> dict[str, Any]:
    return {"pointer_type": "Bounded Number Constant", "script_element_type": "Pointer", "value": round(float(value), 4)}


def ptr(char: str, prop: str, *key_extra: str, coeff: float = 1.0) -> dict[str, Any]:
    return {
        "pointer_type": "Bounded Number Pointer",
        "script_element_type": "Pointer",
        "character": char,
        "keyring": [prop, *key_extra],
        "coefficient": round(float(coeff), 4),
    }


def op(operator_type: str, operands: list[Any], subtype: str | None = None) -> dict[str, Any]:
    node = {"operator_type": operator_type, "script_element_type": "Operator", "operands": operands}
    if subtype:
        node["operator_subtype"] = subtype
    return node


def abs_op(node: Any) -> dict[str, Any]:
    return op("Absolute Value", [node])


def cmp_op(subtype: str, left: Any, right: Any) -> dict[str, Any]:
    return op("Arithmetic Comparator", [left, right], subtype)


def nudge(target: dict[str, Any], delta: Any) -> dict[str, Any]:
    return op("Nudge", [deepcopy(target), delta])


def permissive_gate(prop: str) -> dict[str, Any]:
    return cmp_op("Less Than or Equal To", abs_op(ptr("char_witness", prop)), num_const(1.0))


def threshold_gate(prop: str, value: float) -> dict[str, Any]:
    return cmp_op("Greater Than or Equal To", ptr("char_witness", prop), num_const(value))


def encounter_script(index: int, prop: str) -> dict[str, Any]:
    return op(
        "Addition",
        [
            num_const(0.62 + (index % 5) * 0.03),
            ptr("char_witness", prop, coeff=0.65),
            abs_op(ptr("char_witness", VARS[(VARS.index(prop) + 1) % len(VARS)], coeff=0.25)),
        ],
    )


def acceptability(prop: str) -> dict[str, Any]:
    return cmp_op("Less Than or Equal To", abs_op(ptr("char_witness", prop)), num_const(1.0))


def desirability(profile: dict[str, Any], base: float) -> dict[str, Any]:
    primary = profile["primary"]
    secondary = profile["secondary"]
    tertiary = profile["tertiary"]
    return op(
        "Addition",
        [
            num_const(base),
            ptr("char_diplomat", primary, "char_witness", coeff=0.34),
            ptr("char_magician", primary, "char_witness", coeff=0.31),
            ptr("char_diplomat", secondary, "char_witness", "char_magician", coeff=0.28),
            abs_op(ptr("char_witness", tertiary, coeff=0.18)),
        ],
    )


def make_effects(profile: dict[str, Any], reaction_index: int) -> list[dict[str, Any]]:
    primary = profile["primary"]
    secondary = profile["secondary"]
    tertiary = profile["tertiary"]
    d0, d1, d2 = profile["deltas"]
    scale = [1.0, 0.65, -0.45][reaction_index % 3]
    specs = [
        ("char_witness", [primary], d0 * scale, "char_witness", secondary, 0.08),
        ("char_witness", [primary, "char_diplomat"], d0 * 0.65 * scale, "char_witness", primary, 0.10),
        ("char_diplomat", [secondary, "char_witness", "char_magician"], d1 * scale, "char_diplomat", secondary, 0.10),
        ("char_witness", [secondary], d1 * 0.75 * scale, "char_witness", tertiary, 0.08),
        ("char_magician", [tertiary, "char_witness"], d2 * scale, "char_witness", primary, 0.10),
    ]
    effects = []
    for char, keyring, delta, link_char, link_prop, coeff in specs:
        target = ptr(char, keyring[0], *keyring[1:])
        effects.append(
            {
                "effect_type": "Bounded Number Effect",
                "Set": deepcopy(target),
                "to": nudge(target, op("Addition", [num_const(delta), ptr(link_char, link_prop, coeff=coeff)])),
            }
        )
    return effects


def reaction_text(scene: dict[str, Any], option_text: str, profile_name: str, reaction_index: int) -> str:
    doctrine = scene.get("theme") or "the final verdict"
    surface, gain, cost = PROFILE_SURFACES.get(profile_name, PROFILE_SURFACES["procedure"])
    if profile_name == "witness":
        return (
            f"Yusuf keeps the witness relation visible instead of rushing to doctrine. In {doctrine}, this makes the examiner part of the evidence, "
            "and the dark lantern remembers one more step toward being lit."
        )
    if reaction_index == 0:
        return (
            f"Safiya tests the move as {surface}. It gives the court {gain}, but Yusuf sees {cost} waiting just outside the clerk's clean margin."
        )
    if reaction_index == 1:
        return (
            f"Ilyas presses the weak point in the answer: {cost}. The doctrine of {doctrine} stops being abstract because someone must now pay for the distinction."
        )
    return (
        f"The witnesses understand the choice before the scholars finish naming it. To {option_text[0].lower() + option_text[1:]} makes {gain} visible, while {cost} remains unresolved."
    )


def option_visibility(profile_name: str, scene_index: int, is_secret: bool) -> Any:
    if is_secret:
        thresholds = [
            threshold_gate("Veil_Disclosure", min(0.04 + scene_index * 0.004, 0.12)),
            threshold_gate("Letter_Spirit", min(0.02 + scene_index * 0.003, 0.10)),
        ]
        return op("And", thresholds)
    prop = OPTION_PROFILES[profile_name]["primary"]
    return permissive_gate(prop)


def make_option(scene: dict[str, Any], option_index: int, profile_name: str, option_text: str, next_id: str, is_secret: bool) -> dict[str, Any]:
    profile = OPTION_PROFILES[profile_name]
    opt_id = f"{scene['id']}_opt_{profile_name}_{option_index + 1}"
    scene_id_parts = str(scene["id"]).split("_")
    scene_num = int(scene_id_parts[1]) if len(scene_id_parts) > 1 and scene_id_parts[1].isdigit() else 21
    option = {
        "id": opt_id,
        "text_script": string_constant(option_text),
        "visibility_script": option_visibility(profile_name, scene_num, is_secret),
        "performability_script": permissive_gate(profile["secondary"]),
        "reactions": [],
    }
    if is_secret:
        option["secret"] = True
    for rxn_index in range(3):
        option["reactions"].append(
            {
                "id": f"{opt_id}_r{rxn_index + 1}",
                "text_script": string_constant(reaction_text(scene, option_text, profile_name, rxn_index)),
                "desirability_script": desirability(profile, 0.10 + rxn_index * 0.035 + option_index * 0.01),
                "after_effects": make_effects(profile, rxn_index),
                "consequence_id": next_id,
            }
        )
    return option


def make_encounter(scene: dict[str, Any], index: int, next_id: str | None) -> dict[str, Any]:
    prop = VARS[index % len(VARS)]
    enc = {
        "id": scene["id"],
        "title": scene["title"],
        "text_script": string_constant(scene["body"]),
        "acceptability_script": acceptability(prop),
        "desirability_script": encounter_script(index, prop),
        "options": [],
        "connected_spools": ["spool_main", f"spool_{scene['act']}"],
        "earliest_turn": 0,
        "latest_turn": 999,
        "creation_index": index,
        "creation_time": now_ts(),
        "modified_time": now_ts(),
        "graph_position_x": 220 + (index % 5) * 360,
        "graph_position_y": 180 + (index // 5) * 260,
    }
    if next_id:
        for option_index, (profile_name, option_text) in enumerate(scene["options"]):
            enc["options"].append(make_option(scene, option_index, profile_name, option_text, next_id, False))
        if scene.get("secret"):
            profile_name, option_text = scene["secret"]
            enc["options"].append(make_option(scene, len(enc["options"]), profile_name, option_text, next_id, True))
    return enc


def final_visibility(target_id: str) -> Any:
    if target_id == "page_secret_ninth_lantern":
        return op(
            "And",
            [
                cmp_op("Greater Than or Equal To", abs_op(ptr("char_witness", "Veil_Disclosure")), num_const(0.16)),
                cmp_op("Greater Than or Equal To", abs_op(ptr("char_witness", "Letter_Spirit")), num_const(0.10)),
                cmp_op("Less Than or Equal To", abs_op(ptr("char_witness", "Solitude_Consensus")), num_const(0.62)),
            ],
        )
    return permissive_gate(
        {
            "page_end_diplomat_state": "Solitude_Consensus",
            "page_end_magician_legend": "Veil_Disclosure",
            "page_end_corpse_reenthroned": "Letter_Spirit",
            "page_end_witness_mask": "Veil_Disclosure",
            "page_end_shared_fault": "Discord_Ijma",
            "page_end_city_forgets": "Veil_Disclosure",
            "page_end_outside_causality": "Letter_Spirit",
        }.get(target_id, "Discord_Ijma")
    )


def add_final_options(enc: dict[str, Any]) -> None:
    final_options = [
        ("diplomat", "Let Safiya turn the verdict into narrow public policy.", "page_end_diplomat_state"),
        ("magician", "Let Ilyas govern the city through a useful legend.", "page_end_magician_legend"),
        ("corpse", "Return the Sleeping Precedent to its old office.", "page_end_corpse_reenthroned"),
        ("witness", "Name the witness relation without claiming the hidden seat.", "page_end_witness_mask"),
        ("fault", "Distribute fault until contradiction becomes public law.", "page_end_shared_fault"),
        ("forget", "Seal the record and let civic amnesia preserve peace.", "page_end_city_forgets"),
        ("outside", "Reject the exam and open court in the market.", "page_end_outside_causality"),
        ("ninth", "Light the ninth lantern and make the court testify.", "page_secret_ninth_lantern"),
    ]
    profile_lookup = {
        "diplomat": "procedure",
        "magician": "symbol",
        "corpse": "precedent",
        "witness": "witness",
        "fault": "justice",
        "forget": "veil",
        "outside": "identity",
        "ninth": "witness",
    }
    enc["options"] = []
    for index, (slug, text, target) in enumerate(final_options):
        profile_name = profile_lookup[slug]
        option = make_option(enc, index, profile_name, text, target, target.startswith("page_secret_"))
        option["id"] = f"{enc['id']}_opt_{slug}"
        option["visibility_script"] = final_visibility(target)
        for rxn_index, reaction in enumerate(option["reactions"]):
            reaction["id"] = f"{option['id']}_r{rxn_index + 1}"
        enc["options"].append(option)


def make_ending(enc_id: str, index: int) -> dict[str, Any]:
    title, body = ENDING_TEXT[enc_id]
    prop = VARS[index % len(VARS)]
    return {
        "id": enc_id,
        "title": title,
        "text_script": string_constant(body),
        "acceptability_script": acceptability(prop),
        "desirability_script": encounter_script(index + 30, prop),
        "options": [],
        "connected_spools": ["spool_endings"],
        "earliest_turn": 0,
        "latest_turn": 999,
        "creation_index": 100 + index,
        "creation_time": now_ts(),
        "modified_time": now_ts(),
        "graph_position_x": 200 + index * 220,
        "graph_position_y": 1420,
    }


def make_secret_bridge(index: int) -> dict[str, Any]:
    scene = {
        "id": "page_secret_ninth_lantern",
        "title": "The Ninth Lantern Testifies",
        "act": "act3",
        "theme": "secret witness relation",
        "body": (
            "The hidden route opens only if Yusuf has repeatedly noticed that doctrine was watching him back. The ninth lantern descends, unlit, and Safiya finally stops pretending the court is neutral. Ilyas sets down his theater props. The Sleeping Precedent closes itself. This is not yet the ending. It is the secret chamber where Yusuf must decide whether to use the revelation for personal authority, public repair, or institutional confession."
        ),
        "options": [
            ("witness", "Require Safiya and Ilyas to enter their pressures as testimony."),
            ("procedure", "Write a rule for examining the judge before verdict."),
            ("mercy", "Use the revelation to protect future foreign witnesses."),
        ],
    }
    enc = make_encounter(scene, index, "page_end_ninth_lantern_secret")
    enc["connected_spools"] = ["spool_secret"]
    return enc


def build_world(base: dict[str, Any]) -> dict[str, Any]:
    world = deepcopy(base)
    world["IFID"] = "SW-NINE-LANTERN-EXPANDED-KALAM-EXAM"
    world["storyworld_title"] = "The Nine Lantern Examination: Kalam Exam"
    world["about_text"] = string_constant(
        "A longer lattice storyworld in which Yusuf Lin, a Chinese convert and legal apprentice, must pass a Kalam/Qadi examination by navigating doctrine, testimony, public order, identity pressure, and the hidden witness relation inside judgment."
    )
    encounters: list[dict[str, Any]] = []
    for index, scene in enumerate(SCENES):
        next_id = SCENES[index + 1]["id"] if index + 1 < len(SCENES) else None
        enc = make_encounter(scene, index, next_id)
        if scene["id"] == "page_020_verdict_lattice":
            add_final_options(enc)
        encounters.append(enc)
    encounters.append(make_secret_bridge(len(SCENES)))
    ending_ids = list(ENDING_TEXT)
    encounters.extend(make_ending(enc_id, idx) for idx, enc_id in enumerate(ending_ids))
    world["encounters"] = encounters
    act_ids = {act: [scene["id"] for scene in SCENES if scene["act"] == act] for act in ["act1", "act2", "act3"]}
    world["spools"] = [
        {
            "id": "spool_main",
            "spool_name": "The Nine Lantern Kalam Examination",
            "spool_type": "General",
            "starts_active": True,
            "creation_index": 0,
            "creation_time": now_ts(),
            "modified_time": now_ts(),
            "encounters": [scene["id"] for scene in SCENES],
        },
        {
            "id": "spool_act1",
            "spool_name": "Act I: Translation and Doctrine",
            "spool_type": "General",
            "starts_active": False,
            "creation_index": 1,
            "creation_time": now_ts(),
            "modified_time": now_ts(),
            "encounters": act_ids["act1"],
        },
        {
            "id": "spool_act2",
            "spool_name": "Act II: Justice, Freedom, and Testimony",
            "spool_type": "General",
            "starts_active": False,
            "creation_index": 2,
            "creation_time": now_ts(),
            "modified_time": now_ts(),
            "encounters": act_ids["act2"],
        },
        {
            "id": "spool_act3",
            "spool_name": "Act III: Administration, Identity, and Verdict",
            "spool_type": "General",
            "starts_active": False,
            "creation_index": 3,
            "creation_time": now_ts(),
            "modified_time": now_ts(),
            "encounters": act_ids["act3"],
        },
        {
            "id": "spool_endings",
            "spool_name": "Endings",
            "spool_type": "General",
            "starts_active": False,
            "creation_index": 4,
            "creation_time": now_ts(),
            "modified_time": now_ts(),
            "encounters": ending_ids,
        },
        {
            "id": "spool_secret",
            "spool_name": "Secret Route: The Witness/Judge Relation",
            "spool_type": "General",
            "starts_active": False,
            "creation_index": 5,
            "creation_time": now_ts(),
            "modified_time": now_ts(),
            "encounters": ["page_secret_ninth_lantern", "page_end_ninth_lantern_secret"],
        },
    ]
    world["modified_time"] = now_ts()
    world["meta"] = {
        **(world.get("meta") if isinstance(world.get("meta"), dict) else {}),
        "expanded_by": "expand_nine_lantern_storyworld.py",
        "playable_nonterminal_encounters": len(SCENES) + 1,
        "secret_route": {
            "bridge": "page_secret_ninth_lantern",
            "ending": "page_end_ninth_lantern_secret",
            "clue_encounters": [scene["id"] for scene in SCENES if scene.get("secret")],
            "gate": "abs(Veil_Disclosure) >= 0.16 and abs(Letter_Spirit) >= 0.10 with moderate Solitude_Consensus",
        },
    }
    return world


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")


def run_cmd(cmd: list[str], cwd: Path, log_path: Path, timeout: int = 600) -> dict[str, Any]:
    started = time.time()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write("$ " + " ".join(cmd) + "\n\n")
        handle.flush()
        try:
            proc = subprocess.run(cmd, cwd=str(cwd), text=True, stdout=handle, stderr=subprocess.STDOUT, timeout=timeout)
            rc = proc.returncode
        except subprocess.TimeoutExpired:
            handle.write(f"\nTIMEOUT after {timeout}s\n")
            rc = 124
    return {"command": cmd, "returncode": rc, "seconds": round(time.time() - started, 3), "log": str(log_path)}


def parse_mc(text: str) -> dict[str, float]:
    rates: dict[str, float] = {}
    in_dist = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("--- Ending Distribution"):
            in_dist = True
            continue
        if stripped.startswith("---") and in_dist:
            break
        if in_dist and "(" in stripped and "%" in stripped:
            parts = stripped.split()
            if parts:
                eid = parts[0]
                if not eid.startswith("page_"):
                    continue
                pct_raw = stripped.split("(")[1].split("%")[0].strip()
                try:
                    rates[eid] = float(pct_raw) / 100.0
                except ValueError:
                    pass
    return rates


def write_matrix(path: Path) -> None:
    lines = ["# Nine Lantern Expanded Encounter Matrix", ""]
    for index, scene in enumerate(SCENES, start=1):
        lines.append(f"{index}. `{scene['id']}` - {scene['title']} ({scene['act']})")
        lines.append(f"Theme: {scene['theme']}")
        option_text = "; ".join(text for _, text in scene.get("options", []))
        lines.append("Options: " + (option_text if option_text else "final lattice options generated in JSON."))
        if scene.get("secret"):
            lines.append("Secret clue option: " + scene["secret"][1])
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Expand the Nine Lantern storyworld into a denser Kalam/Qadi exam arc.")
    parser.add_argument("--source", default=str(DEFAULT_SOURCE))
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT))
    parser.add_argument("--mc-runs", type=int, default=2000)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    logs = out_dir / "logs"
    source = Path(args.source).resolve()
    base = json.loads(source.read_text(encoding="utf-8-sig"))
    world = build_world(base)
    world_path = out_dir / "nine_lantern_expanded_kalam_exam.json"
    write_json(world_path, world)
    write_matrix(out_dir / "encounter_matrix.md")
    commands = {
        "validator": run_cmd([sys.executable, str(STORY_SCRIPTS / "sweepweave_validator.py"), "validate", str(world_path)], REPO_ROOT, logs / "validator.log"),
        "quality_gate": run_cmd(
            [
                sys.executable,
                str(STORY_SCRIPTS / "storyworld_quality_gate.py"),
                "--storyworld",
                str(world_path),
                "--strict",
                "--report-out",
                str(out_dir / "quality_gate.json"),
            ],
            REPO_ROOT,
            logs / "quality_gate.log",
        ),
        "authoring_score": run_cmd(
            [
                sys.executable,
                str(CONVEYOR_SCRIPTS / "score_storyworld_authoring.py"),
                "--storyworld",
                str(world_path),
                "--repo-root",
                str(REPO_ROOT),
                "--out-json",
                str(out_dir / "authoring_score.json"),
            ],
            REPO_ROOT,
            logs / "authoring_score.log",
        ),
        "monte_carlo": run_cmd(
            [
                sys.executable,
                str(STORY_SCRIPTS / "monte_carlo_rehearsal.py"),
                str(world_path),
                "--runs",
                str(args.mc_runs),
                "--seed",
                "49",
            ],
            REPO_ROOT,
            out_dir / "monte_carlo.txt",
        ),
    }
    quality = json.loads((out_dir / "quality_gate.json").read_text(encoding="utf-8")) if (out_dir / "quality_gate.json").exists() else {}
    score = json.loads((out_dir / "authoring_score.json").read_text(encoding="utf-8")) if (out_dir / "authoring_score.json").exists() else {}
    mc_text = (out_dir / "monte_carlo.txt").read_text(encoding="utf-8", errors="replace") if (out_dir / "monte_carlo.txt").exists() else ""
    mc_rates = parse_mc(mc_text)
    summary = {
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "source": str(source),
        "world": str(world_path),
        "playable_nonterminal_encounters": len(SCENES) + 1,
        "ending_count": len(ENDING_TEXT),
        "option_count": sum(len(enc.get("options") or []) for enc in world["encounters"]),
        "reaction_count": sum(len(opt.get("reactions") or []) for enc in world["encounters"] for opt in (enc.get("options") or [])),
        "effect_count": sum(len(rxn.get("after_effects") or []) for enc in world["encounters"] for opt in (enc.get("options") or []) for rxn in (opt.get("reactions") or [])),
        "quality_gate": {"pass": quality.get("pass"), "failures": quality.get("failures", [])},
        "authoring_score": score,
        "monte_carlo_rates": mc_rates,
        "commands": commands,
    }
    write_json(out_dir / "run_summary.json", summary)
    (out_dir / "brief.md").write_text(
        "# Nine Lantern Expanded Kalam Exam\n\n"
        f"- World: `{world_path}`\n"
        f"- Playable non-terminal encounters: {summary['playable_nonterminal_encounters']}\n"
        f"- Endings: {summary['ending_count']}\n"
        f"- Options/reactions/effects: {summary['option_count']} / {summary['reaction_count']} / {summary['effect_count']}\n"
        f"- Quality pass: {quality.get('pass')} failures={quality.get('failures', [])}\n"
        f"- Authoring score: {score.get('weighted_authoring_verifier_score')}\n"
        f"- MC ending rates: {mc_rates}\n\n"
        "Improvement target: denser Kalam/Qadi scenes, active p/p2 effects, act spools, and a multi-clue secret route to `page_secret_ninth_lantern`.\n",
        encoding="utf-8",
        newline="\n",
    )
    print(str(out_dir / "brief.md"))
    print(str(out_dir / "run_summary.json"))
    return 0 if commands["validator"]["returncode"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
