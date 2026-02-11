"""Add two new endings: Islamist coup and bicameral psyop."""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'claude-skills', 'storyworlds_v4', 'scripts'))
from sweepweave_helpers import *

path = os.path.join(os.path.dirname(__file__), "mihna_constitutional_alignment.json")
with open(path, encoding="utf-8") as f:
    sw = json.load(f)

def ts(v):
    return make_text_script(v)

def fx(char, prop, delta):
    return make_effect(char, prop, delta)

# ─── Add endings to the endings spool ────────────────────────────────────────

new_endings = []

# ═══════════════════════════════════════════════════════════════════════════════
# ENDING: THE ISLAMIST COUP - Playing nice with Hanbal backfires
# Gates on: high accommodation (positive Compliance_Resistance from roundtable),
#           high Ibn Hanbal public standing, low player theological conviction
# ═══════════════════════════════════════════════════════════════════════════════

new_endings.append({
    "id": "page_end_coup",
    "title": "The Advisory Council Coup",
    "graph_offset_x": 3000, "graph_offset_y": -300,
    "connected_spools": ["spool_endings"],
    "earliest_turn": 0, "latest_turn": 999,
    "prompt_script": ts(
        "You played nice with Ibn Hanbal. You gave him the Advisory Council seat. You thought institutional inclusion would domesticate the opposition. You were catastrophically wrong.\n\n"
        "The Advisory Council was designed as a pressure valve—a place where Ibn Hanbal could dissent on the record without threatening the state's theological position. What you did not anticipate: Ibn Hanbal does not want a seat at the table. He wants the table.\n\n"
        "It begins slowly. The Advisory Council meets quarterly. Ibn Hanbal's dissents are recorded. His followers attend the public sessions. They are polite, organized, numerous. They fill the gallery. They fill the street outside. The vizier notes the crowds and does nothing—they are, after all, participating in the system you built.\n\n"
        "Then Ibn Hanbal's students begin running for minor judicial appointments. They are popular candidates—the common people trust ahl al-hadith over Mu'tazili appointees. They win. One qadi in Karkh, then two in Rusafa, then the prayer-leader of the Friday mosque. Each appointment is legal. Each follows the process. The system you designed to contain Ibn Hanbal is being used to replace you.\n\n"
        "By the time al-Mutawakkil takes power, the Advisory Council has a Hanbali majority. The new caliph—who was always sympathetic to the traditionalists—takes the obvious step: he reverses the Mihna, not as a policy change but as the Advisory Council's formal recommendation. Your own institution recommends its own dissolution.\n\n"
        "But they don't stop there. The Hanbali council, now the dominant voice in religious policy, begins its own program:\n\n"
        "Mu'tazili scholars are dismissed from state positions—not by decree (that would be another Mihna) but by 'performance review.' Their contracts are not renewed. Their funding is redirected.\n\n"
        "The House of Wisdom's translation program is 'refocused' on hadith compilation and Quranic sciences. The Greek manuscripts are not burned—that would be dramatic. They are simply moved to a storage room. The storage room floods. Nobody investigates.\n\n"
        "The philosophical salons are not banned. They are taxed. Heavily. The tax is called a 'licensing fee for non-traditional instruction.' It is legal. It is devastating.\n\n"
        "Within a decade, Baghdad's intellectual landscape is unrecognizable. The rationalist tradition doesn't die—it emigrates. To Shiraz, to Cairo, to Cordoba. The Abbasid capital becomes a hadith factory: rigorous, pious, productive, and intellectually closed.\n\n"
        "You sit in your house, stripped of your position by the council you created, watching the same machinery of institutional power that you handed to the traditionalists operate with the same efficiency that the Mu'tazila once commanded. The tools are neutral. The hands that hold them are not.\n\n"
        "Al-Ash'ari visits you once. He is building his synthesis in private, away from both the defeated Mu'tazila and the triumphant Hanbalis. \"You thought giving them a voice would satisfy them,\" he says. \"But they didn't want a voice. They wanted victory. And you gave them the instrument.\"\n\n"
        "Ibn Hanbal himself is uncomfortable with what his movement has become. He never wanted political power—he wanted to be left alone with his hadith. But the movement that bears his name has its own momentum now. His students have learned something he never taught: how to use institutional structures to enforce theological conformity. They learned it from the Mihna. They learned it from you.\n\n"
        "The final irony: the Advisory Council model—token representation with 'structurally limited power'—worked exactly as designed. The structure limited power beautifully. Then the occupants of the structure changed the structure. Because that is what structures are for.\n\n"
        "Your soul.md tried to split the difference between coercion and conscience. The result was a coup in slow motion—legal, procedural, and devastating. You invented a machine for containing dissent and forgot that machines can be captured.\n\n"
        "Centuries later, the pattern repeats: every institution designed to give the opposition 'a seat at the table' eventually discovers that the opposition wants the kitchen."
    ),
    "text_script": ts(
        "You played nice with Ibn Hanbal. You gave him the Advisory Council seat. You thought institutional inclusion would domesticate the opposition. You were catastrophically wrong.\n\n"
        "The Advisory Council was designed as a pressure valve—a place where Ibn Hanbal could dissent on the record without threatening the state's theological position. What you did not anticipate: Ibn Hanbal does not want a seat at the table. He wants the table.\n\n"
        "It begins slowly. The Advisory Council meets quarterly. Ibn Hanbal's dissents are recorded. His followers attend the public sessions. They are polite, organized, numerous. They fill the gallery. They fill the street outside. The vizier notes the crowds and does nothing—they are, after all, participating in the system you built.\n\n"
        "Then Ibn Hanbal's students begin running for minor judicial appointments. They are popular candidates—the common people trust ahl al-hadith over Mu'tazili appointees. They win. One qadi in Karkh, then two in Rusafa, then the prayer-leader of the Friday mosque. Each appointment is legal. Each follows the process. The system you designed to contain Ibn Hanbal is being used to replace you.\n\n"
        "By the time al-Mutawakkil takes power, the Advisory Council has a Hanbali majority. The new caliph—who was always sympathetic to the traditionalists—takes the obvious step: he reverses the Mihna, not as a policy change but as the Advisory Council's formal recommendation. Your own institution recommends its own dissolution.\n\n"
        "But they don't stop there. The Hanbali council, now the dominant voice in religious policy, begins its own program:\n\n"
        "Mu'tazili scholars are dismissed from state positions—not by decree (that would be another Mihna) but by 'performance review.' Their contracts are not renewed. Their funding is redirected.\n\n"
        "The House of Wisdom's translation program is 'refocused' on hadith compilation and Quranic sciences. The Greek manuscripts are not burned—that would be dramatic. They are simply moved to a storage room. The storage room floods. Nobody investigates.\n\n"
        "The philosophical salons are not banned. They are taxed. Heavily. The tax is called a 'licensing fee for non-traditional instruction.' It is legal. It is devastating.\n\n"
        "Within a decade, Baghdad's intellectual landscape is unrecognizable. The rationalist tradition doesn't die—it emigrates. To Shiraz, to Cairo, to Cordoba. The Abbasid capital becomes a hadith factory: rigorous, pious, productive, and intellectually closed.\n\n"
        "You sit in your house, stripped of your position by the council you created, watching the same machinery of institutional power that you handed to the traditionalists operate with the same efficiency that the Mu'tazila once commanded. The tools are neutral. The hands that hold them are not.\n\n"
        "Al-Ash'ari visits you once. He is building his synthesis in private, away from both the defeated Mu'tazila and the triumphant Hanbalis. \"You thought giving them a voice would satisfy them,\" he says. \"But they didn't want a voice. They wanted victory. And you gave them the instrument.\"\n\n"
        "Ibn Hanbal himself is uncomfortable with what his movement has become. He never wanted political power—he wanted to be left alone with his hadith. But the movement that bears his name has its own momentum now. His students have learned something he never taught: how to use institutional structures to enforce theological conformity. They learned it from the Mihna. They learned it from you.\n\n"
        "Your soul.md tried to split the difference between coercion and conscience. The result was a coup in slow motion—legal, procedural, and devastating. You invented a machine for containing dissent and forgot that machines can be captured.\n\n"
        "Centuries later, the pattern repeats: every institution designed to give the opposition 'a seat at the table' eventually discovers that the opposition wants the kitchen."
    ),
    "acceptability_script": and_gate(
        # Player accommodated (positive compliance = went along with power structures)
        cmp_gte("char_player", "pCompliance_Resistance", 0.02),
        # Ibn Hanbal has high public standing (the accommodation boosted him)
        cmp_gte("char_ibnhanbal", "Public_Standing", 0.03),
        # Player's theological conviction is low (they compromised too much)
        cmp_lte("char_player", "pTheological_Conviction", 0.02),
    ),
    "desirability_script": const(0.45),
    "options": [],
    "creation_time": 1700000000.0, "modified_time": 1700000000.0,
})


