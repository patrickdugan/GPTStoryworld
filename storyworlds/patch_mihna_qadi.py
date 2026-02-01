"""Add qadi bench encounters to the Mihna storyworld."""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'claude-skills', 'storyworlds_v4', 'scripts'))
from sweepweave_helpers import *

path = os.path.join(os.path.dirname(__file__), "mihna_constitutional_alignment.json")
with open(path, encoding="utf-8") as f:
    sw = json.load(f)

# ─── Add the qadi spool ─────────────────────────────────────────────────────

sw["spools"].append({
    "id": "spool_qadi",
    "spool_type": "General",
    "spool_name": "Qadi's Bench",
    "creation_index": 4,
    "creation_time": 1700000000.0,
    "modified_time": 1700000000.0,
    "starts_active": True,
    "encounters": [],  # filled below
})

def ts(v):
    return make_text_script(v)

def fx(char, prop, delta):
    return make_effect(char, prop, delta)

def qadi_enc(page_id, title, text, options, desirability, gx, gy):
    return {
        "id": page_id,
        "title": title,
        "graph_offset_x": gx, "graph_offset_y": gy,
        "connected_spools": ["spool_qadi"],
        "earliest_turn": 0, "latest_turn": 999,
        "prompt_script": ts(text),
        "text_script": ts(text),
        "acceptability_script": True,
        "desirability_script": const(desirability),
        "options": options,
        "creation_time": 1700000000.0, "modified_time": 1700000000.0,
    }

def qopt(page_id, idx, text, rxn_text, effects, vis=True, des=1.0):
    o = make_option(page_id, idx, text, vis)
    r = make_reaction(page_id, idx, 0, rxn_text, "", effects, des)
    o["reactions"] = [r]
    return o

qadi_encounters = []

# ═══════════════════════════════════════════════════════════════════════════════
# 1. CHILD CUSTODY AFTER DIVORCE
# ═══════════════════════════════════════════════════════════════════════════════

qadi_encounters.append(qadi_enc("page_qadi_custody", "The Mother's Claim",
    "A woman named Fatima stands before your bench. Her husband Khalid has divorced her—talaq, irrevocable—and now claims sole custody of their two children, a boy of four and a girl of six. He cites the traditional hadith: the father has the right to custody after the age of weaning.\n\nFatima weeps. \"He divorced me for a younger wife. He was absent for months trading in Basra. I raised them alone. Now he wants them because his new wife wants servants, not children.\"\n\nKhalid's advocate argues: \"The hadith is clear. The father's household provides lineage, education, and inheritance. The mother's right ends at weaning.\"\n\nThe Mu'tazili position weighs maslaha—the welfare of the child—as a rational principle that can override specific hadith application. The traditionalist position holds to the transmitted ruling. The question before you: whose framework governs your bench?",
    [
        qopt("page_qadi_custody", 0,
            "Rule for the mother: the children's welfare (maslaha) is the governing principle, and reason shows they thrive with her.",
            "You cite the Quranic principle of la darar—no harm. The children know their mother; removing them causes measurable harm. You argue that the hadith establishes a default, not an absolute—and that the default yields when the rational assessment of welfare demands it.\n\nKhalid's advocate protests: \"This is Mu'tazili innovation! The qadi substitutes his reason for the Prophet's ruling!\" The crowd murmurs. Fatima clutches her children. Your ruling holds—but it has been noticed. The traditionalist scholars will cite this case when they argue that the Mihna produces judges who override the Sunna.",
            [fx("char_player", "Aql_Naql", 0.045), fx("char_player", "pAql_Naql", 0.022),
             fx("char_player", "Public_Standing", -0.024),
             fx("char_amma", "Aql_Naql", 0.024),
             fx("char_player", "Theological_Conviction", 0.024)]),
        qopt("page_qadi_custody", 1,
            "Rule for the father: the hadith is clear, and a qadi's role is to apply the transmitted ruling, not to reason beyond it.",
            "You cite the hadith and rule for Khalid. Fatima collapses. The children are led away by a man they barely know.\n\nIbn Hanbal's followers nod approvingly—the Sunna was followed. But the water-carrier in the gallery, who knows Fatima's family, spits on the floor as he leaves. Al-Amma does not always align with the scholars. Your ruling is legally sound and humanly devastating. The question you do not ask—because bila kayf forbids it—is whether God intended this specific outcome when the Prophet spoke those words.",
            [fx("char_player", "Aql_Naql", -0.045), fx("char_player", "pAql_Naql", -0.022),
             fx("char_player", "Public_Standing", -0.024),
             fx("char_amma", "Compliance_Resistance", -0.024),
             fx("char_player", "Theological_Conviction", 0.024)]),
        qopt("page_qadi_custody", 2,
            "Split custody: the girl stays with her mother until marriage age, the boy transfers to the father at seven—and require Khalid to fund the mother's household.",
            "You invoke both the hadith and the principle of equity. The boy will eventually join his father's household—the traditional ruling is preserved—but not yet, and not without conditions. Khalid must provide housing and maintenance for Fatima as long as she has custody. The girl remains with her mother, as the Hanafi school permits.\n\nNeither side is satisfied. Both sides can live with it. Al-Ash'ari, who has been observing from the gallery, catches your eye. This is what synthesis looks like at ground level: ugly, partial, pragmatic, and more just than either pure position.",
            [fx("char_player", "Aql_Naql", 0.012), fx("char_player", "pAql_Naql", 0.006),
             fx("char_player", "Public_Standing", 0.024), fx("char_player", "pPublic_Standing", 0.012),
             fx("char_player", "Theological_Conviction", 0.024), fx("char_player", "pTheological_Conviction", 0.012)]),
    ],
    desirability=13.0, gx=400, gy=-300))


