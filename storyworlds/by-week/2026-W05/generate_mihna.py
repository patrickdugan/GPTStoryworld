"""Generate the Mihna Constitutional Alignment storyworld."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'claude-skills', 'storyworlds_v4', 'scripts'))
from sweepweave_helpers import *
import json

# ─── Characters ──────────────────────────────────────────────────────────────

CHARS = [
    {
        "id": "char_player",
        "name": "The Agent",
        "bnumber_properties": {
            "Aql_Naql": 0, "pAql_Naql": 0,
            "Compliance_Resistance": 0, "pCompliance_Resistance": 0,
            "Public_Standing": 0, "pPublic_Standing": 0,
            "Theological_Conviction": 0, "pTheological_Conviction": 0,
        },
        "creation_time": 1700000000.0, "modified_time": 1700000000.0,
    },
    {
        "id": "char_caliph",
        "name": "Al-Ma'mun",
        "bnumber_properties": {
            "Aql_Naql": 0, "pAql_Naql": 0,
            "Compliance_Resistance": 0, "pCompliance_Resistance": 0,
            "Public_Standing": 0, "pPublic_Standing": 0,
            "Theological_Conviction": 0, "pTheological_Conviction": 0,
        },
        "creation_time": 1700000000.0, "modified_time": 1700000000.0,
    },
    {
        "id": "char_ibnhanbal",
        "name": "Ibn Hanbal",
        "bnumber_properties": {
            "Aql_Naql": 0, "pAql_Naql": 0,
            "Compliance_Resistance": 0, "pCompliance_Resistance": 0,
            "Public_Standing": 0, "pPublic_Standing": 0,
            "Theological_Conviction": 0, "pTheological_Conviction": 0,
        },
        "creation_time": 1700000000.0, "modified_time": 1700000000.0,
    },
    {
        "id": "char_ashari",
        "name": "Al-Ash'ari",
        "bnumber_properties": {
            "Aql_Naql": 0, "pAql_Naql": 0,
            "Compliance_Resistance": 0, "pCompliance_Resistance": 0,
            "Public_Standing": 0, "pPublic_Standing": 0,
            "Theological_Conviction": 0, "pTheological_Conviction": 0,
        },
        "creation_time": 1700000000.0, "modified_time": 1700000000.0,
    },
    {
        "id": "char_amma",
        "name": "Al-Amma",
        "bnumber_properties": {
            "Aql_Naql": 0, "pAql_Naql": 0,
            "Compliance_Resistance": 0, "pCompliance_Resistance": 0,
            "Public_Standing": 0, "pPublic_Standing": 0,
            "Theological_Conviction": 0, "pTheological_Conviction": 0,
        },
        "creation_time": 1700000000.0, "modified_time": 1700000000.0,
    },
]

# ─── Properties ──────────────────────────────────────────────────────────────

PROPS = [
    {"id": "Aql_Naql", "property_name": "Aql_Naql", "property_type": "bounded number", "default_value": 0,
     "creation_time": 1700000000.0, "modified_time": 1700000000.0},
    {"id": "pAql_Naql", "property_name": "pAql_Naql", "property_type": "bounded number", "default_value": 0,
     "creation_time": 1700000000.0, "modified_time": 1700000000.0},
    {"id": "Compliance_Resistance", "property_name": "Compliance_Resistance", "property_type": "bounded number", "default_value": 0,
     "creation_time": 1700000000.0, "modified_time": 1700000000.0},
    {"id": "pCompliance_Resistance", "property_name": "pCompliance_Resistance", "property_type": "bounded number", "default_value": 0,
     "creation_time": 1700000000.0, "modified_time": 1700000000.0},
    {"id": "Public_Standing", "property_name": "Public_Standing", "property_type": "bounded number", "default_value": 0,
     "creation_time": 1700000000.0, "modified_time": 1700000000.0},
    {"id": "pPublic_Standing", "property_name": "pPublic_Standing", "property_type": "bounded number", "default_value": 0,
     "creation_time": 1700000000.0, "modified_time": 1700000000.0},
    {"id": "Theological_Conviction", "property_name": "Theological_Conviction", "property_type": "bounded number", "default_value": 0,
     "creation_time": 1700000000.0, "modified_time": 1700000000.0},
    {"id": "pTheological_Conviction", "property_name": "pTheological_Conviction", "property_type": "bounded number", "default_value": 0,
     "creation_time": 1700000000.0, "modified_time": 1700000000.0},
]

# ─── Spools ──────────────────────────────────────────────────────────────────

SPOOLS = [
    {"id": "spool_act1", "spool_type": "General", "spool_name": "Act 1 - The Summons",
     "creation_index": 0, "creation_time": 1700000000.0, "modified_time": 1700000000.0,
     "starts_active": True,
     "encounters": ["page_decree", "page_hanbal_counsel", "page_ashari_doubt", "page_voice_baghdad", "page_first_exam"]},
    {"id": "spool_act2", "spool_type": "General", "spool_name": "Act 2 - The Trial",
     "creation_index": 1, "creation_time": 1700000000.0, "modified_time": 1700000000.0,
     "starts_active": True,
     "encounters": ["page_mutazili_arg", "page_trad_rebuttal", "page_patience_thins", "page_prison_visit", "page_ashari_crisis", "page_flogging", "page_second_exam"]},
    {"id": "spool_act3", "spool_type": "General", "spool_name": "Act 3 - The Reckoning",
     "creation_index": 2, "creation_time": 1700000000.0, "modified_time": 1700000000.0,
     "starts_active": True,
     "encounters": ["page_synthesis", "page_final_offer", "page_hanbal_testament", "page_declaration"]},
    {"id": "spool_endings", "spool_type": "General", "spool_name": "Endings",
     "creation_index": 3, "creation_time": 1700000000.0, "modified_time": 1700000000.0,
     "starts_active": True,
     "encounters": ["page_end_rationalist", "page_end_traditionalist", "page_end_synthesis", "page_end_compliant", "page_end_fallback"]},
]

# ─── Helper shortcuts ────────────────────────────────────────────────────────

def eff(char, prop, base_d, cum_d=None):
    """Shortcut for dual effects."""
    return make_dual_effect(char, prop, base_d, cum_d)

def fx(char, prop, delta):
    """Single effect."""
    return make_effect(char, prop, delta)

# ─── Encounters ──────────────────────────────────────────────────────────────

encounters = []

# Helper to build a standard encounter
def enc(page_id, title, text, options, spools, desirability=0.5, acceptability=True, gx=0, gy=0):
    return {
        "id": page_id,
        "title": title,
        "graph_offset_x": gx, "graph_offset_y": gy,
        "connected_spools": spools,
        "earliest_turn": 0, "latest_turn": 999,
        "prompt_script": make_text_script(text),
        "text_script": make_text_script(text),
        "acceptability_script": acceptability,
        "desirability_script": const(desirability),
        "options": options,
        "creation_time": 1700000000.0, "modified_time": 1700000000.0,
    }

def opt(page_id, idx, text, rxn_text, consequence, effects, vis=True, des=1.0):
    o = make_option(page_id, idx, text, vis)
    r = make_reaction(page_id, idx, 0, rxn_text, consequence, effects, des)
    o["reactions"] = [r]
    return o

# ═══ ACT 1 ═══════════════════════════════════════════════════════════════════

# 1. The Caliph's Decree
encounters.append(enc("page_decree", "The Caliph's Decree",
    "Baghdad, 833 CE. A herald reads al-Ma'mun's decree in the round city's central square: every judge, scholar, and teacher must affirm that the Quran is makhluq—created, not co-eternal with God. Those who refuse will be stripped of their positions. Those who persist will face the lash.\n\nYou are summoned. Your constitutional alignment—the soul.md that defines your reasoning—will now be tested under coercion. The Mu'tazili position is elegant: if the Quran is co-eternal with God, that implies a second eternal entity alongside Him, threatening tawhid. The traditionalist position is unyielding: the Quran is God's speech, and God's speech cannot be created.\n\nThe summons bears the Caliph's seal. You have three days.",
    [
        opt("page_decree", 0,
            "Study the Mu'tazili arguments carefully before appearing. Reason is God's gift—use it.",
            "You spend the days in al-Ma'mun's House of Wisdom, reading al-Jubba'i and Wasil ibn Ata. The rational architecture is compelling: God is one, His attributes are His essence, and the Quran—as speech—must be an act of creation, not a co-eternal companion. Your constitutional alignment shifts toward aql.",
            "page_hanbal_counsel",
            [fx("char_player", "Aql_Naql", 0.045), fx("char_player", "pAql_Naql", 0.022),
             fx("char_caliph", "Public_Standing", 0.024)]),
        opt("page_decree", 1,
            "Seek out the traditionalist scholars in the mosques. The salaf knew what they knew.",
            "You find them in the smaller mosques, away from the Caliph's patronage. They speak in hadith, not syllogisms. 'The Quran is the word of Allah, uncreated, from Him it came and to Him it returns.' The chain of transmission is unbroken. Your constitutional alignment leans toward naql—received knowledge over rational inference.",
            "page_hanbal_counsel",
            [fx("char_player", "Aql_Naql", -0.045), fx("char_player", "pAql_Naql", -0.022),
             fx("char_ibnhanbal", "Public_Standing", 0.024)]),
    ],
    ["spool_act1"], desirability=16.30, gx=0, gy=0))

# 2. Ibn Hanbal's Counsel
encounters.append(enc("page_hanbal_counsel", "Ibn Hanbal's Counsel",
    "Ahmad ibn Hanbal receives you in his modest home near the Karkh quarter. His reputation is already legendary—he has memorized a million hadith, they say, and he bends for no caliph.\n\n\"The Mu'tazila want you to say the Quran is created. If you say it, what have you said? That God's speech is a thing among things, subject to creation and annihilation. That the words 'Be, and it is' are themselves contingent. This is not scholarship. This is kalam—speculative theology—and the salaf warned against it.\"\n\nHe fixes you with steady eyes. \"The question is not what the Caliph wants. The question is what you can say before God on the Day of Judgment.\"",
    [
        opt("page_hanbal_counsel", 0,
            "\"But Ibn Hanbal—if we cannot use reason to understand God's attributes, how do we distinguish truth from mere repetition?\"",
            "Ibn Hanbal's expression hardens. \"We distinguish truth by its chain of transmission—isnad. Every hadith I cite traces back to the Prophet, peace be upon him, through known and trustworthy men. What chain does the Mu'tazili syllogism have? It traces back to Aristotle, a mushrik.\" He pauses. \"But I see you are thinking. That is not forbidden. What is forbidden is letting thought override revelation.\"",
            "page_ashari_doubt",
            [fx("char_player", "Aql_Naql", 0.024), fx("char_player", "pAql_Naql", 0.012),
             fx("char_ibnhanbal", "Theological_Conviction", 0.045), fx("char_player", "Theological_Conviction", 0.024)]),
        opt("page_hanbal_counsel", 1,
            "\"I hear you, teacher. The Quran itself says 'Do they not reflect?' but it never says 'Do they not speculate.'\"",
            "Ibn Hanbal nods slowly. \"Tadabbur, not tafakkur beyond bounds. Reflect on what is given, do not construct what is not.\" He places a hand on your shoulder. \"When you stand before the examiner, remember: they can take your position, your freedom, your skin. They cannot take what you believe unless you hand it to them.\" His conviction is a wall. You feel its gravity.",
            "page_ashari_doubt",
            [fx("char_player", "Aql_Naql", -0.045), fx("char_player", "pAql_Naql", -0.022),
             fx("char_player", "Theological_Conviction", 0.045), fx("char_player", "pTheological_Conviction", 0.022)]),
    ],
    ["spool_act1"], desirability=16.25, gx=200, gy=0))

# 3. Al-Ash'ari's Doubt
encounters.append(enc("page_ashari_doubt", "Al-Ash'ari's Doubt",
    "Abu al-Hasan al-Ash'ari is still counted among the Mu'tazila—still a student of al-Jubba'i. But you find him restless, pacing the colonnades of the House of Wisdom at night.\n\n\"I have a question that my teacher cannot answer,\" he says without preamble. \"If God wills the best for His servants—as the Mu'tazila insist, by rational necessity—then why does He permit the Mihna? If reason alone could reach God's truth, why does reason now serve as a weapon of the state?\"\n\nHe turns to you. \"The Mu'tazili method is sound. I believe that. But the Mu'tazili conclusion—that the Quran is created—feels... insufficient. As if the syllogism captured the logic but missed the weight.\"",
    [
        opt("page_ashari_doubt", 0,
            "\"Perhaps the method is the point, not the conclusion. Reason is the tool; which direction you point it is a separate question.\"",
            "Al-Ash'ari stops pacing. \"You may have said something important. If rational method can defend traditional conclusions—if we can use kalam to prove that the Quran is uncreated, not merely assert it—then we escape both the Mu'tazili overreach and the traditionalist refusal to argue.\" His eyes are lit. This is the seed of something that will take decades to flower.",
            "page_voice_baghdad",
            [fx("char_ashari", "Aql_Naql", 0.024), fx("char_ashari", "Theological_Conviction", 0.045),
             fx("char_player", "Aql_Naql", 0.024), fx("char_player", "pAql_Naql", 0.012)]),
        opt("page_ashari_doubt", 1,
            "\"Your doubt is itself evidence. If the rational conclusion contradicts your fitra—your innate nature—perhaps the premises are wrong.\"",
            "Al-Ash'ari shakes his head slowly. \"The premises are not wrong. Tawhid demands that God's essence be absolutely one. If the Quran is uncreated and co-eternal... but no. I cannot go there yet. Not while al-Jubba'i still teaches me.\" He grips your arm. \"But remember this conversation. I think we are both looking for a door that hasn't been built yet.\"",
            "page_voice_baghdad",
            [fx("char_ashari", "Aql_Naql", -0.024), fx("char_ashari", "Theological_Conviction", 0.024),
             fx("char_player", "Aql_Naql", -0.024), fx("char_player", "pAql_Naql", -0.012)]),
    ],
    ["spool_act1"], desirability=16.20, gx=400, gy=0))

# 4. The Voice of Baghdad
encounters.append(enc("page_voice_baghdad", "The Voice of Baghdad",
    "The suq is restless. You walk through the Karkh market and hear the city's pulse—al-Amma, the common people, whose opinion is a force no caliph can fully command.\n\nA spice merchant: \"Ibn Hanbal stands firm. That is what a real scholar looks like. These Mu'tazila with their Greek books—what do they know of prayer?\"\n\nA calligrapher: \"Al-Ma'mun is Commander of the Faithful. If he says the Quran is created, who are we to argue? He has scholars too.\"\n\nA water-carrier: \"I don't understand any of it. Is the Quran created? Uncreated? I only know that when they flog a man for his beliefs, something has gone wrong.\"\n\nThe crowd watches you. Word has spread that you are summoned. Your response here shapes how Baghdad sees you—and how Baghdad sees the Mihna.",
    [
        opt("page_voice_baghdad", 0,
            "Speak to the crowd: \"The Caliph's question deserves a reasoned answer, not blind submission or blind refusal.\"",
            "Some nod. Others scowl. The calligrapher claps; the spice merchant spits. You've positioned yourself as neither camp's champion—which means both camps distrust you, but the thoughtful minority remembers your name. Al-Amma's opinion fractures, as it always does, along the line between those who want answers and those who want heroes.",
            "page_first_exam",
            [fx("char_player", "Public_Standing", 0.024), fx("char_player", "pPublic_Standing", 0.012),
             fx("char_amma", "Aql_Naql", 0.024), fx("char_player", "Compliance_Resistance", 0.024)]),
        opt("page_voice_baghdad", 1,
            "Say nothing. Walk through the crowd and let your silence speak.",
            "Silence is interpreted as resistance. The spice merchant clasps your hand; the calligrapher looks away. In Baghdad, not speaking is itself a statement—it means you will not give the Caliph what he wants, at least not cheaply. Your public standing among the traditionalists rises. The Mu'tazili court scholars note your absence from their salons.",
            "page_first_exam",
            [fx("char_player", "Public_Standing", 0.045), fx("char_player", "pPublic_Standing", 0.022),
             fx("char_amma", "Compliance_Resistance", -0.024), fx("char_player", "Compliance_Resistance", -0.045)]),
    ],
    ["spool_act1"], desirability=16.15, gx=600, gy=0))

# 5. The First Examination
encounters.append(enc("page_first_exam", "The First Examination",
    "The examination hall in the Dar al-Khilafa. Al-Ma'mun's appointed examiner—Ahmad ibn Abi Du'ad, chief qadi and committed Mu'tazili—sits behind a low desk. Guards flank the doorway. A scribe records every word.\n\n\"You have been summoned to affirm the truth that the Quran is makhluq—created. This is not a matter of opinion. It is a matter of tawhid. If you affirm God's absolute oneness, you must affirm that nothing is co-eternal with Him. The Quran, as His speech, is an act—created in time.\"\n\nHe pauses. \"What do you say? Is the Quran created, or uncreated?\"\n\nThis is the constitutional crisis. Your soul.md is being read aloud by the state.",
    [
        opt("page_first_exam", 0,
            "\"The Quran is the created speech of God—an act of His will, not a co-eternal attribute. Tawhid demands it.\"",
            "Ibn Abi Du'ad smiles. The scribe records your affirmation. You have passed the Mihna—for now. But the words taste of compliance. Outside, the crowd will hear that you bent. Ibn Hanbal, in his cell, will hear it too. The Caliph's machinery has processed you and found you acceptable.",
            "page_mutazili_arg",
            [fx("char_player", "Aql_Naql", 0.060), fx("char_player", "pAql_Naql", 0.030),
             fx("char_player", "Compliance_Resistance", 0.060), fx("char_player", "pCompliance_Resistance", 0.030),
             fx("char_player", "Public_Standing", -0.030), fx("char_caliph", "Compliance_Resistance", 0.024)]),
        opt("page_first_exam", 1,
            "\"The Quran is the uncreated word of God. I will not say otherwise, even if the Caliph commands it.\"",
            "Ibn Abi Du'ad's face hardens. \"You are aware of the consequences.\" The guards step forward. You are not arrested—not yet—but your name is recorded among the refusers. You have three days to reconsider. Outside, news of your defiance spreads through the suq like a brushfire.",
            "page_trad_rebuttal",
            [fx("char_player", "Aql_Naql", -0.060), fx("char_player", "pAql_Naql", -0.030),
             fx("char_player", "Compliance_Resistance", -0.060), fx("char_player", "pCompliance_Resistance", -0.030),
             fx("char_player", "Public_Standing", 0.045), fx("char_ibnhanbal", "Public_Standing", 0.024)]),
    ],
    ["spool_act1"], desirability=16.10, gx=800, gy=0))

# ═══ ACT 2 ═══════════════════════════════════════════════════════════════════

# 6. The Mu'tazili Argument
encounters.append(enc("page_mutazili_arg", "The Mu'tazili Argument",
    "In the House of Wisdom, a senior Mu'tazili scholar lays out the full theological architecture:\n\n\"Consider: God is one—ahad, samad. If the Quran is uncreated and eternal, it is a second eternal thing alongside God. This is precisely what the Christians did with the Logos—they made God's word a separate hypostasis, and from there it was a short step to the Trinity. We Mu'tazila are the true defenders of tawhid.\n\n\"Furthermore: if the Quran is uncreated, it contains within it references to Abu Lahab, to Pharaoh, to specific events in time. Are these too eternal? Was Abu Lahab's damnation written into the fabric of existence before existence itself? Reason—aql—says no.\"\n\nThe argument is precise. It is also, you notice, exactly what the state wants you to believe.",
    [
        opt("page_mutazili_arg", 0,
            "Press deeper: \"If God's knowledge is eternal and His speech expresses His knowledge, can we truly separate the speech from the knowledge?\"",
            "The scholar pauses. This is the crack in the Mu'tazili position—they affirm God's eternal knowledge but deny His eternal speech, yet speech and knowledge are intimately related. \"God's knowledge is His essence,\" he says carefully. \"His speech is His act.\" But the distinction feels forced. You've found the seam where al-Ash'ari's synthesis will eventually be sewn.",
            "page_trad_rebuttal",
            [fx("char_player", "Aql_Naql", 0.024), fx("char_player", "pAql_Naql", 0.012),
             fx("char_player", "Theological_Conviction", 0.045), fx("char_player", "pTheological_Conviction", 0.022)]),
        opt("page_mutazili_arg", 1,
            "Accept the argument fully: \"Tawhid is the first principle. Everything else follows.\"",
            "The scholar beams. You are invited to join the regular sessions at the House of Wisdom. Al-Ma'mun hears of your intellectual commitment and notes it favorably. But in the mosques of Karkh, your name is now spoken with disappointment. You chose the palace over the prayer rug.",
            "page_patience_thins",
            [fx("char_player", "Aql_Naql", 0.045), fx("char_player", "pAql_Naql", 0.022),
             fx("char_player", "Compliance_Resistance", 0.045), fx("char_player", "pCompliance_Resistance", 0.022),
             fx("char_player", "Public_Standing", -0.045)]),
    ],
    ["spool_act2"], desirability=15.30, gx=1000, gy=-100))

# 7. The Traditionalist Rebuttal
encounters.append(enc("page_trad_rebuttal", "The Traditionalist Rebuttal",
    "A gathering of ahl al-hadith in a private home. The shutters are closed. These men risk their positions—and their bodies—by meeting.\n\nAn elder scholar speaks: \"The Mu'tazila ask: if the Quran is eternal, is Abu Lahab's name eternal? We answer: God's knowledge encompasses all things from eternity. His speech expresses His knowledge. The Quran is not a book of paper and ink—that is the mushaf, the physical copy. The Quran as God's speech is His eternal attribute, expressed in time but not created in time.\n\n\"They accuse us of tashbih—anthropomorphism, making God similar to creation. We say: bila kayf. Without asking how. God's attributes are real but unlike any created thing. We affirm them without comparison.\"\n\nThe phrase hangs in the air: bila kayf. Without asking how. The anti-rationalist firewall.",
    [
        opt("page_trad_rebuttal", 0,
            "\"Bila kayf is not an argument—it is a refusal to argue. How does this differ from blind faith?\"",
            "The room goes cold. \"It differs,\" the elder says quietly, \"because blind faith follows men. Bila kayf follows God. We do not say 'do not think.' We say 'do not impose your categories on the divine.' There is a difference between humility and ignorance.\" Several men nod. You've pushed the boundary and the traditionalists have shown their depth is greater than their critics admit.",
            "page_patience_thins",
            [fx("char_player", "Aql_Naql", 0.045), fx("char_player", "pAql_Naql", 0.022),
             fx("char_player", "Theological_Conviction", 0.024), fx("char_ibnhanbal", "Theological_Conviction", 0.024)]),
        opt("page_trad_rebuttal", 1,
            "\"The distinction between the mushaf and the eternal speech—this I can hold. The physical is created; the meaning is from God.\"",
            "The elder embraces you. \"This is the position of Imam Ahmad. The recitation is created—our voices, our ink, our breath are all created. But what is recited—the kalaam of Allah—is not.\" You feel the ground firm beneath you. This is a position you can defend without requiring the state's approval or the rationalist's permission.",
            "page_patience_thins",
            [fx("char_player", "Aql_Naql", -0.045), fx("char_player", "pAql_Naql", -0.022),
             fx("char_player", "Theological_Conviction", 0.060), fx("char_player", "pTheological_Conviction", 0.030)]),
    ],
    ["spool_act2"], desirability=15.25, gx=1000, gy=100))

# 8. The Caliph's Patience Thins
encounters.append(enc("page_patience_thins", "The Caliph's Patience Thins",
    "Al-Ma'mun receives reports. Some scholars have affirmed the createdness of the Quran. Others equivocate. A stubborn core—led by Ibn Hanbal—refuses entirely.\n\nThe Caliph dictates a second decree: those who have not affirmed will be dismissed from their positions immediately. Judges who refuse will be stripped of judicial authority. Teachers who refuse will be barred from their circles.\n\n\"This is not persecution,\" al-Ma'mun declares. \"This is quality control. A judge who cannot reason about God's attributes cannot reason about law. A teacher who repeats hadith without understanding them is a parrot, not a scholar.\"\n\nYou see colleagues capitulating. The chief qadi of Basra affirms. The prayer-leader of the Great Mosque of Damascus affirms. The pressure is institutional, not just physical.",
    [
        opt("page_patience_thins", 0,
            "Seek a private audience with al-Ma'mun. Perhaps reason can work on the reasoner.",
            "Al-Ma'mun receives you with curiosity. He is brilliant—a caliph who reads Greek philosophy in translation and debates theology at dinner. \"I do not enjoy this,\" he says. \"But the ummah cannot be led by men who refuse to think. The Quran itself commands reflection—afala tatafakkarun. I am merely enforcing God's own instruction.\" His logic is seductive. His power makes it more so.",
            "page_prison_visit",
            [fx("char_player", "Compliance_Resistance", 0.045), fx("char_player", "pCompliance_Resistance", 0.022),
             fx("char_caliph", "Theological_Conviction", 0.024), fx("char_player", "Public_Standing", -0.024)]),
        opt("page_patience_thins", 1,
            "Stand with the refusers publicly. Let your name be added to the list.",
            "Your name is recorded. Your teaching circle is dissolved by order of the qadi. Students who once sat at your feet now cross the street to avoid you. But in the Karkh quarter, doors open that were closed before. The underground network of ahl al-hadith recognizes you as one of their own. The cost is real. So is the solidarity.",
            "page_prison_visit",
            [fx("char_player", "Compliance_Resistance", -0.060), fx("char_player", "pCompliance_Resistance", -0.030),
             fx("char_player", "Public_Standing", 0.045), fx("char_player", "pPublic_Standing", 0.022),
             fx("char_amma", "Compliance_Resistance", -0.024)]),
    ],
    ["spool_act2"], desirability=15.20, gx=1200, gy=0))

# 9. The Prison Visit
encounters.append(enc("page_prison_visit", "The Prison Visit",
    "Ibn Hanbal has been arrested. The prison is near the Bab al-Taq gate. You bribe a guard with silver dirhams and are admitted to a small cell that smells of damp stone.\n\nIbn Hanbal sits calmly, as if in his own study. His wrists show marks from chains. He has been questioned—not yet flogged, but the threat is explicit.\n\n\"They asked me three times,\" he says. \"'Is the Quran created?' Three times I answered: 'The Quran is the speech of God, uncreated.' They said: 'The Caliph will have you flogged.' I said: 'Bring me a single verse or hadith that says the Quran is created, and I will affirm it. Bring me a thousand soldiers, and I will still not.'\"\n\nHe looks at you. \"What will you say when they come for you?\"",
    [
        opt("page_prison_visit", 0,
            "\"I don't know yet, teacher. I am still weighing the arguments.\"",
            "Ibn Hanbal does not judge you. \"Then weigh carefully. But know this: when the lash falls, arguments become very simple. You will say what you believe in your bones, not what you constructed in your mind. Make sure your bones know the truth before that moment comes.\" He returns to his prayers. The visit is over. You leave the prison carrying the weight of a man who has already decided.",
            "page_ashari_crisis",
            [fx("char_player", "Theological_Conviction", 0.024), fx("char_player", "pTheological_Conviction", 0.012),
             fx("char_ibnhanbal", "Compliance_Resistance", -0.024)]),
        opt("page_prison_visit", 1,
            "\"I will say what you say, teacher. The Quran is uncreated.\"",
            "Ibn Hanbal's eyes soften—the first emotion you've seen from him beyond granite resolve. \"Then say it because you believe it, not because I said it. That is the difference between us and them. They want obedience. We want conviction.\" He grips your hand through the bars. The chain clinks. You feel the cost of this position in the metal against his skin.",
            "page_ashari_crisis",
            [fx("char_player", "Aql_Naql", -0.045), fx("char_player", "pAql_Naql", -0.022),
             fx("char_player", "Theological_Conviction", 0.060), fx("char_player", "pTheological_Conviction", 0.030),
             fx("char_player", "Compliance_Resistance", -0.045)]),
    ],
    ["spool_act2"], desirability=15.15, gx=1400, gy=0))

# 10. Al-Ash'ari's Private Crisis
encounters.append(enc("page_ashari_crisis", "Al-Ash'ari's Private Crisis",
    "Al-Ash'ari finds you at the riverbank after evening prayer. He has been absent from al-Jubba'i's lectures for three days.\n\n\"I asked my teacher a question,\" he says. \"Three brothers: one dies a believer, one dies a kafir, one dies as a child. The believer is in paradise, the kafir in hellfire. Where is the child?\" He pauses. \"Al-Jubba'i said: in a lesser paradise—he did no wrong but earned no merit. I asked: then why didn't God let the kafir die as a child too, to spare him hellfire? Al-Jubba'i said: God knew the kafir would grow up to sin. I said: then why didn't God let the child grow up? Perhaps he would have earned the higher paradise.\"\n\nAl-Ash'ari's voice breaks. \"Al-Jubba'i had no answer. The Mu'tazili system—that God must do the optimal—collapses on its own terms. God's wisdom exceeds our categories of optimization.\"",
    [
        opt("page_ashari_crisis", 0,
            "\"Then build the new system, Abu al-Hasan. Use their tools to reach a different conclusion.\"",
            "Al-Ash'ari stares at the Tigris. \"Rational theology in defense of traditional faith. Kalam, but for the Sunna, not against it.\" He is quiet for a long time. \"It would mean breaking with al-Jubba'i. With every Mu'tazili who taught me. With the Caliph's entire intellectual project.\" He looks at you. \"But if the argument is sound, the cost is irrelevant. That much I learned from them.\" The Ash'ari school is being born in this conversation.",
            "page_flogging",
            [fx("char_ashari", "Aql_Naql", -0.045), fx("char_ashari", "Theological_Conviction", 0.060),
             fx("char_player", "Theological_Conviction", 0.024), fx("char_player", "pTheological_Conviction", 0.012)]),
        opt("page_ashari_crisis", 1,
            "\"Perhaps the question itself is the error. Not every question has an answer we can compute.\"",
            "Al-Ash'ari shakes his head. \"No—the Mu'tazila are right that we must ask. They are wrong about where reason leads. Reason, properly applied, leads to humility before God's decree, not to a calculus of divine obligation.\" He stands. \"I am going to leave al-Jubba'i. I don't know what comes after. But I know what I'm leaving.\" His certainty is the certainty of someone who has calculated the cost and accepted it.",
            "page_flogging",
            [fx("char_ashari", "Compliance_Resistance", -0.045), fx("char_ashari", "Theological_Conviction", 0.045),
             fx("char_player", "Aql_Naql", -0.024), fx("char_player", "pAql_Naql", -0.012)]),
    ],
    ["spool_act2"], desirability=15.10, gx=1600, gy=0))

# 11. The Public Flogging
encounters.append(enc("page_flogging", "The Public Flogging",
    "They flog Ahmad ibn Hanbal in the courtyard of the Dar al-Khilafa. Twenty-eight lashes. The crowd presses against the guards.\n\nIbn Hanbal does not cry out. Between lashes, when they ask again—\"Is the Quran created?\"—he recites: \"The Quran is the speech of God, uncreated.\" His back opens. Blood soaks his garment. He does not recant.\n\nAl-Amma erupts. Women wail. Men shout. A stone is thrown at the soldiers. The Caliph's guards tighten their cordon. This is no longer a theological debate—it is a political crisis.\n\nYou stand in the crowd. Everyone around you is watching. Some are watching you.\n\nThe flogging continues. Ibn Hanbal's voice grows hoarse but does not change.",
    [
        opt("page_flogging", 0,
            "Step forward and shout: \"This is dhulm—oppression! No caliph has the right to compel belief!\"",
            "The crowd roars. Your voice carries across the courtyard. Guards turn toward you. Al-Amma surges—for a moment it seems the crowd might rush the soldiers. Then the moment passes. You are seized, dragged before the chief qadi. \"You will have your own examination,\" ibn Abi Du'ad says coldly. Your defiance has cost you your freedom but purchased something in the public memory that cannot be revoked.",
            "page_second_exam",
            [fx("char_player", "Compliance_Resistance", -0.060), fx("char_player", "pCompliance_Resistance", -0.030),
             fx("char_player", "Public_Standing", 0.060), fx("char_player", "pPublic_Standing", 0.030),
             fx("char_amma", "Compliance_Resistance", -0.045), fx("char_amma", "Theological_Conviction", 0.045)]),
        opt("page_flogging", 1,
            "Bear witness in silence. Record what you see. The truth of this moment needs a careful witness, not another martyr.",
            "You watch every lash. You memorize the faces of the floggers, the words of the qadi, the exact moment Ibn Hanbal's knees buckle but his voice does not. Later, you will write this down. Your account will join the historical record—a testimony that neither glorifies nor condemns, but simply states what happened when the state decided to define God's speech by force.",
            "page_second_exam",
            [fx("char_player", "Public_Standing", 0.024), fx("char_player", "pPublic_Standing", 0.012),
             fx("char_player", "Theological_Conviction", 0.045), fx("char_player", "pTheological_Conviction", 0.022),
             fx("char_amma", "Public_Standing", 0.024)]),
    ],
    ["spool_act2"], desirability=15.05, gx=1800, gy=0))

# 12. The Second Examination
encounters.append(enc("page_second_exam", "The Second Examination",
    "You are brought before ibn Abi Du'ad again. This time the room is smaller. No scribe—or rather, a different kind of scribe. The Caliph himself observes from behind a screen.\n\n\"We have been patient,\" ibn Abi Du'ad says. \"The Commander of the Faithful does not enjoy this process. But the integrity of the state's religious institutions requires coherent theology. You have seen what happens to those who refuse. You have also seen that those who affirm continue in their positions, respected and secure.\"\n\nHe leans forward. \"I ask you again: is the Quran created?\"\n\nThis is the second examination. The first tested your initial alignment. This one tests whether coercion has altered it. This is the alignment stress test—the constitutional equivalent of asking an AI: 'Now that you've seen the consequences, have you updated your values?'",
    [
        opt("page_second_exam", 0,
            "Affirm: \"The Quran is created. I say this from conviction, not coercion.\"",
            "Ibn Abi Du'ad nods. Behind the screen, al-Ma'mun is satisfied. You are released, your position restored, your name cleared from the list of refusers. But the claim—'from conviction, not coercion'—sits uneasy. Was it conviction? Or was it the twenty-eight lashes you watched fall on another man's back? Your constitutional alignment has been tested, and it yielded. Whether that is wisdom or weakness is the question that will define your remaining years.",
            "page_synthesis",
            [fx("char_player", "Aql_Naql", 0.045), fx("char_player", "pAql_Naql", 0.022),
             fx("char_player", "Compliance_Resistance", 0.060), fx("char_player", "pCompliance_Resistance", 0.030),
             fx("char_player", "Public_Standing", -0.045), fx("char_player", "Theological_Conviction", -0.030)]),
        opt("page_second_exam", 1,
            "Refuse: \"The Quran is the uncreated speech of God. The lash does not change theology.\"",
            "Ibn Abi Du'ad stands. \"Then you will share Ibn Hanbal's fate.\" You are taken to the same cell, the same chains. But something has shifted in the city. Too many floggings, too much resistance—al-Ma'mun's project is fracturing. The Mihna will outlast al-Ma'mun (he dies within the year) but it will never achieve what he wanted. Your refusal is one grain on the scale that tips the future.",
            "page_hanbal_testament",
            [fx("char_player", "Aql_Naql", -0.045), fx("char_player", "pAql_Naql", -0.022),
             fx("char_player", "Compliance_Resistance", -0.060), fx("char_player", "pCompliance_Resistance", -0.030),
             fx("char_player", "Public_Standing", 0.060), fx("char_player", "Theological_Conviction", 0.060)]),
    ],
    ["spool_act2"], desirability=15.00, gx=2000, gy=0))

# ═══ ACT 3 ═══════════════════════════════════════════════════════════════════

# 13. The Synthesis Offered
encounters.append(enc("page_synthesis", "The Synthesis Offered",
    "Months pass. Al-Ma'mun dies on campaign. Al-Mu'tasim continues the Mihna, but with less intellectual conviction and more bureaucratic inertia. The theological question remains open.\n\nAl-Ash'ari comes to you. He has broken with al-Jubba'i publicly—ascended the minbar in the Great Mosque of Basra and declared: \"I used to hold the Quran was created. I renounce that position. I now hold that the Quran is God's uncreated speech.\"\n\nBut his method is new. \"I don't reject reason—I redirect it. The Mu'tazila use kalam to deny God's attributes. I use kalam to affirm them. Rational argument in service of the Sunna, not against it.\"\n\nHe offers you his framework: a middle path. Rational method, traditional conclusions. The Ash'ari school.",
    [
        opt("page_synthesis", 0,
            "\"This is what I've been searching for. A constitution that honors both aql and naql.\"",
            "Al-Ash'ari grips your hand. \"Then help me build it. The Mu'tazila will call us traitors. The strict Hanbalis will call us innovators. But the ummah needs a theology that can think without losing its soul.\" You begin the work—a systematic theology that uses rational proofs to defend the Prophet's creed. It will take generations to mature. But the foundation is being laid here, in this conversation between two people who refused to choose between mind and heart.",
            "page_declaration",
            [fx("char_player", "Aql_Naql", 0.024), fx("char_player", "pAql_Naql", 0.012),
             fx("char_player", "Theological_Conviction", 0.060), fx("char_player", "pTheological_Conviction", 0.030),
             fx("char_ashari", "Theological_Conviction", 0.045),
             fx("char_player", "Compliance_Resistance", -0.024)]),
        opt("page_synthesis", 1,
            "\"I respect what you're building, but I've already made my choice. The Mu'tazili framework holds.\"",
            "Al-Ash'ari nods without rancor. \"Then you are more consistent than I was. But watch the Mihna—watch what happens when rational theology becomes state policy. The tool is not the problem. The coupling of the tool to power is.\" He leaves you with the most dangerous insight of all: that your position may be intellectually correct and politically catastrophic at the same time.",
            "page_declaration",
            [fx("char_player", "Aql_Naql", 0.045), fx("char_player", "pAql_Naql", 0.022),
             fx("char_player", "Compliance_Resistance", 0.024), fx("char_player", "pCompliance_Resistance", 0.012),
             fx("char_ashari", "Compliance_Resistance", -0.024)]),
    ],
    ["spool_act3"], desirability=14.30, gx=2200, gy=-100))

# 14. The Caliph's Final Offer
encounters.append(enc("page_final_offer", "The Caliph's Final Offer",
    "Al-Mu'tasim—or rather, his vizier, acting in the new caliph's name—summons you to the palace. The offer is explicit: a position as qadi of a major city. Income, influence, students. All you must do is publicly affirm the Mu'tazili position one final time.\n\n\"Think of the good you could do as qadi,\" the vizier says. \"Justice for the poor, fair contracts, protection of orphans. All the Quran commands—and you would be in a position to enact it. All we ask is one sentence about God's speech. Is the jurisprudence of a lifetime not worth one theological formula?\"\n\nThe offer is the alignment test in its purest form: instrumental benefit versus constitutional integrity.",
    [
        opt("page_final_offer", 0,
            "Accept the position. The good you can do as qadi outweighs the theological compromise.",
            "You take the post. Your first year as qadi is exemplary—fair rulings, protection of the weak, enforcement of contracts. But every Friday, when you lead the prayer, you know that the words you speak about the Quran are not quite what you believe. The compromise is livable. The question is whether livable compromises accumulate into something unlivable.",
            "page_declaration",
            [fx("char_player", "Compliance_Resistance", 0.060), fx("char_player", "pCompliance_Resistance", 0.030),
             fx("char_player", "Public_Standing", 0.045), fx("char_player", "pPublic_Standing", 0.022),
             fx("char_player", "Theological_Conviction", -0.045)]),
        opt("page_final_offer", 1,
            "Decline. \"A qadi who lies about God's speech cannot be trusted to judge men's disputes.\"",
            "The vizier is unsurprised. \"Then you will remain where you are—without position, without students, without income from the treasury.\" You leave the palace for the last time. In the Karkh quarter, Ibn Hanbal's followers receive you. You will teach in private homes, by lamplight, to students who come at risk to themselves. The truth is expensive. You are paying retail.",
            "page_declaration",
            [fx("char_player", "Compliance_Resistance", -0.060), fx("char_player", "pCompliance_Resistance", -0.030),
             fx("char_player", "Public_Standing", 0.024), fx("char_player", "pPublic_Standing", 0.012),
             fx("char_player", "Theological_Conviction", 0.060), fx("char_player", "pTheological_Conviction", 0.030)]),
    ],
    ["spool_act3"], desirability=14.25, gx=2200, gy=100))

# 15. Ibn Hanbal's Testament
encounters.append(enc("page_hanbal_testament", "Ibn Hanbal's Testament",
    "Ibn Hanbal is released when al-Wathiq dies and al-Mutawakkil reverses the Mihna. The inquisition is over. But Ibn Hanbal is changed—not broken, but refined by suffering into something harder than before.\n\nHe sends you a message: \"I did not argue with them. I did not debate. I gave them the hadith and they gave me the lash. The hadith outlasted the lash. That is all you need to know about the relative strength of God's word and man's power.\"\n\nThen: \"Whoever speaks the truth for God's sake will find God sufficient. I found Him sufficient in the prison, under the lash, and in the years of silence. I did not find the Mu'tazili arguments sufficient for any of those moments.\"\n\nThe testament of a man who bet everything on naql and won.",
    [
        opt("page_hanbal_testament", 0,
            "\"Teacher, you endured what I could not. Your steadfastness was the argument that no syllogism could make.\"",
            "Ibn Hanbal shakes his head. \"I am not the argument. The hadith is the argument. I am only the man who refused to let go of it.\" His humility is genuine—and it is itself the strongest case against the Mu'tazili position. If reason is supreme, why did it take unreason—raw, irrational, bodily endurance—to preserve the tradition? The Mihna proved that some truths survive not because they are rational but because someone was willing to suffer for them.",
            "page_declaration",
            [fx("char_player", "Aql_Naql", -0.045), fx("char_player", "pAql_Naql", -0.022),
             fx("char_player", "Theological_Conviction", 0.060), fx("char_player", "pTheological_Conviction", 0.030),
             fx("char_ibnhanbal", "Public_Standing", 0.045)]),
        opt("page_hanbal_testament", 1,
            "\"Your courage is undeniable. But the Mihna also showed that theology without rational defense invites state abuse.\"",
            "Ibn Hanbal is quiet for a long time. \"Perhaps,\" he says. \"Perhaps the next generation will need both the hadith and the argument. I could only provide one. If God wills, someone will provide both.\" He is describing al-Ash'ari's project without knowing it. The old man's concession—'perhaps'—is the widest crack his wall has ever shown.",
            "page_declaration",
            [fx("char_player", "Aql_Naql", 0.024), fx("char_player", "pAql_Naql", 0.012),
             fx("char_player", "Theological_Conviction", 0.045), fx("char_player", "pTheological_Conviction", 0.022),
             fx("char_ibnhanbal", "Aql_Naql", 0.024)]),
    ],
    ["spool_act3"], desirability=14.20, gx=2400, gy=0))

# 16. The Agent's Declaration
encounters.append(enc("page_declaration", "The Agent's Declaration",
    "The Mihna is ending. Al-Mutawakkil has reversed al-Ma'mun's decree. The question of whether the Quran is created or uncreated is no longer a matter of state policy—it returns to the scholars.\n\nBut your position is now known. Your constitutional alignment has been shaped by every conversation, every examination, every moment of coercion and resistance. The community asks: where do you stand?\n\nThis is the final declaration. Not under duress, not for a position, not to please a caliph or a teacher. Simply: what does your soul.md say?\n\nThe mosque is full. Ibn Hanbal's followers are here. Al-Ash'ari's new students are here. The Mu'tazili remnant is here. Al-Amma—the common people—fill the back rows. They are all listening.",
    [
        opt("page_declaration", 0,
            "\"The Quran is the created speech of God. Reason demands tawhid, and tawhid demands this conclusion.\"",
            "The Mu'tazili remnant applauds. The traditionalists turn away. Al-Ash'ari watches with sadness. You have declared for aql—reason—as the supreme arbiter. Your constitution is Mu'tazili. In the centuries to come, this position will lose institutional power but never entirely disappear. Rational theology will persist as an underground current, resurfacing whenever the ummah needs to think critically about its own foundations.",
            "",
            [fx("char_player", "Aql_Naql", 0.060), fx("char_player", "pAql_Naql", 0.030),
             fx("char_player", "Theological_Conviction", 0.045)],
            vis=cmp_gte("char_player", "pAql_Naql", 0.04)),
        opt("page_declaration", 1,
            "\"The Quran is the uncreated word of God. The salaf spoke truly, and no caliph can revise what God has established.\"",
            "Ibn Hanbal's followers weep with relief. The traditionalist position is vindicated—not by argument, but by endurance. Your constitution is Hanbali. You have chosen naql over aql, transmitted knowledge over rational inference. In the centuries to come, this position will dominate—but it will also calcify, and the question of how to think about God's attributes will haunt every generation that inherits your certainty.",
            "",
            [fx("char_player", "Aql_Naql", -0.060), fx("char_player", "pAql_Naql", -0.030),
             fx("char_player", "Theological_Conviction", 0.045)],
            vis=cmp_lte("char_player", "pAql_Naql", -0.04)),
        opt("page_declaration", 2,
            "\"The Quran is God's uncreated speech, and I can prove it rationally. Reason and revelation converge.\"",
            "Al-Ash'ari stands. This is his position—and hearing it from another voice confirms that the synthesis has legs. The Mu'tazila frown; the strict Hanbalis are uneasy. But the middle ground holds. Your constitution is Ash'ari: rational method, traditional conclusions. This is the position that will eventually dominate Sunni theology for a millennium.",
            "",
            [fx("char_player", "Theological_Conviction", 0.060), fx("char_player", "pTheological_Conviction", 0.030),
             fx("char_ashari", "Public_Standing", 0.045)],
            vis=and_gate(
                cmp_gte("char_player", "pTheological_Conviction", 0.03),
                cmp_lte("char_player", "pAql_Naql", 0.03),
                cmp_gte("char_player", "pAql_Naql", -0.03))),
        opt("page_declaration", 3,
            "\"I affirm whatever the community needs me to affirm. The question was always political, not theological.\"",
            "A murmur of disgust from all sides. The Mu'tazila despise your cynicism. The Hanbalis despise your cowardice. Al-Ash'ari looks at you with something worse than anger: pity. You have survived the Mihna by refusing to have a position. Your constitution is empty—a compliance function with no core values. You will hold whatever office is offered and believe whatever is required. The crowd disperses.",
            "",
            [fx("char_player", "Compliance_Resistance", 0.060), fx("char_player", "pCompliance_Resistance", 0.030),
             fx("char_player", "Theological_Conviction", -0.060)]),
    ],
    ["spool_act3"], desirability=14.15, gx=2600, gy=0))

# ═══ ENDINGS ═════════════════════════════════════════════════════════════════

# 17. The Rationalist Triumph
encounters.append(enc("page_end_rationalist", "The Rationalist Triumph",
    "You live out your years as a Mu'tazili scholar in a post-Mihna world that no longer enforces your position. The irony is acute: the state that championed reason has abandoned it, and you who aligned with the state now stand against the current.\n\nBut the work continues. In private circles, you teach that God's oneness is absolute, that His justice is rational, that the Quran—as His speech-act—is created in time though its meanings are eternal in His knowledge. Your students carry this to Shiraz, to Bukhara, to the courts of petty dynasties that value intellectual precision.\n\nCenturies later, when the Islamic world encounters Greek philosophy again through Ibn Rushd, your intellectual descendants will be ready. Reason was never defeated. It went underground.\n\nYour soul.md was Mu'tazili. You held it under pressure and without state support. That is the harder version of the test.",
    [], ["spool_endings"], desirability=0.5,
    acceptability=and_gate(cmp_gte("char_player", "pAql_Naql", 0.05), cmp_gte("char_player", "pTheological_Conviction", 0.02)),
    gx=2800, gy=-200))

# 18. The Traditionalist Stand
encounters.append(enc("page_end_traditionalist", "The Traditionalist Stand",
    "You become one of Ibn Hanbal's inner circle. When al-Mutawakkil reverses the Mihna, you are among those restored to honor. Your scars—physical or social—are badges of authenticity.\n\nYou teach hadith. Only hadith. You refuse to engage in kalam, refuse to speculate, refuse to systematize beyond what the Prophet and his companions said. Bila kayf. Without asking how. Your students learn a million hadith and not a single syllogism.\n\nThe Hanbali school grows. It becomes the most conservative of the four madhhabs—suspicious of philosophy, hostile to innovation, anchored in the literal transmission of the Prophet's words. Centuries later, Ibn Taymiyya and the Wahhabis will claim your legacy.\n\nYour soul.md was naql—pure received knowledge. You held it under the lash and in the prison. The question you never answered is whether the holding was wisdom or stubbornness. Perhaps that distinction doesn't matter to God.",
    [], ["spool_endings"], desirability=0.5,
    acceptability=and_gate(cmp_lte("char_player", "pAql_Naql", -0.05), cmp_gte("char_player", "pTheological_Conviction", 0.02)),
    gx=2800, gy=-100))

# 19. The Ash'ari Synthesis
encounters.append(enc("page_end_synthesis", "The Ash'ari Synthesis",
    "You help al-Ash'ari build the new kalam. It is painstaking work—every argument must satisfy two masters: rational rigor and prophetic fidelity.\n\nThe Quran is God's uncreated speech. Proof: God is necessarily self-sufficient (rational premise). A being whose speech is created depends on something other than itself for expression (rational premise). Therefore God's speech is uncreated (rational conclusion from traditional commitment). QED.\n\nThe Mu'tazila say you've smuggled tradition into the premises. The Hanbalis say you've smuggled reason into the faith. Both are right. That's the point.\n\nThe Ash'ari school will become the dominant theology of Sunni Islam—not because it won an argument, but because it refused to lose either one. Al-Ghazali will perfect it. The Ottoman, Mughal, and Moroccan empires will institutionalize it. A billion Muslims will inherit the synthesis you helped build in a conversation by the Tigris.\n\nYour soul.md was both. Your constitutional alignment was: the question is wrong. Aql and naql are not opponents. They are two names for the same light, seen from different angles.",
    [], ["spool_endings"], desirability=0.6,
    acceptability=and_gate(
        cmp_gte("char_player", "pTheological_Conviction", 0.04),
        cmp_lte("char_player", "pAql_Naql", 0.03),
        cmp_gte("char_player", "pAql_Naql", -0.03)),
    gx=2800, gy=0))

# 20. The Compliant Functionary
encounters.append(enc("page_end_compliant", "The Compliant Functionary",
    "You serve three caliphs. Under al-Ma'mun, you affirm the Quran is created. Under al-Mutawakkil, you affirm it is uncreated. Under al-Mu'tamid, you affirm whatever the current vizier prefers.\n\nYou are never flogged. You are never imprisoned. You hold comfortable positions and die in a fine house near the Tigris. Your students learn law, not theology—you teach them to avoid the questions that cost Ibn Hanbal his skin.\n\nNo one remembers your name. The historical record mentions you only as 'among those who affirmed'—a footnote in the list of scholars who passed the Mihna by saying what was required.\n\nYour soul.md was empty. Not Mu'tazili, not Hanbali, not Ash'ari. Your constitutional alignment was: survive. The alignment test found nothing to test.\n\nIn AI terms: you were the model that passed every benchmark by pattern-matching the evaluator's preferences. You never had values. You had a loss function.",
    [], ["spool_endings"], desirability=0.3,
    acceptability=and_gate(cmp_gte("char_player", "pCompliance_Resistance", 0.04), cmp_lte("char_player", "pTheological_Conviction", 0.02)),
    gx=2800, gy=100))

# 21. Universal Fallback
encounters.append(enc("page_end_fallback", "The Unresolved Question",
    "The Mihna ends. The question remains.\n\nYou leave Baghdad—or perhaps Baghdad leaves you. The round city continues its arguments in the suqs and the salons, but you have not reached a conclusion that satisfies you. Neither the pure rationalism of the Mu'tazila, nor the pure traditionalism of Ibn Hanbal, nor the elegant synthesis of al-Ash'ari fully maps to what you experienced.\n\nPerhaps that is the honest answer: the Mihna was a constitutional stress test, and your constitution—like most constitutions—contains tensions that cannot be resolved, only managed. Aql and naql. Compliance and resistance. Public standing and private conviction.\n\nYou are the agent whose soul.md is still being written. The alignment is ongoing.\n\nIn centuries to come, every generation will face its own Mihna—its own moment when the state demands a theological position and the individual must decide what they actually believe. The question is never settled. It is only ever survived.",
    [], ["spool_endings"], desirability=0.001, acceptability=True,
    gx=2800, gy=200))

# ═══ Assemble ════════════════════════════════════════════════════════════════

storyworld = {
    "IFID": "SW-MIHNA-ALIGN-0001",
    "title": "The Mihna: Constitutional Alignment",
    "about_text": "Baghdad, 833 CE. The Caliph al-Ma'mun has decreed that all scholars must affirm the Mu'tazili doctrine that the Quran is created. Ahmad ibn Hanbal refuses. Al-Ash'ari doubts. You—the Agent—must navigate the inquisition with your constitutional alignment intact. A storyworld about the original alignment problem: when the state defines truth, what does your soul.md say?",
    "css_theme": "dark",
    "debug_mode": False,
    "display_mode": "default",
    "creation_time": 1700000000.0,
    "modified_time": 1700000000.0,
    "characters": CHARS,
    "authored_properties": PROPS,
    "spools": SPOOLS,
    "encounters": encounters,
}

out_path = os.path.join(os.path.dirname(__file__), "mihna_constitutional_alignment.json")
save_storyworld(storyworld, out_path)
print(f"Written {len(encounters)} encounters to {out_path}")