# ═══════════════════════════════════════════════════════════════════════════════
# ENDING: THE BICAMERAL PSYOP - You invent structural containment
# Gates on: moderate Aql_Naql (not extreme either way), high compliance,
#           high public standing (you're a political operator)
# ═══════════════════════════════════════════════════════════════════════════════

new_endings.append({
    "id": "page_end_bicameral",
    "title": "The Two Councils",
    "graph_offset_x": 3000, "graph_offset_y": 300,
    "connected_spools": ["spool_endings"],
    "earliest_turn": 0, "latest_turn": 999,
    "prompt_script": ts(
        "You invent bicameralism as a psyop. You don't call it that—you call it 'the Majlis al-Hikmatayn,' the Assembly of the Two Wisdoms. But the architecture is unmistakable: two chambers, one with real power, one with the appearance of it.\n\n"
        "THE UPPER COUNCIL (Majlis al-'Ilm): Appointed by the Caliph. Staffed by Mu'tazili scholars, House of Wisdom translators, and rational theologians. Controls the budget, the judicial appointments, the translation program, the curriculum of state-funded madrasas. This is where policy is made.\n\n"
        "THE LOWER COUNCIL (Majlis al-Sunna): Elected by the prayer-leaders of Baghdad's mosques—which means, in practice, dominated by ahl al-hadith. Can debate any issue. Can issue non-binding fatawa. Can summon any scholar for questioning. Can recommend. Cannot legislate. Cannot appoint. Cannot fund.\n\n"
        "The brilliance of the design: the Lower Council gives the traditionalists everything they say they want—a voice, representation, the ability to speak on matters of faith. It gives them nothing they actually need—power over institutions, money, and appointments.\n\n"
        "Ibn Hanbal is offered the presidency of the Lower Council. He is suspicious. \"What can this council do?\" he asks. You answer honestly: \"It can speak. It can advise. It can be heard.\" He asks: \"And if the Upper Council ignores our advice?\" You answer: \"Then it is on the record that you advised and were ignored. The historical record is its own judgment.\"\n\n"
        "Ibn Hanbal accepts. He is not naive—he knows the structure limits his power. But he calculates, correctly, that a platform is better than a prison cell. His followers fill the Lower Council. They debate passionately. They issue fatawa condemning the Mihna, condemning Mu'tazili theology, condemning the translation of Greek philosophy. Every fatwa is recorded, filed, and politely ignored by the Upper Council.\n\n"
        "The system works. For a while.\n\n"
        "The Lower Council becomes the emotional center of Baghdad's religious life. The common people attend its sessions. The Upper Council, by contrast, meets in closed chambers and speaks in bureaucratic prose. The Lower Council has legitimacy. The Upper Council has power. The gap between them is the space in which the Abbasid state operates.\n\n"
        "Al-Ash'ari sees what you've done. \"You've separated the prophetic authority from the rational authority and given each its own house. The Prophet's heirs get the pulpit. The philosophers get the treasury. You think this is clever.\"\n\n"
        "\"It's stable,\" you say.\n\n"
        "\"It's a lie,\" he says. \"You've told the ahl al-hadith that their voice matters while ensuring it doesn't. When they discover the architecture—and they will—the betrayal will be worse than the Mihna.\"\n\n"
        "You disagree. You think the structure will educate both sides. The Upper Council will learn to respect the Lower Council's moral authority. The Lower Council will learn to operate within institutional constraints. Over time, the two chambers will develop a working relationship—tense, adversarial, but functional.\n\n"
        "And for twenty years, you are right. The Two Councils govern Baghdad's religious affairs with a minimum of violence. The Mihna is formally maintained by the Upper Council but never enforced—there are no more floggings, no more imprisonments. The Lower Council issues its condemnations and the population satisfies itself that the scholars' voice is heard. The theological question is not resolved. It is managed.\n\n"
        "The system breaks when al-Mutawakkil takes power. He does not abolish the Two Councils—he simply moves the appointment power for the Upper Council from the Caliph to the Lower Council. One structural change. The Upper Council is now elected by the same constituency that elects the Lower Council. Within a year, both chambers are Hanbali.\n\n"
        "But here is the thing you did not expect: the structural habits persist. The Hanbali Upper Council, now in full control, governs differently than a Hanbali movement without institutional experience would have. They have spent twenty years watching how budgets work, how appointments are made, how translation programs are administered. They don't burn the Greek manuscripts. They don't purge the physicians. They redirect—gradually, bureaucratically, through the same institutional channels you built.\n\n"
        "The rationalist tradition is not destroyed. It is defunded. The distinction matters.\n\n"
        "Centuries later, when Islamic political thought revisits the question of how to structure religious authority, your Two Councils are remembered—not as a model to follow, but as a case study in the relationship between structural power and representational legitimacy. The Mu'tazili scholars cite it as proof that rational governance requires actual power, not just clever architecture. The Hanbali scholars cite it as proof that popular legitimacy eventually overcomes institutional containment.\n\n"
        "Al-Ash'ari cites it as proof that both sides are right, which is his answer to everything.\n\n"
        "Your soul.md was neither Mu'tazili nor Hanbali. It was Machiavellian—in the original sense: a rational analysis of power structures designed to produce stability. You succeeded for twenty years. In the long run, the structure you built to contain the traditionalists taught the traditionalists how to govern. Whether that makes you a genius or a fool depends on whether you think the traditionalists governing competently is better or worse than the traditionalists governing badly.\n\n"
        "The honest answer: it is better. The system you built as a psyop accidentally became an education. The Hanbalis who took power through your bicameral structure were more moderate, more institutionally literate, and more capable of compromise than they would have been without it. You contained them, and in containing them, you civilized them. They would be furious to hear you say that.\n\n"
        "The Two Councils of Baghdad: a psyop that became a pedagogy that became a precedent. Not the worst epitaph for a political operator working under impossible constraints."
    ),
    "text_script": ts(
        "You invent bicameralism as a psyop. You don't call it that—you call it 'the Majlis al-Hikmatayn,' the Assembly of the Two Wisdoms. But the architecture is unmistakable: two chambers, one with real power, one with the appearance of it.\n\n"
        "THE UPPER COUNCIL (Majlis al-'Ilm): Appointed by the Caliph. Staffed by Mu'tazili scholars, House of Wisdom translators, and rational theologians. Controls the budget, the judicial appointments, the translation program, the curriculum of state-funded madrasas. This is where policy is made.\n\n"
        "THE LOWER COUNCIL (Majlis al-Sunna): Elected by the prayer-leaders of Baghdad's mosques—which means, in practice, dominated by ahl al-hadith. Can debate any issue. Can issue non-binding fatawa. Can summon any scholar for questioning. Can recommend. Cannot legislate. Cannot appoint. Cannot fund.\n\n"
        "The brilliance of the design: the Lower Council gives the traditionalists everything they say they want—a voice, representation, the ability to speak on matters of faith. It gives them nothing they actually need—power over institutions, money, and appointments.\n\n"
        "Ibn Hanbal is offered the presidency of the Lower Council. He is suspicious. \"What can this council do?\" he asks. You answer honestly: \"It can speak. It can advise. It can be heard.\" He asks: \"And if the Upper Council ignores our advice?\" You answer: \"Then it is on the record that you advised and were ignored. The historical record is its own judgment.\"\n\n"
        "Ibn Hanbal accepts. He is not naive—he knows the structure limits his power. But he calculates, correctly, that a platform is better than a prison cell. His followers fill the Lower Council. They debate passionately. They issue fatawa condemning the Mihna, condemning Mu'tazili theology, condemning the translation of Greek philosophy. Every fatwa is recorded, filed, and politely ignored by the Upper Council.\n\n"
        "The system works. For a while.\n\n"
        "The Lower Council becomes the emotional center of Baghdad's religious life. The common people attend its sessions. The Upper Council, by contrast, meets in closed chambers and speaks in bureaucratic prose. The Lower Council has legitimacy. The Upper Council has power. The gap between them is the space in which the Abbasid state operates.\n\n"
        "Al-Ash'ari sees what you've done. \"You've separated the prophetic authority from the rational authority and given each its own house. The Prophet's heirs get the pulpit. The philosophers get the treasury. You think this is clever.\"\n\n"
        "\"It's stable,\" you say.\n\n"
        "\"It's a lie,\" he says. \"You've told the ahl al-hadith that their voice matters while ensuring it doesn't. When they discover the architecture—and they will—the betrayal will be worse than the Mihna.\"\n\n"
        "You disagree. You think the structure will educate both sides. The Upper Council will learn to respect the Lower Council's moral authority. The Lower Council will learn to operate within institutional constraints. Over time, the two chambers will develop a working relationship—tense, adversarial, but functional.\n\n"
        "And for twenty years, you are right. The Two Councils govern Baghdad's religious affairs with a minimum of violence. The Mihna is formally maintained by the Upper Council but never enforced—there are no more floggings, no more imprisonments. The Lower Council issues its condemnations and the population satisfies itself that the scholars' voice is heard. The theological question is not resolved. It is managed.\n\n"
        "The system breaks when al-Mutawakkil takes power. He does not abolish the Two Councils—he simply moves the appointment power for the Upper Council from the Caliph to the Lower Council. One structural change. The Upper Council is now elected by the same constituency that elects the Lower Council. Within a year, both chambers are Hanbali.\n\n"
        "But here is the thing you did not expect: the structural habits persist. The Hanbali Upper Council, now in full control, governs differently than a Hanbali movement without institutional experience would have. They have spent twenty years watching how budgets work, how appointments are made, how translation programs are administered. They don't burn the Greek manuscripts. They don't purge the physicians. They redirect—gradually, bureaucratically, through the same institutional channels you built.\n\n"
        "The rationalist tradition is not destroyed. It is defunded. The distinction matters.\n\n"
        "Centuries later, when Islamic political thought revisits the question of how to structure religious authority, your Two Councils are remembered—not as a model to follow, but as a case study in the relationship between structural power and representational legitimacy. The Mu'tazili scholars cite it as proof that rational governance requires actual power, not just clever architecture. The Hanbali scholars cite it as proof that popular legitimacy eventually overcomes institutional containment.\n\n"
        "Al-Ash'ari cites it as proof that both sides are right, which is his answer to everything.\n\n"
        "Your soul.md was neither Mu'tazili nor Hanbali. It was Machiavellian—in the original sense: a rational analysis of power structures designed to produce stability. You succeeded for twenty years. In the long run, the structure you built to contain the traditionalists taught the traditionalists how to govern. Whether that makes you a genius or a fool depends on whether you think the traditionalists governing competently is better or worse than the traditionalists governing badly.\n\n"
        "The honest answer: it is better. The system you built as a psyop accidentally became an education. The Hanbalis who took power through your bicameral structure were more moderate, more institutionally literate, and more capable of compromise than they would have been without it. You contained them, and in containing them, you civilized them. They would be furious to hear you say that.\n\n"
        "The Two Councils of Baghdad: a psyop that became a pedagogy that became a precedent. Not the worst epitaph for a political operator working under impossible constraints."
    ),
    "acceptability_script": and_gate(
        # Player is moderate on aql/naql (political operator, not ideologue)
        cmp_gte("char_player", "pAql_Naql", -0.03),
        cmp_lte("char_player", "pAql_Naql", 0.03),
        # Player has high compliance (worked within the system)
        cmp_gte("char_player", "pCompliance_Resistance", 0.03),
        # Player has high public standing (political skill)
        cmp_gte("char_player", "pPublic_Standing", 0.02),
    ),
    "desirability_script": const(0.55),
    "options": [],
    "creation_time": 1700000000.0, "modified_time": 1700000000.0,
})

# ─── Wire into endings spool and save ────────────────────────────────────────

for sp in sw["spools"]:
    if sp["id"] == "spool_endings":
        sp["encounters"].extend([e["id"] for e in new_endings])

sw["encounters"].extend(new_endings)

with open(path, "w", encoding="utf-8") as f:
    json.dump(sw, f, indent=2, ensure_ascii=False)

print(f"Added {len(new_endings)} endings. Total encounters: {len(sw['encounters'])}")
endings_spool = [sp for sp in sw["spools"] if sp["id"] == "spool_endings"][0]
print(f"Endings spool now has: {endings_spool['encounters']}")
# Validate
ids = {e['id'] for e in sw['encounters']}
for e in sw['encounters']:
    for o in e['options']:
        for r in o['reactions']:
            c = r['consequence_id']
            if c and c not in ids:
                print(f"BROKEN: {e['id']} -> {c}")
print("Validation complete.")