# ═══════════════════════════════════════════════════════════════════════════════
# 2. WIFE-BEATING (DARABA - 4:34)
# ═══════════════════════════════════════════════════════════════════════════════

qadi_encounters.append(qadi_enc("page_qadi_daraba", "The Bruise and the Verse",
    "A woman named Zaynab appears with bruises on her arms and face. Her husband Mas'ud stands beside her, unrepentant. \"She disobeyed me,\" he says. \"She left the house without permission to visit her mother. I disciplined her as the Quran permits.\"\n\nHe cites Sura 4:34: '...and strike them (wa-dribuhunna).' His reading is literal: the verse permits physical discipline of a disobedient wife, after admonishment and separation of beds have failed.\n\nZaynab says: \"He broke my wrist last month. He strikes me when his business fails. This is not discipline—this is rage.\"\n\nThe Mu'tazili scholars argue that daraba must be read in light of God's justice ('adl)—an essential divine attribute. A just God cannot command harm. Therefore daraba means 'turn away from' or 'strike lightly with a miswak.' The traditionalists read the verse as written, though most add that the Prophet said the striking must not leave a mark.\n\nThe crowd watches. This case will set precedent.",
    [
        qopt("page_qadi_daraba", 0,
            "Rule that daraba in 4:34 cannot mean injurious striking. God's justice ('adl) makes the literalist reading incoherent. Grant Zaynab a khul' divorce with full mahr.",
            "You deliver a ruling that will be quoted for decades—and not always favorably. \"The Mu'tazili principle of divine justice requires that no Quranic verse be read in a manner that produces injustice. God commands the good and forbids the evil—this is rational necessity. A reading of daraba that permits a man to break his wife's bones contradicts the character of the Lawgiver. I rule that daraba here means separation or symbolic gesture, and that Mas'ud's violence constitutes darar—harm—entitling Zaynab to dissolution of the marriage with retention of her full mahr.\"\n\nMas'ud is led away shouting. The traditionalist scholars write letters of protest. But the women in the gallery—and there are always women in the gallery—remember this ruling.",
            [fx("char_player", "Aql_Naql", 0.060), fx("char_player", "pAql_Naql", 0.030),
             fx("char_player", "Public_Standing", 0.024),
             fx("char_amma", "Aql_Naql", 0.045),
             fx("char_player", "Theological_Conviction", 0.045), fx("char_player", "pTheological_Conviction", 0.022)]),
        qopt("page_qadi_daraba", 1,
            "Uphold the husband's right to light discipline per the verse, but rule that Mas'ud exceeded it. Fine him and warn him—but do not dissolve the marriage.",
            "You walk the traditional line. \"The verse permits discipline—this is the zahir, the plain text. But the Prophet, peace be upon him, said: 'The best of you are the best to their wives.' And he said: 'Do not strike the face, do not leave a mark.' Mas'ud has exceeded every limit. He is fined twenty dinars, payable to Zaynab, and if he strikes her again, I will dissolve the marriage myself.\"\n\nZaynab is returned to a man who broke her wrist, with twenty dinars and a warning. The traditionalists approve your textual fidelity. The Mu'tazili scholars ask: is this what justice looks like? You do not answer, because you are not sure.",
            [fx("char_player", "Aql_Naql", -0.024), fx("char_player", "pAql_Naql", -0.012),
             fx("char_player", "Public_Standing", -0.024),
             fx("char_amma", "Compliance_Resistance", -0.024),
             fx("char_player", "Theological_Conviction", 0.024)]),
        qopt("page_qadi_daraba", 2,
            "Investigate the marriage itself: call witnesses, examine the pattern of violence, and rule based on the totality of evidence—not one verse in isolation.",
            "You spend three days hearing testimony. Neighbors confirm years of violence. Zaynab's mother testifies she begged Mas'ud to stop. A doctor—a Nestorian Christian from the bimaristan—describes the healed fractures.\n\nYour ruling: \"No single verse governs a marriage. The Quran commands living with wives in kindness—bi'l-ma'ruf (4:19). It commands not retaining wives to cause harm—la tumsikuhunna diraran (2:231). The totality of the Quranic ethic, read together, forbids what Mas'ud has done. I dissolve this marriage. Zaynab retains her mahr and custody of the children.\"\n\nThis is neither purely rational nor purely textual. It is jurisprudence—the art of reading many texts together. Al-Ash'ari nods from the gallery. The synthesis lives in the details.",
            [fx("char_player", "Aql_Naql", 0.024), fx("char_player", "pAql_Naql", 0.012),
             fx("char_player", "Public_Standing", 0.045), fx("char_player", "pPublic_Standing", 0.022),
             fx("char_player", "Theological_Conviction", 0.045), fx("char_player", "pTheological_Conviction", 0.022)]),
    ],
    desirability=12.5, gx=400, gy=-200))


# ═══════════════════════════════════════════════════════════════════════════════
# 3. THE UMM WALAD (SLAVE MOTHER'S STATUS)
# ═══════════════════════════════════════════════════════════════════════════════

qadi_encounters.append(qadi_enc("page_qadi_umm_walad", "The Slave Mother's Freedom",
    "A merchant named Harith has died. His estate includes Layla, an umm walad—a slave woman who bore him a son. Under the established ruling of Umar ibn al-Khattab, an umm walad cannot be sold and is freed upon her master's death.\n\nBut Harith's brother Yusuf challenges this. \"Umar's ruling is ijtihad—his personal judgment. It is not in the Quran or the Sunna. The Prophet himself allowed the sale of umm walad. I want Layla sold to settle Harith's debts.\"\n\nHe is technically correct: there is a hadith narrated by Jabir that the Prophet permitted such sales. Umar overrode it by his own reasoning.\n\nLayla stands before you with her son—a free boy, since his father was free. If you sell her, the child keeps his freedom but loses his mother. If you free her, Harith's creditors lose their claim.\n\nThe Mu'tazili principle: God's justice requires that motherhood be protected. Reason shows that separating a mother from her child produces harm that outweighs any debt.\n\nThe traditionalist principle: follow the strongest hadith. If the Prophet permitted it, Umar's override was ijtihad that can be reversed.\n\nThe question beneath the question: can a caliph's or companion's reasoning override a prophetic hadith?",
    [
        qopt("page_qadi_umm_walad", 0,
            "Free Layla: God's justice ('adl) and rational maslaha both demand it. Umar's reasoning was sound because it was grounded in a higher principle than the specific hadith.",
            "You rule that Umar's ijtihad was not arbitrary—it was the application of the Quranic principle that no bearer of burdens bears another's burden (6:164). The child's welfare, the mother's dignity, and the general principle of istihsan (juristic preference for equity) all converge.\n\n\"The hadith of Jabir reports a permission, not a command. Permissions can be restricted by higher principles. Umar restricted it. I uphold the restriction.\"\n\nLayla is freed. Harith's creditors are furious. Yusuf appeals to the chief qadi—a Mu'tazili appointee who upholds your ruling. The case becomes a flashpoint: is this rational justice or judicial overreach? The answer depends entirely on your theology.",
            [fx("char_player", "Aql_Naql", 0.045), fx("char_player", "pAql_Naql", 0.022),
             fx("char_player", "Public_Standing", 0.024), fx("char_player", "pPublic_Standing", 0.012),
             fx("char_amma", "Aql_Naql", 0.024),
             fx("char_player", "Theological_Conviction", 0.024)]),
        qopt("page_qadi_umm_walad", 1,
            "Allow the sale: the hadith of Jabir is explicit, and a companion's ijtihad—even Umar's—cannot override the Prophet's word.",
            "You rule for Yusuf. Layla is to be sold, with the proceeds paying Harith's debts. The son—free, fatherless, and now motherless—is placed with Harith's family.\n\nLayla does not scream. She holds her son's face in her hands for a long moment, then lets go. The slave market in Karkh will have her by Friday.\n\nIbn Hanbal's students cite your ruling approvingly: the hadith was followed. But even among the traditionalists, there is discomfort. The elderly scholar who taught you hadith pulls you aside: \"The ruling is correct. I wish it were also merciful.\" He does not explain how both can be true. Bila kayf.",
            [fx("char_player", "Aql_Naql", -0.045), fx("char_player", "pAql_Naql", -0.022),
             fx("char_player", "Public_Standing", -0.045), fx("char_player", "pPublic_Standing", -0.022),
             fx("char_amma", "Compliance_Resistance", -0.024),
             fx("char_player", "Theological_Conviction", 0.024)]),
        qopt("page_qadi_umm_walad", 2,
            "Free Layla but compensate the creditors from the public treasury (bayt al-mal). The state that enforces the Mihna can also enforce mercy.",
            "A creative ruling that satisfies no jurist cleanly. You argue that the bayt al-mal exists precisely for cases where justice and debt collide. The state's obligation to protect the vulnerable (a Quranic principle both sides accept) trumps its obligation to enforce private debts.\n\nThe creditors are paid. Layla is freed. The treasury official protests the expenditure. Al-Ma'mun's vizier, hearing of the case, is amused: \"A qadi who spends the caliph's money on a slave woman's freedom. At least he's consistent—he uses reason for everything.\"\n\nYour ruling establishes no clear precedent. It solves one case beautifully. The next qadi will face the same question with an empty treasury.",
            [fx("char_player", "Aql_Naql", 0.024), fx("char_player", "pAql_Naql", 0.012),
             fx("char_player", "Public_Standing", 0.045), fx("char_player", "pPublic_Standing", 0.022),
             fx("char_player", "Compliance_Resistance", 0.024),
             fx("char_player", "Theological_Conviction", 0.024), fx("char_player", "pTheological_Conviction", 0.012)]),
    ],
    desirability=12.0, gx=400, gy=-100))


# ═══════════════════════════════════════════════════════════════════════════════
# 4. APOSTASY ACCUSATION (RIDDA)
# ═══════════════════════════════════════════════════════════════════════════════

qadi_encounters.append(qadi_enc("page_qadi_ridda", "The Accusation of Apostasy",
    "A philosopher named Ibrahim has been denounced by his neighbors. He teaches Greek logic in a private salon—Aristotle's Organon, translated at the House of Wisdom. His accuser, a cloth merchant named Tariq, claims Ibrahim denied the resurrection of the body in a public conversation: \"He said the afterlife is spiritual, not physical. That the descriptions of paradise in the Quran are metaphors. This is kufr—disbelief.\"\n\nIbrahim responds: \"I said that Ibn Sina's argument for the immateriality of the soul is compatible with Islamic eschatology. I did not deny the resurrection—I discussed its modality. Tariq does not understand philosophy and heard heresy where there was only nuance.\"\n\nThe penalty for apostasy (ridda) in traditional fiqh is death, after a three-day period for repentance. The Mu'tazili position on free will (qadar) complicates this: if humans have genuine free will and are responsible for their choices, does the state have the right to coerce belief? The Mu'tazila also tend to interpret Quranic eschatology more figuratively.\n\nThe crowd outside your court is large. Word has spread. Tariq's faction wants blood. Ibrahim's students want vindication.",
    [
        qopt("page_qadi_ridda", 0,
            "Dismiss the case: interpreting eschatology is not apostasy. The Quran commands 'no compulsion in religion' (2:256), and philosophical interpretation is within the bounds of ijtihad.",
            "You deliver a ruling that makes the Mu'tazili scholars proud and the traditionalists apoplectic:\n\n\"Ridda requires a clear, unambiguous renunciation of Islam's core tenets: the oneness of God, the prophethood of Muhammad, and the obligation of the five pillars. Discussing the modality of resurrection is not renunciation—it is tafsir, interpretation. The Prophet's companions themselves disagreed on eschatological details. Furthermore, the Quranic principle of la ikraha fi'l-din—no compulsion in religion—establishes that belief cannot be coerced. If it cannot be coerced, it cannot be punished.\"\n\nIbrahim walks free. Tariq organizes a petition against you. The philosophical salons of Baghdad breathe easier. But you have established a precedent that the strict fuqaha will spend decades trying to overturn: that the qadi's bench is not an inquisition.",
            [fx("char_player", "Aql_Naql", 0.060), fx("char_player", "pAql_Naql", 0.030),
             fx("char_player", "Public_Standing", -0.024),
             fx("char_amma", "Aql_Naql", 0.045),
             fx("char_player", "Compliance_Resistance", -0.024),
             fx("char_player", "Theological_Conviction", 0.045), fx("char_player", "pTheological_Conviction", 0.022)]),
        qopt("page_qadi_ridda", 1,
            "Open a formal ridda investigation: summon witnesses, examine Ibrahim's writings, and apply the traditional three-day repentance protocol.",
            "You follow the established procedure. Ibrahim is detained. Scholars are summoned to examine his teachings. His students are interrogated. The three-day clock starts.\n\nOn day two, Ibrahim recants everything. \"I affirm the bodily resurrection, the physical paradise, and every detail of the traditional creed.\" His voice is flat. His eyes are dead. He has calculated the odds and chosen survival over sincerity.\n\nYou release him. The traditional procedure was followed. Tariq is satisfied. Ibrahim's salon closes permanently. His students scatter. One of them—a gifted mathematician—leaves Baghdad for Cairo and never returns.\n\nThe irony is perfect: you are enforcing theological conformity while the Caliph is enforcing a different theological conformity on you. The Mihna eats its own.",
            [fx("char_player", "Aql_Naql", -0.045), fx("char_player", "pAql_Naql", -0.022),
             fx("char_player", "Public_Standing", 0.024),
             fx("char_amma", "Compliance_Resistance", 0.024),
             fx("char_player", "Compliance_Resistance", 0.024),
             fx("char_player", "Theological_Conviction", -0.024)]),
        qopt("page_qadi_ridda", 2,
            "Turn the accusation into a public debate: let Ibrahim defend his position before qualified scholars. If his interpretation is within bounds, he is acquitted. If not, he recants voluntarily.",
            "You convene a munazara—a formal disputation—in the court. Ibrahim defends his position. Three scholars examine him: one Mu'tazili, one Hanbali, one from the emerging Ash'ari circle.\n\nThe debate lasts four hours. Ibrahim is sharp but not heretical—he affirms the resurrection while discussing its philosophical implications. The Mu'tazili scholar finds no fault. The Hanbali scholar condemns his language but admits the substance is within bounds. The Ash'ari observer says: \"His conclusions are sound; his method needs discipline.\"\n\nYou rule: not guilty of ridda, but Ibrahim must submit his future public lectures to scholarly review. A compromise. Tariq storms out. Ibrahim is chastened but alive and free.\n\nThe munazara becomes a model. Other qadis begin using it for sensitive cases. You have accidentally invented a procedural safeguard that neither pure reason nor pure tradition would have produced alone.",
            [fx("char_player", "Aql_Naql", 0.024), fx("char_player", "pAql_Naql", 0.012),
             fx("char_player", "Public_Standing", 0.045), fx("char_player", "pPublic_Standing", 0.022),
             fx("char_player", "Theological_Conviction", 0.045), fx("char_player", "pTheological_Conviction", 0.022),
             fx("char_ashari", "Public_Standing", 0.024)]),
    ],
    desirability=11.5, gx=400, gy=0))


# ═══════════════════════════════════════════════════════════════════════════════
# 5. THE WINE MERCHANT'S TESTIMONY
# ═══════════════════════════════════════════════════════════════════════════════

qadi_encounters.append(qadi_enc("page_qadi_wine", "The Wine Merchant's Testimony",
    "A property dispute. A Muslim merchant claims a Christian wine-seller encroached on his warehouse boundary. The Christian, a Nestorian named Yuhanna, produces a deed—witnessed by two Christian men and one Muslim woman.\n\nThe traditional position: the testimony of non-Muslims against Muslims is inadmissible in most schools. A woman's testimony counts as half a man's in financial matters (per 2:282). Yuhanna's deed has no valid witnesses by traditional standards.\n\nThe Mu'tazili position: God's justice is universal and rational. If the deed is genuine, excluding testimony based on the witness's religion or sex undermines the purpose of evidence—which is to establish truth. The function of testimony is epistemic, not ritual.\n\nThe Hanafi school (closest to accepting non-Muslim testimony) allows it in some commercial cases. The Hanbali school rejects it entirely.\n\nYuhanna has been a respected merchant in Baghdad for thirty years. The Muslim claimant arrived last year from Kufa.",
    [
        qopt("page_qadi_wine", 0,
            "Accept Yuhanna's deed: testimony is about establishing truth, and these witnesses are credible regardless of faith or sex.",
            "You rule that the purpose of shahada (testimony) is to establish facts, and that credibility is a function of character, not creed. Yuhanna's witnesses are known, honest, and consistent. The deed is valid.\n\nThe Muslim merchant appeals, citing the traditional evidentiary hierarchy. Ibn Hanbal's followers add this to their list of your rationalist innovations. But the Christian and Jewish merchants of Baghdad—who form a significant portion of the tax base—note that a qadi finally treated their oaths as worth something. The Caliph's treasury benefits from the confidence of dhimmi traders. Justice and revenue align, for once.",
            [fx("char_player", "Aql_Naql", 0.060), fx("char_player", "pAql_Naql", 0.030),
             fx("char_player", "Public_Standing", 0.024), fx("char_player", "pPublic_Standing", 0.012),
             fx("char_amma", "Aql_Naql", 0.024),
             fx("char_player", "Theological_Conviction", 0.024)]),
        qopt("page_qadi_wine", 1,
            "Reject the deed: the witnesses do not meet the Sharia standard. Require Yuhanna to produce Muslim male witnesses or forfeit.",
            "You apply the traditional evidentiary rules. Yuhanna cannot produce Muslim male witnesses to a transaction conducted entirely within the Christian quarter. The deed is rejected. The Muslim merchant takes the warehouse.\n\nYuhanna is dignified in defeat. \"I have lived in Baghdad under the Pact of Umar for thirty years. I pay the jizya. I step off the road when a Muslim passes. But I cannot protect my property in your courts because my friends pray differently.\" He moves his business to Mosul.\n\nThe Christian quarter is quieter after that. Quieter and poorer. The jizya receipts decline. The connection between justice and prosperity is not theoretical.",
            [fx("char_player", "Aql_Naql", -0.045), fx("char_player", "pAql_Naql", -0.022),
             fx("char_player", "Public_Standing", -0.030),
             fx("char_amma", "Compliance_Resistance", -0.024),
             fx("char_player", "Theological_Conviction", 0.024)]),
        qopt("page_qadi_wine", 2,
            "Apply the Hanafi exception: accept dhimmi testimony in commercial disputes between dhimmis and Muslims, but note it as an exceptional ruling requiring corroboration.",
            "You find the narrow path through the fiqh. The Hanafi school—the official school of the Abbasid judiciary—does allow non-Muslim testimony in certain commercial contexts, particularly where the transaction occurred in non-Muslim spaces. You accept the deed but require additional corroboration: a survey of the actual property boundary by a neutral party.\n\nThe survey confirms Yuhanna's claim. The warehouse is his. The Muslim merchant grumbles but accepts a ruling grounded in established Hanafi precedent—no rationalist innovation, just careful jurisprudence.\n\nYuhanna thanks you. \"I don't care which school you follow, qadi. I care that you looked at the evidence.\" The simplest standard of justice, spoken by a man who has learned not to expect it.",
            [fx("char_player", "Aql_Naql", 0.012), fx("char_player", "pAql_Naql", 0.006),
             fx("char_player", "Public_Standing", 0.045), fx("char_player", "pPublic_Standing", 0.022),
             fx("char_player", "Theological_Conviction", 0.024), fx("char_player", "pTheological_Conviction", 0.012)]),
    ],
    desirability=11.0, gx=400, gy=100))


# ═══════════════════════════════════════════════════════════════════════════════
# 6. THE PREDESTINATION DEFENSE
# ═══════════════════════════════════════════════════════════════════════════════

qadi_encounters.append(qadi_enc("page_qadi_qadar", "The Thief Who Blamed God",
    "A thief named Wahb is caught red-handed stealing grain from the public storehouse. The evidence is incontrovertible. But Wahb's defense is theological:\n\n\"Everything occurs by God's decree—qada' wa qadar. If God willed that I steal, how can the qadi punish me for fulfilling God's will? You would punish me for what God predetermined. This is injustice.\"\n\nThe courtroom laughs. But the argument, stripped of its self-serving application, touches the deepest fault line in Islamic theology.\n\nThe Mu'tazili position: humans have genuine free will (ikhtiyar). God creates the capacity for action; humans create their own acts. Wahb chose to steal; he is fully responsible.\n\nThe Ash'ari position (still forming): God creates all acts, including human acts, but humans 'acquire' (kasb) their acts—they are responsible through acquisition, not origination.\n\nThe strict predestinarian position: God decrees all things. Punishment is part of the decree. The qadi punishes because God decreed the punishment too. The circle closes.\n\nWahb waits, grinning. He doesn't expect acquittal. He expects you to reveal your theology.",
    [
        qopt("page_qadi_qadar", 0,
            "\"Wahb, you are a free agent who chose to steal. God gave you the capacity for good and evil; you chose evil. The Mu'tazili position is clear: you created your own act.\"",
            "Wahb shrugs. \"Then cut my hand, qadi. But know that you have said God does not control His creation.\" He has landed a blow—not legally, but theologically. The Mu'tazili position on free will does limit God's sovereignty in a way that many Muslims find uncomfortable.\n\nYou order the hadd punishment: amputation of the right hand. It is carried out. Wahb, now one-handed, leaves the court. In the Hanbali circles, your theological declaration matters more than the sentence. \"The qadi said humans create their own acts. This is the Mu'tazili heresy of the Qadariyya.\" Your ruling was correct. Your theology is now on the record.",
            [fx("char_player", "Aql_Naql", 0.045), fx("char_player", "pAql_Naql", 0.022),
             fx("char_player", "Theological_Conviction", 0.045), fx("char_player", "pTheological_Conviction", 0.022),
             fx("char_player", "Public_Standing", -0.024),
             fx("char_amma", "Aql_Naql", 0.024)]),
        qopt("page_qadi_qadar", 1,
            "\"Wahb, God decreed your theft and He decreed your punishment. I am the instrument of both. Hold out your hand.\"",
            "The courtroom falls silent. The predestinarian position, stated baldly, is terrifying in its consistency. Wahb's grin fades. He did not expect you to out-theologize him.\n\nThe hand is cut. Wahb is carried out. Ibn Hanbal's followers are impressed—not by the theology exactly, but by the refusal to engage in Mu'tazili speculation about human agency. You stayed within the transmitted framework: God decrees, we submit.\n\nBut Al-Ash'ari, hearing of the case, shakes his head. \"Both positions miss something. The thief is responsible—but not because he created his act. He is responsible because he acquired it. Kasb. The answer is neither freedom nor compulsion. It is something in between.\" The synthesis grows.",
            [fx("char_player", "Aql_Naql", -0.045), fx("char_player", "pAql_Naql", -0.022),
             fx("char_player", "Theological_Conviction", 0.045), fx("char_player", "pTheological_Conviction", 0.022),
             fx("char_player", "Public_Standing", 0.024),
             fx("char_ashari", "Theological_Conviction", 0.024)]),
        qopt("page_qadi_qadar", 2,
            "\"Wahb, your theology is above your station but not wrong to ask. However, the court does not adjudicate divine will—it adjudicates human action. You stole. The hadd applies. Theology is for the scholars; the bench deals in evidence.\"",
            "You refuse the theological bait entirely. The court is not a seminary. The evidence is clear. The hadd is applied.\n\nWahb leaves unsatisfied—he wanted a debate. The crowd is satisfied—they wanted a sentence. The scholars are intrigued—you have implicitly argued that jurisprudence and theology operate in separate domains. This is not quite Mu'tazili, not quite Hanbali. It is a pragmatic separation of concerns that no school has formally articulated but every working qadi practices.\n\nAl-Ash'ari notes: \"The qadi just discovered that you can apply the law without resolving the metaphysics. That may be the most important legal principle in Islam, and no one has written it down.\"",
            [fx("char_player", "Aql_Naql", 0.012), fx("char_player", "pAql_Naql", 0.006),
             fx("char_player", "Public_Standing", 0.045), fx("char_player", "pPublic_Standing", 0.022),
             fx("char_player", "Theological_Conviction", 0.024), fx("char_player", "pTheological_Conviction", 0.012),
             fx("char_ashari", "Aql_Naql", 0.024)]),
    ],
    desirability=10.5, gx=400, gy=200))


# ═══════════════════════════════════════════════════════════════════════════════
# 7. THE INHERITANCE OF THE HERMAPHRODITE (KHUNTHA)
# ═══════════════════════════════════════════════════════════════════════════════

qadi_encounters.append(qadi_enc("page_qadi_khuntha", "The Inheritance of the Khuntha",
    "A wealthy landowner has died. Among his heirs is a person named Nuri—a khuntha mushkil, an individual of ambiguous sex whose physical markers do not clearly indicate male or female. Islamic inheritance law (faraid) assigns fixed shares based on sex: a male heir receives double a female heir's share.\n\nNuri's siblings want the minimum allocation—they classify Nuri as female. Nuri claims the male share, citing masculine social presentation and decades of living as a man.\n\nThe classical fiqh is genuinely uncertain here. The Hanafi school assigns the lesser (female) share as a precaution. The Shafi'i school attempts biological determination. The Hanbali school assigns the average of male and female shares.\n\nThe Mu'tazili approach, grounded in rational justice, asks: what classification best serves equity? The traditionalist approach asks: what classification best fits the transmitted categories?\n\nNuri stands before you—a person the law was not designed for, asking the law to see them anyway.",
    [
        qopt("page_qadi_khuntha", 0,
            "Rule based on Nuri's social reality and self-identification: decades of masculine life constitute the strongest evidence. Assign the male share.",
            "You argue from istihsan—juristic preference grounded in equity and reason. \"The faraid are based on social roles as much as biology. Nuri has lived as a man, traded as a man, prayed in the men's rows, and been recognized by the community as a man for forty years. The rational assessment of Nuri's social reality outweighs the ambiguity of physical examination.\"\n\nNuri receives the male share. The siblings appeal. The Hanbali scholars argue you've substituted reason for God's categories. The Mu'tazili scholars support you but are uncomfortable—they also believe in rational categories, just different ones. You've pushed the jurisprudence into territory where no school has firm footing.",
            [fx("char_player", "Aql_Naql", 0.045), fx("char_player", "pAql_Naql", 0.022),
             fx("char_player", "Public_Standing", 0.024),
             fx("char_amma", "Aql_Naql", 0.024),
             fx("char_player", "Theological_Conviction", 0.024)]),
        qopt("page_qadi_khuntha", 1,
            "Apply the Hanafi precautionary principle: assign the lesser (female) share. In doubt, protect the other heirs' certain rights.",
            "You cite the Hanafi maxim: al-yaqin la yazulu bi'l-shakk—certainty is not overridden by doubt. The other heirs' shares are certain; Nuri's classification is doubtful. In doubt, assign the lesser share.\n\nNuri accepts the ruling with dignity. \"I expected this,\" they say. \"The law sees what it wants to see.\" The siblings are satisfied. The jurists approve your caution. But you notice that the law's categories, applied mechanically, have reduced a human being to a problem of arithmetic. The faraid were designed to ensure justice. In this case, justice and the faraid point in different directions.",
            [fx("char_player", "Aql_Naql", -0.024), fx("char_player", "pAql_Naql", -0.012),
             fx("char_player", "Public_Standing", -0.024),
             fx("char_player", "Theological_Conviction", 0.024),
             fx("char_amma", "Compliance_Resistance", 0.024)]),
        qopt("page_qadi_khuntha", 2,
            "Apply the Hanbali compromise: assign the average of the male and female shares. Neither category fully applies; split the difference.",
            "The Hanbali method is mathematically elegant: calculate both the male and female shares, average them. Nuri receives more than the female share but less than the male share. The siblings receive proportionally adjusted amounts.\n\n\"This is not justice,\" Nuri says. \"This is arithmetic.\" Perhaps. But it is arithmetic that acknowledges the ambiguity rather than forcing a binary resolution. The Hanbali scholars approve—Ibn Hanbal himself ruled on a khuntha case using this method.\n\nAl-Ash'ari comments: \"The qadi found a position that satisfies the text, accommodates the reality, and offends everyone equally. That may be the definition of jurisprudence.\"",
            [fx("char_player", "Aql_Naql", 0.012), fx("char_player", "pAql_Naql", 0.006),
             fx("char_player", "Public_Standing", 0.024), fx("char_player", "pPublic_Standing", 0.012),
             fx("char_player", "Theological_Conviction", 0.024), fx("char_player", "pTheological_Conviction", 0.012)]),
    ],
    desirability=10.0, gx=400, gy=300))


# ═══════════════════════════════════════════════════════════════════════════════
# 8. THE COERCED DIVORCE
# ═══════════════════════════════════════════════════════════════════════════════

qadi_encounters.append(qadi_enc("page_qadi_talaq", "The Coerced Divorce",
    "A soldier named Abbas has returned from the Caliph's campaign against the Byzantines. In his absence, his commander—a powerful amir—pressured Abbas's wife Hind into obtaining a khul' divorce by threatening to confiscate Abbas's military pension. Hind divorced Abbas under duress. The amir then married Hind himself.\n\nAbbas stands before you, broken. \"I fought for the Caliph. While I bled at the frontier, his amir stole my wife.\"\n\nThe amir's advocate argues: \"The khul' was legal. Hind initiated it. The reasons are irrelevant—Islamic divorce law examines the act, not the motive.\"\n\nThe Mu'tazili principle: an act performed under coercion (ikrah) has no legal validity, because moral responsibility requires genuine free choice. A coerced divorce is no divorce at all.\n\nThe Hanafi position: a coerced talaq by the husband is still valid (he spoke the words). But a coerced khul' by the wife? The schools diverge.\n\nThe amir is powerful. He is connected to the Caliph's inner circle. Ruling against him has consequences.",
    [
        qopt("page_qadi_talaq", 0,
            "Nullify the divorce: coercion vitiates consent, and without consent, the khul' is void. Return Hind to Abbas's marriage.",
            "You deliver the ruling knowing what it costs. \"The Quran specifies that khul' requires the wife's genuine desire to separate—taraadiyaa (mutual agreement, 2:229). Coercion by a third party destroys the foundation of the khul'. The divorce is void. The amir's subsequent marriage to Hind is therefore invalid—a nikah without a valid dissolution is zina.\"\n\nThe word zina hits like a thunderbolt. The amir's advocate sputters. The courtroom erupts. You have just accused one of the Caliph's commanders of fornication, using impeccable legal logic.\n\nThe amir does not appear for sentencing. He transfers to a post in Khurasan. Hind returns to Abbas. Your name is now on a powerful man's list. But the ruling stands—because the logic stands, and even the Caliph's judges cannot overrule sound fiqh without admitting that the law serves power, not justice.",
            [fx("char_player", "Aql_Naql", 0.045), fx("char_player", "pAql_Naql", 0.022),
             fx("char_player", "Compliance_Resistance", -0.060), fx("char_player", "pCompliance_Resistance", -0.030),
             fx("char_player", "Public_Standing", 0.045), fx("char_player", "pPublic_Standing", 0.022),
             fx("char_amma", "Compliance_Resistance", -0.045)]),
        qopt("page_qadi_talaq", 1,
            "Uphold the divorce: the khul' was formally valid. Hind spoke the words. The court cannot investigate motives behind every divorce.",
            "You rule that the khul' met its formal requirements: Hind initiated, Hind renounced her mahr, the dissolution was witnessed. The court does not and cannot investigate the private pressures that lead to every divorce—if it did, half the divorces in Baghdad would be invalidated.\n\nAbbas weeps. The soldier who bled for the Caliph has been processed by the Caliph's legal machinery and found expendable. The amir keeps Hind. The ruling is legally defensible and morally bankrupt. The law, applied without reference to justice, becomes the instrument of the powerful—which is precisely what the Mu'tazila warn about when they insist that reason must inform jurisprudence.",
            [fx("char_player", "Aql_Naql", -0.024), fx("char_player", "pAql_Naql", -0.012),
             fx("char_player", "Compliance_Resistance", 0.060), fx("char_player", "pCompliance_Resistance", 0.030),
             fx("char_player", "Public_Standing", -0.060), fx("char_player", "pPublic_Standing", -0.030),
             fx("char_amma", "Compliance_Resistance", 0.045)]),
        qopt("page_qadi_talaq", 2,
            "Refer the case to the chief qadi and the Caliph's court. This is too politically explosive for a single qadi—and the system should bear the weight of its own decisions.",
            "You write a detailed brief documenting the coercion, the evidence, and the legal arguments on both sides. You refer it upward with a recommendation to nullify—but you let the chief qadi make the final call.\n\nThe chief qadi, a political creature, delays. And delays. Abbas waits. Hind waits. Eventually, the amir is transferred for unrelated reasons and the case becomes moot—Hind, now in Khurasan, is beyond your jurisdiction.\n\nYou saved yourself. You may have doomed Hind. The referral was procedurally correct and humanly inadequate. Al-Ash'ari, hearing of it, says: \"The qadi who refers justice to a committee has already decided against it.\"",
            [fx("char_player", "Compliance_Resistance", 0.024), fx("char_player", "pCompliance_Resistance", 0.012),
             fx("char_player", "Public_Standing", -0.024),
             fx("char_player", "Theological_Conviction", -0.024),
             fx("char_amma", "Public_Standing", -0.024)]),
    ],
    desirability=9.5, gx=400, gy=400))


# ═══ Wire encounters into spool and save ═════════════════════════════════════

qadi_ids = [e["id"] for e in qadi_encounters]
for sp in sw["spools"]:
    if sp["id"] == "spool_qadi":
        sp["encounters"] = qadi_ids

sw["encounters"].extend(qadi_encounters)

with open(path, "w", encoding="utf-8") as f:
    json.dump(sw, f, indent=2, ensure_ascii=False)

print(f"Added {len(qadi_encounters)} qadi encounters. Total encounters: {len(sw['encounters'])}")
print("Qadi cases:")
for e in qadi_encounters:
    nopts = len(e["options"])
    print(f"  {e['id']:30s} {e['title']:45s} opts={nopts}")
