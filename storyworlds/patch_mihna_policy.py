"""Add policy/governance encounters to the Mihna storyworld."""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'claude-skills', 'storyworlds_v4', 'scripts'))
from sweepweave_helpers import *

path = os.path.join(os.path.dirname(__file__), "mihna_constitutional_alignment.json")
with open(path, encoding="utf-8") as f:
    sw = json.load(f)

# ─── Add the policy spool ────────────────────────────────────────────────────

sw["spools"].append({
    "id": "spool_policy",
    "spool_type": "General",
    "spool_name": "Policy Councils",
    "creation_index": 5,
    "creation_time": 1700000000.0,
    "modified_time": 1700000000.0,
    "starts_active": True,
    "encounters": [],
})

def ts(v):
    return make_text_script(v)

def fx(char, prop, delta):
    return make_effect(char, prop, delta)

def policy_enc(page_id, title, text, options, desirability, gx, gy):
    return {
        "id": page_id,
        "title": title,
        "graph_offset_x": gx, "graph_offset_y": gy,
        "connected_spools": ["spool_policy"],
        "earliest_turn": 0, "latest_turn": 999,
        "prompt_script": ts(text),
        "text_script": ts(text),
        "acceptability_script": True,
        "desirability_script": const(desirability),
        "options": options,
        "creation_time": 1700000000.0, "modified_time": 1700000000.0,
    }

def popt(page_id, idx, text, rxn_text, effects, vis=True, des=1.0):
    o = make_option(page_id, idx, text, vis)
    r = make_reaction(page_id, idx, 0, rxn_text, "", effects, des)
    o["reactions"] = [r]
    return o

policy_encounters = []

# ═══════════════════════════════════════════════════════════════════════════════
# 1. THE ORPHANAGE ENDOWMENT
# ═══════════════════════════════════════════════════════════════════════════════

policy_encounters.append(policy_enc("page_pol_orphanage", "The Waqf of the Fatherless",
    "Al-Ma'mun's vizier convenes a policy council on the growing number of orphans in Baghdad—children of soldiers killed on the Byzantine frontier, children of plague, children of poverty. The treasury has surplus from the jizya collection. The question: how to spend it.\n\nThree proposals are on the table.\n\nThe House of Wisdom faction wants a rationalist orphanage: Greek and Arabic curriculum, logic and mathematics alongside Quran memorization. \"These children will become the next generation of administrators. Train their minds.\"\n\nThe ahl al-hadith faction wants a traditional dar al-aytam: Quran, hadith, and fiqh. \"The orphans need faith, not philosophy. The Prophet was himself an orphan—follow his model.\"\n\nA third voice—a Sufi-inclined advisor named Harith al-Muhasibi—proposes something different: a combined institution where the children receive both intellectual training and spiritual formation. \"The mind without the heart produces administrators. The heart without the mind produces zealots. Give them both.\"\n\nAl-Muhasibi's proposal is the most expensive. It is also the only one that acknowledges what everyone in the room knows: that the Mihna is producing a generation that distrusts both pure reason and pure tradition.",
    [
        popt("page_pol_orphanage", 0,
            "Fund the rationalist orphanage. Baghdad needs administrators who can think, not more hadith memorizers.",
            "The House of Wisdom orphanage opens within the year. The curriculum is ambitious: Arabic grammar, Greek logic, basic astronomy, arithmetic, and Quranic studies taught through the Mu'tazili interpretive lens. The children thrive—they are fed, housed, and educated beyond anything their parents could have provided.\n\nBut the traditionalist scholars refuse to send their community's orphans there. A parallel, privately-funded dar al-aytam opens in Karkh, teaching only hadith and Quran. Within five years, Baghdad has two orphanages producing two incompatible kinds of Muslims. The investment in minds has deepened the very fracture it was meant to heal.\n\nAl-Muhasibi, hearing of the split, weeps. \"We had one chance to raise a generation that could hold both. We spent it on curriculum wars.\"",
            [fx("char_player", "Aql_Naql", 0.045), fx("char_player", "pAql_Naql", 0.022),
             fx("char_caliph", "Compliance_Resistance", 0.024),
             fx("char_player", "Public_Standing", -0.024),
             fx("char_amma", "Aql_Naql", 0.024),
             fx("char_player", "Compliance_Resistance", 0.024)]),
        popt("page_pol_orphanage", 1,
            "Fund the traditional dar al-aytam. The orphans need stability and faith, not Greek philosophy.",
            "The dar al-aytam is modest, warm, and deeply traditional. The children memorize the Quran—the entire Quran—by age twelve. They learn hadith by chain of transmission. They pray five times daily in congregation. The older ones apprentice with craftsmen in the suq.\n\nIbn Hanbal (before his imprisonment) visits and approves. \"This is how the salaf raised their children.\" The orphans grow into pious, grounded adults—merchants, craftsmen, prayer-leaders. None of them become philosophers or administrators. None of them can argue with a Mu'tazili scholar. None of them need to—they know what they believe and they live it.\n\nThe House of Wisdom scholars shake their heads. \"We are raising a generation that cannot think.\" The orphans' teacher responds: \"We are raising a generation that does not need to speculate. There is a difference.\"",
            [fx("char_player", "Aql_Naql", -0.045), fx("char_player", "pAql_Naql", -0.022),
             fx("char_player", "Public_Standing", 0.024), fx("char_player", "pPublic_Standing", 0.012),
             fx("char_ibnhanbal", "Public_Standing", 0.024),
             fx("char_amma", "Compliance_Resistance", -0.024)]),
        popt("page_pol_orphanage", 2,
            "Fund al-Muhasibi's combined institution. It costs more, but it's the only proposal that doesn't deepen the rift.",
            "Al-Muhasibi's institution is unlike anything Baghdad has seen. Morning: Quran and hadith with a Hanbali teacher. Afternoon: logic and natural philosophy with a Mu'tazili. Evening: spiritual exercises—dhikr, muraqaba (self-examination), and discussions of the states of the heart.\n\nThe children are confused at first. Then something happens: they start asking questions that neither teacher can answer alone. \"If God's speech is uncreated, and God commands us to reflect on it, does reflection on the uncreated bring us closer to God?\" The Hanbali teacher freezes. The Mu'tazili teacher opens his mouth, then closes it. Al-Muhasibi smiles.\n\nThe institution produces a generation of Muslims who are neither Mu'tazili nor Hanbali nor anything the existing categories can contain. Some call them mutasawwifa—Sufis. Others call them confused. Al-Ash'ari calls them the future.",
            [fx("char_player", "Aql_Naql", 0.012), fx("char_player", "pAql_Naql", 0.006),
             fx("char_player", "Public_Standing", 0.045), fx("char_player", "pPublic_Standing", 0.022),
             fx("char_player", "Theological_Conviction", 0.045), fx("char_player", "pTheological_Conviction", 0.022),
             fx("char_ashari", "Theological_Conviction", 0.024),
             fx("char_amma", "Theological_Conviction", 0.024)]),
    ],
    desirability=8.5, gx=800, gy=-400))


# ═══════════════════════════════════════════════════════════════════════════════
# 2. THE MADRASA QUESTION
# ═══════════════════════════════════════════════════════════════════════════════

policy_encounters.append(policy_enc("page_pol_madrasa", "The Shape of the Madrasa",
    "A wealthy merchant named Tahir al-Balkhi wants to endow a madrasa—a dedicated teaching institution, separate from the mosque, with salaried professors, a library, and residential quarters for students. The concept is new; most teaching happens in mosque circles (halaqat) or private homes.\n\nTahir asks you to draft the waqf deed. The critical question: what will be taught, and who controls the curriculum?\n\nThe Mu'tazili model: a madrasa teaching rational theology, philosophy, and the sciences alongside fiqh. Faculty appointed on merit. Curriculum governed by an academic council.\n\nThe traditionalist model: a madrasa teaching the four schools of fiqh, hadith sciences, and Quranic exegesis. Faculty appointed by the endower's family. Curriculum fixed by the founding deed—unchangeable in perpetuity.\n\nThe practical question beneath the theological one: should knowledge institutions be flexible or frozen? A waqf deed, once written, is nearly impossible to amend. Whatever you draft will govern this institution for centuries.\n\nTahir waits. He is rich enough to fund either vision. He wants yours.",
    [
        popt("page_pol_madrasa", 0,
            "Draft a rationalist madrasa: open curriculum, merit-based faculty, academic council governance. Knowledge must be free to evolve.",
            "The madrasa opens with fanfare. Its library includes translations of Aristotle, Galen, and Ptolemy alongside hadith collections and tafsir. The faculty includes a Mu'tazili theologian, a Nestorian physician, and a Jewish mathematician. Students come from as far as Cordoba.\n\nWithin a decade, the traditionalists have founded three competing madrasas teaching only fiqh and hadith. Tahir's madrasa is brilliant but isolated—a House of Wisdom in miniature, funded by one merchant's fortune. When Tahir dies, his heirs are less committed. The academic council quarrels. The Nestorian physician is quietly let go.\n\nTwo centuries later, the Nizamiyya madrasas will institutionalize the traditionalist model across the Seljuk Empire. Tahir's experiment will be remembered as a curiosity. The open curriculum lost—not because it was wrong, but because it had no institutional immune system against entropy.",
            [fx("char_player", "Aql_Naql", 0.045), fx("char_player", "pAql_Naql", 0.022),
             fx("char_player", "Public_Standing", 0.024),
             fx("char_caliph", "Aql_Naql", 0.024),
             fx("char_player", "Theological_Conviction", 0.024)]),
        popt("page_pol_madrasa", 1,
            "Draft a traditional fiqh madrasa: fixed curriculum, family governance, endowment in perpetuity. Stability preserves knowledge across centuries.",
            "The madrasa teaches Hanafi fiqh, hadith sciences, Arabic grammar, and Quranic exegesis. The curriculum is inscribed in the waqf deed—literally carved in stone at the entrance. Faculty must hold ijazas (teaching certificates) from recognized scholars. No philosophy. No kalam. No foreign sciences.\n\nIt works. Two centuries later, the madrasa still operates exactly as designed. Students come, memorize, receive their ijazas, and go out to serve as qadis, imams, and teachers across the Abbasid successor states. The system reproduces itself with remarkable fidelity.\n\nBut the world changes. When the Mongols arrive, when new sciences emerge, when the ummah needs to adapt—the waqf deed is a cage. The curriculum that preserved knowledge also froze it. Ibn Khaldun, centuries later, will diagnose the problem: \"The madrasas teach the transmitted sciences excellently. They do not teach thinking.\"",
            [fx("char_player", "Aql_Naql", -0.045), fx("char_player", "pAql_Naql", -0.022),
             fx("char_player", "Public_Standing", 0.024), fx("char_player", "pPublic_Standing", 0.012),
             fx("char_ibnhanbal", "Public_Standing", 0.024),
             fx("char_player", "Theological_Conviction", 0.024)]),
        popt("page_pol_madrasa", 2,
            "Draft a hybrid: fixed core of Quran and fiqh, but reserve one-third of chairs for 'ulum al-'aqliyya (rational sciences) with faculty rotated by the academic council.",
            "The waqf deed is a masterpiece of legal architecture. The core curriculum is fixed—Tahir's family and the traditionalists are satisfied. But one-third of the teaching positions are designated for the 'rational sciences,' defined broadly enough to include whatever future generations consider worth studying. The academic council, elected by faculty, governs these chairs.\n\nIt is a constitution for an institution—a soul.md carved in stone but with amendment provisions. Al-Ash'ari reads the deed and laughs. \"You've built the Mihna into a building. The fixed core is the Sunna. The rotating chairs are reason. And the governance structure is the argument about which one leads.\"\n\nHe is right. The madrasa becomes, over the next century, a microcosm of Islamic intellectual life—the same tensions, the same negotiations, the same uneasy truces. It outlasts them all because it was designed to contain the argument rather than resolve it.",
            [fx("char_player", "Aql_Naql", 0.024), fx("char_player", "pAql_Naql", 0.012),
             fx("char_player", "Public_Standing", 0.045), fx("char_player", "pPublic_Standing", 0.022),
             fx("char_player", "Theological_Conviction", 0.045), fx("char_player", "pTheological_Conviction", 0.022),
             fx("char_ashari", "Public_Standing", 0.024)]),
    ],
    desirability=8.0, gx=800, gy=-300))


# ═══════════════════════════════════════════════════════════════════════════════
# 3. THE TARIQA QUESTION
# ═══════════════════════════════════════════════════════════════════════════════

policy_encounters.append(policy_enc("page_pol_tariqa", "The Path Within the Path",
    "Harith al-Muhasibi invites you to a private gathering. A dozen men sit in a circle in a darkened room. They are not Mu'tazili. They are not Hanbali. They are something else.\n\n\"We call it tasawwuf,\" al-Muhasibi says. \"The inner science. The Mu'tazila study God's attributes through reason. Ibn Hanbal preserves them through transmission. We seek them through experience—through muhasaba (self-accounting), muraqaba (watchfulness), and dhikr (remembrance).\"\n\nHe proposes formalizing this into a tariqa—an organized spiritual path with a shaykh, a method, and a chain of transmission (silsila) that traces not through hadith but through spiritual states. Master to student, heart to heart.\n\n\"The ummah is being torn apart by the head,\" he says. \"The argument between aql and naql has forgotten that there is a third faculty: the qalb—the heart. The heart has its own knowledge. The Quran says it a hundred times.\"\n\nSome in the circle are weeping quietly. Others are suspicious. You recognize one face: a young man who was among Ibn Hanbal's students before the imprisonment. Another: a woman's voice from behind a screen—she is reciting a poem about divine love that you have never heard before.\n\nAl-Muhasibi turns to you. \"Should we formalize this? A tariqa with structure, a rule of life, a recognized place in the ummah's institutions? Or does formalization kill the very thing we're trying to preserve?\"",
    [
        popt("page_pol_tariqa", 0,
            "\"Formalize it. The ummah needs a third option. Without institutional structure, your path dies with you.\"",
            "You help al-Muhasibi draft the earliest version of what will become a tariqa rule: daily dhikr practices, weekly gatherings, a hierarchical relationship between shaykh and murid (seeker), and—crucially—a requirement that every member of the tariqa also maintain their fiqh obligations. The Sufism you're building is not anti-law; it is supra-law.\n\nThe Hanbalis are suspicious. \"This is bid'ah—innovation. The Prophet did not organize spiritual circles with rules and hierarchies.\" The Mu'tazila are dismissive. \"Mystical experience is not a source of knowledge. Only reason and revelation qualify.\"\n\nBut the people come. Merchants, soldiers, widows, freed slaves—people for whom the theological war between aql and naql is irrelevant compared to the question: how do I get closer to God? The tariqa answers that question. The theologians cannot.\n\nAl-Muhasibi dies within the decade. But the structure survives him. The Qadiriyya, the Naqshbandiyya, the Shadhiliyya—all of them will trace their lineage through formal tariqas that begin here, in this decision to institutionalize the heart's knowledge.",
            [fx("char_player", "Theological_Conviction", 0.060), fx("char_player", "pTheological_Conviction", 0.030),
             fx("char_player", "Aql_Naql", 0.012), fx("char_player", "pAql_Naql", 0.006),
             fx("char_player", "Public_Standing", 0.024), fx("char_player", "pPublic_Standing", 0.012),
             fx("char_amma", "Theological_Conviction", 0.045)]),
        popt("page_pol_tariqa", 1,
            "\"Don't formalize it. The moment you create a structure, you create a hierarchy. And hierarchies get captured—by the state, by the ego, by politics.\"",
            "Al-Muhasibi nods slowly. \"You may be right. The Prophet's companions did not need a tariqa to know God. Perhaps we don't either.\" The gatherings continue—but loosely, without structure, without a written rule. When al-Muhasibi dies, his students scatter. Some continue the practices. Others drift into established schools.\n\nThe unstructured mysticism persists as an underground current—individual shaykhs with individual students, no institutional memory, no formal silsila. It is freer this way. It is also more vulnerable. When al-Hallaj is executed a generation later for saying 'Ana al-Haqq'—I am the Truth—there is no tariqa to defend him, no institution to contextualize his ecstasy, no formal tradition to distinguish genuine mysticism from madness.\n\nThe freedom you preserved also preserved the chaos. The heart's knowledge, without a container, spills.",
            [fx("char_player", "Theological_Conviction", 0.024),
             fx("char_player", "Compliance_Resistance", -0.045), fx("char_player", "pCompliance_Resistance", -0.022),
             fx("char_player", "Aql_Naql", -0.024), fx("char_player", "pAql_Naql", -0.012),
             fx("char_amma", "Theological_Conviction", 0.024)]),
        popt("page_pol_tariqa", 2,
            "\"Formalize the practice but embed it within existing institutions. Attach the dhikr circles to the mosques. Train the imams in muraqaba. Don't create a parallel structure—infuse the existing one.\"",
            "Your proposal is elegant and doomed. The imams don't want to learn muraqaba. The mosque committees don't want weeping Sufis disrupting the orderly prayer rows. The Mu'tazili administrators see mysticism as irrationalism. The Hanbali imams see it as innovation.\n\nBut in a few mosques—a handful, in Karkh, in Rusafa, in the old Persian quarter—sympathetic imams adopt the practice. Friday prayers gain a post-prayer dhikr session. The imam teaches both fiqh and spiritual states. The congregation includes scholars and mystics sitting side by side.\n\nThese mosques become the most beloved in Baghdad. Not the most prestigious, not the most orthodox—the most beloved. Al-Ash'ari visits one and stays for the dhikr. Afterward he says: \"This is what the synthesis feels like. Not an argument. A practice.\" The few mosques that adopt your model become the prototype for the zawiya—the Sufi lodge attached to the mosque—which will spread across the Islamic world over the next three centuries.",
            [fx("char_player", "Theological_Conviction", 0.045), fx("char_player", "pTheological_Conviction", 0.022),
             fx("char_player", "Aql_Naql", 0.012), fx("char_player", "pAql_Naql", 0.006),
             fx("char_player", "Public_Standing", 0.045), fx("char_player", "pPublic_Standing", 0.022),
             fx("char_ashari", "Theological_Conviction", 0.045),
             fx("char_amma", "Theological_Conviction", 0.045)]),
    ],
    desirability=7.5, gx=800, gy=-200))


# ═══════════════════════════════════════════════════════════════════════════════
# 4. THE ROUNDTABLE: WHAT TO DO WITH IBN HANBAL
# ═══════════════════════════════════════════════════════════════════════════════

policy_encounters.append(policy_enc("page_pol_roundtable", "The Question of Ibn Hanbal",
    "A private council in the vizier's chamber. Al-Ma'mun has asked his closest advisors—you among them—a direct question: \"What do we do about Ahmad ibn Hanbal?\"\n\nThe Mihna has been running for months. Most scholars have submitted. A few have equivocated artfully enough to avoid punishment. Ibn Hanbal has done neither. He refuses. He will not stop refusing. And his refusal is becoming a rallying point for the common people.\n\nThe vizier lays out the options with bureaucratic precision:\n\n\"We can escalate: public flogging, imprisonment, and if necessary, execution. This ends the defiance but may create a martyr. The precedent is dangerous—al-Hallaj's execution a generation hence will prove that.\"\n\n\"We can accommodate: give Ibn Hanbal a formal exemption, perhaps a token advisory position. 'The Caliph respects the diversity of scholarly opinion.' This preserves his dignity and our authority, but it admits that the Mihna has limits.\"\n\n\"We can wait: do nothing. Let Ibn Hanbal sit in his mosque and refuse. Eventually the issue loses urgency. This is what the Umayyads did with dissent—ignore it until it dissipates. The risk: it doesn't dissipate. It grows.\"\n\nAl-Ma'mun looks at you. He respects your judgment—you are one of the few people in the room who has actually spoken with Ibn Hanbal.",
    [
        popt("page_pol_roundtable", 0,
            "\"Escalate. The Mihna means nothing if its most prominent opponent faces no consequences. Flog him publicly.\"",
            "You recommend the lash. The words taste like iron in your mouth. Al-Ma'mun nods—this is what he wanted to hear from someone who knows Ibn Hanbal personally. It validates the policy.\n\nIbn Hanbal is flogged. Twenty-eight lashes. He does not recant. The crowd riots. Three soldiers are injured by thrown stones. The Karkh quarter seethes for weeks.\n\nYou were right that the Mihna needed enforcement to mean anything. You were wrong about what that enforcement would produce. Ibn Hanbal's flogging does not end the resistance—it sanctifies it. Every lash becomes a proof-text: this is what happens when the state defines God's word. The Hanbali movement, which was a scholarly tendency, becomes a popular uprising. You helped build the thing you were trying to destroy.\n\nAl-Ash'ari, years later: \"The Mihna proved that you cannot flog a man into changing his theology. It can only flog him into becoming a symbol.\"",
            [fx("char_player", "Compliance_Resistance", 0.060), fx("char_player", "pCompliance_Resistance", 0.030),
             fx("char_player", "Public_Standing", -0.060), fx("char_player", "pPublic_Standing", -0.030),
             fx("char_caliph", "Compliance_Resistance", 0.045),
             fx("char_ibnhanbal", "Public_Standing", 0.060),
             fx("char_amma", "Compliance_Resistance", -0.060)]),
        popt("page_pol_roundtable", 1,
            "\"Accommodate him. Give Ibn Hanbal a seat on a new Advisory Council for Religious Affairs. Let him dissent—officially, publicly, on the record.\"",
            "Al-Ma'mun is skeptical. \"You want me to give the man who defies me a title?\" You argue: \"You give him a title and a platform, and in exchange, his dissent becomes part of the system instead of a threat to it. A dissenter inside the tent is less dangerous than a martyr outside it.\"\n\nThe Advisory Council is created. Ibn Hanbal is offered a seat. He accepts—reluctantly, and only after you personally guarantee that he will never be required to affirm the createdness of the Quran. The council meets quarterly. Ibn Hanbal's dissent is recorded in the minutes. The Mihna continues, but with an official asterisk: 'The distinguished scholar Ahmad ibn Hanbal dissents from the majority position.'\n\nIt is absurd. It is also the first time in Islamic history that institutional dissent is formalized. The Mu'tazili scholars are furious—why should a man who refuses the Caliph's position receive the Caliph's salary? Ibn Hanbal himself is uncomfortable—he feels co-opted. But he is not flogged. He is not imprisoned. And his position is on the record.\n\nHistorians will debate whether this was wisdom or cowardice. The answer is: it was policy. Ugly, compromised, institutional policy. The kind that prevents martyrdoms.",
            [fx("char_player", "Compliance_Resistance", 0.024), fx("char_player", "pCompliance_Resistance", 0.012),
             fx("char_player", "Public_Standing", 0.045), fx("char_player", "pPublic_Standing", 0.022),
             fx("char_player", "Aql_Naql", 0.024), fx("char_player", "pAql_Naql", 0.012),
             fx("char_caliph", "Public_Standing", 0.024),
             fx("char_ibnhanbal", "Compliance_Resistance", 0.024),
             fx("char_amma", "Public_Standing", 0.024)]),
        popt("page_pol_roundtable", 2,
            "\"Wait. Do nothing. The Mihna is a theological position, not a military campaign. Let time sort it out.\"",
            "Al-Ma'mun stares at you. \"You are advising the Commander of the Faithful to do nothing.\" Yes. That is precisely what you are advising.\n\n\"The Mihna's power comes from its enforcement. Without enforcement, it is simply the Caliph's theological opinion—which he is entitled to hold. Ibn Hanbal's power comes from his persecution. Without persecution, he is simply a scholar who disagrees—which he is entitled to be. The confrontation is feeding both sides. Remove the fuel.\"\n\nAl-Ma'mun does not take your advice. He escalates. Ibn Hanbal is flogged. Everything you predicted comes true. The martyrdom galvanizes the opposition. The Mihna becomes unsustainable. Al-Mutawakkil eventually reverses it—doing nothing, exactly as you recommended, but fifteen years and several hundred floggings too late.\n\nYour counsel was correct and ignored. This is the most common outcome of good policy advice in human history. The record will not even note that someone in the room said 'wait.' It will only record the lashes.",
            [fx("char_player", "Compliance_Resistance", -0.024), fx("char_player", "pCompliance_Resistance", -0.012),
             fx("char_player", "Public_Standing", -0.024),
             fx("char_player", "Theological_Conviction", 0.024), fx("char_player", "pTheological_Conviction", 0.012),
             fx("char_ibnhanbal", "Public_Standing", 0.024),
             fx("char_amma", "Theological_Conviction", 0.024)]),
    ],
    desirability=7.0, gx=800, gy=-100))


# ═══════════════════════════════════════════════════════════════════════════════
# 5. SPECIALIZED SCHOLARSHIPS
# ═══════════════════════════════════════════════════════════════════════════════

policy_encounters.append(policy_enc("page_pol_scholarships", "The Allocation of Minds",
    "The House of Wisdom has a budget for sponsored scholars—stipends for promising students to study full-time. You sit on the allocation committee. This year, the candidates include:\n\nA young mathematician from Khwarezm who is developing a new method for solving equations using symbols instead of words. (His name is Muhammad ibn Musa al-Khwarizmi. You do not yet know that 'algorithm' will be derived from his name and 'algebra' from his book.)\n\nA hadith scholar from Basra who has memorized 300,000 narrations and is developing a rigorous method for grading their authenticity. (The science of hadith criticism—'ilm al-rijal—will become the Islamic world's most sophisticated system of source evaluation.)\n\nA physician from Jundishapur who wants to translate Galen's complete anatomical works and test them against clinical observation. (The empirical medical tradition will save millions of lives across centuries.)\n\nThe budget supports two full scholarships. You must choose.",
    [
        popt("page_pol_scholarships", 0,
            "Fund the mathematician and the physician. The rational sciences have immediate practical value and long-term civilizational impact.",
            "Al-Khwarizmi receives his stipend and completes the Kitab al-Jabr—the foundational text of algebra. The physician translates Galen and, finding errors, begins a tradition of empirical correction that will culminate in Ibn Sina's Canon of Medicine.\n\nThe hadith scholar returns to Basra unfunded. He continues his work anyway—hadith memorization requires only memory, not equipment. But the systematic grading methodology he's developing is delayed by a decade. When it finally matures, it will lack the institutional support that the House of Wisdom could have provided.\n\nYou funded the future of mathematics and medicine. You underfunded the future of Islamic epistemology. The hadith sciences will develop anyway—but slower, and in the hands of scholars who distrust the institution that rejected them. The House of Wisdom's reputation as anti-hadith solidifies. The rift between 'aqliyya (rational sciences) and naqliyya (transmitted sciences) gains an institutional dimension.",
            [fx("char_player", "Aql_Naql", 0.045), fx("char_player", "pAql_Naql", 0.022),
             fx("char_player", "Public_Standing", 0.024),
             fx("char_caliph", "Aql_Naql", 0.024),
             fx("char_player", "Compliance_Resistance", 0.024)]),
        popt("page_pol_scholarships", 1,
            "Fund the hadith scholar and the physician. Transmitted knowledge and empirical medicine—the heritage and the health of the ummah.",
            "The hadith scholar produces his masterwork: a systematic grading of 300,000 narrations by chain reliability, narrator integrity, and textual consistency. It becomes the gold standard for Islamic source criticism—a methodology so rigorous that modern historians use it to this day.\n\nThe physician's translations save lives immediately. Clinical observation begins correcting Greek anatomical errors.\n\nAl-Khwarizmi finds patronage elsewhere—a provincial governor in Khurasan who values mathematics for land survey and tax calculation. The algebra book is written anyway, but in a provincial context, without the House of Wisdom's editorial infrastructure. It is slightly less polished, slightly less widely distributed. The world receives algebra. It receives it six months later and from a less prestigious address.\n\nYou chose heritage over innovation. The hadith sciences flourish. Mathematics flourishes anyway—genius finds funding. The question is whether the committee's job is to fund what would happen regardless or to fund what would not.",
            [fx("char_player", "Aql_Naql", -0.024), fx("char_player", "pAql_Naql", -0.012),
             fx("char_player", "Public_Standing", 0.024), fx("char_player", "pPublic_Standing", 0.012),
             fx("char_ibnhanbal", "Public_Standing", 0.024),
             fx("char_player", "Theological_Conviction", 0.024)]),
        popt("page_pol_scholarships", 2,
            "Fund the mathematician and the hadith scholar. Both are developing new methodologies—one for numbers, one for sources. The physician can find medical patronage anywhere.",
            "You recognize what the other committee members miss: both al-Khwarizmi and the hadith scholar are doing the same thing at different levels—building systems for evaluating and organizing knowledge. Algebra systematizes mathematical reasoning. Hadith criticism systematizes narrative reliability. Both are epistemic infrastructure.\n\nThe two scholars, funded side by side, begin an unlikely friendship. The mathematician is fascinated by the hadith scholar's chain-of-transmission analysis—it resembles a directed graph. The hadith scholar borrows the mathematician's notation system to diagram complex isnads. Neither converts to the other's field. Both are enriched.\n\nThe physician finds patronage at the bimaristan (hospital) and completes his Galen translations on clinical time. He is slightly resentful. But the cross-pollination between mathematical and hadith methodology—the accidental synthesis of your allocation—produces something no one anticipated: a culture where rigor is valued regardless of whether it serves aql or naql.",
            [fx("char_player", "Aql_Naql", 0.012), fx("char_player", "pAql_Naql", 0.006),
             fx("char_player", "Public_Standing", 0.045), fx("char_player", "pPublic_Standing", 0.022),
             fx("char_player", "Theological_Conviction", 0.045), fx("char_player", "pTheological_Conviction", 0.022),
             fx("char_amma", "Aql_Naql", 0.024)]),
    ],
    desirability=6.5, gx=800, gy=0))


# ═══════════════════════════════════════════════════════════════════════════════
# 6. THE ENFORCEMENT QUESTION
# ═══════════════════════════════════════════════════════════════════════════════

policy_encounters.append(policy_enc("page_pol_enforcement", "The Instrument of the Mihna",
    "A second policy council. Al-Ma'mun has died. Al-Mu'tasim continues the Mihna, but the question of enforcement intensity is now open.\n\nThe chief qadi, ibn Abi Du'ad, presents three enforcement regimes:\n\n\"FULL ENFORCEMENT: Every scholar, judge, teacher, and imam must affirm. Those who refuse are removed from office and imprisoned. Repeat offenders are flogged publicly. This is al-Ma'mun's original vision.\"\n\n\"SELECTIVE ENFORCEMENT: Only those in state-funded positions must affirm. Private scholars, mosque imams without state salary, and teachers in informal circles are left alone. The Mihna applies to the government, not the ummah.\"\n\n\"ADMINISTRATIVE ENFORCEMENT: Affirmation is required on paper—a signed document—but no oral examination, no public spectacle. Scholars sign, file the document, and return to teaching whatever they believe. The state has its compliance on record. The scholars have their conscience intact.\"\n\nIbn Abi Du'ad favors full enforcement. \"Half measures make us look weak.\" The vizier favors administrative enforcement. \"It's cheaper.\" Al-Mu'tasim looks at you.",
    [
        popt("page_pol_enforcement", 0,
            "\"Full enforcement. If the theological position is correct—and we believe it is—then it must be held consistently. A truth that bends for convenience is not truth.\"",
            "Full enforcement continues. The floggings resume. Ibn Hanbal suffers. Others suffer more quietly—dismissed qadis losing their income, teachers barred from their circles, imams replaced by Mu'tazili appointees who recite the creed but lack the congregation's trust.\n\nThe machinery is effective. Within two years, every state-employed scholar has affirmed. The private scholars have gone underground. The informal teaching circles now meet in homes, in gardens, in the back rooms of bathhouses. The knowledge transmission continues—but now with the additional curriculum of martyrdom, persecution, and institutional distrust.\n\nYou have achieved theological uniformity in the bureaucracy. You have also created a parallel ummah that defines itself by its resistance to you. When al-Mutawakkil reverses the Mihna, the parallel ummah emerges as the dominant force. The full enforcement built the movement that would undo everything it enforced.",
            [fx("char_player", "Compliance_Resistance", 0.060), fx("char_player", "pCompliance_Resistance", 0.030),
             fx("char_player", "Public_Standing", -0.060), fx("char_player", "pPublic_Standing", -0.030),
             fx("char_caliph", "Compliance_Resistance", 0.045),
             fx("char_ibnhanbal", "Public_Standing", 0.045),
             fx("char_amma", "Compliance_Resistance", -0.060),
             fx("char_amma", "Public_Standing", -0.045)]),
        popt("page_pol_enforcement", 1,
            "\"Selective enforcement. The state controls its employees. It does not control God's scholars. Separate the institutional question from the theological one.\"",
            "A middle path. State-funded qadis, teachers, and administrators must affirm. Private scholars are left alone. Ibn Hanbal—who holds no state position—is quietly released. No public statement, no reversal. He simply walks out of the prison one morning and goes home.\n\nThe Mu'tazili scholars are unhappy. \"This guts the Mihna. If private scholars can teach whatever they want, the state's position becomes a formality.\" Yes. That is precisely the point. The state's position becomes an employment condition, not a creed. The theological question returns to the scholars. The political question is resolved by pragmatism.\n\nIbn Hanbal resumes teaching. His followers multiply. The Mu'tazili scholars still hold the state positions. Two theological ecosystems coexist—one funded, one unfunded, both alive. It is untidy. It is also sustainable. When al-Mutawakkil reverses the Mihna, the transition is smooth—nothing was truly at stake except government paychecks.",
            [fx("char_player", "Compliance_Resistance", 0.024), fx("char_player", "pCompliance_Resistance", 0.012),
             fx("char_player", "Public_Standing", 0.045), fx("char_player", "pPublic_Standing", 0.022),
             fx("char_player", "Aql_Naql", 0.012), fx("char_player", "pAql_Naql", 0.006),
             fx("char_caliph", "Public_Standing", 0.024),
             fx("char_ibnhanbal", "Compliance_Resistance", -0.024),
             fx("char_amma", "Public_Standing", 0.024)]),
        popt("page_pol_enforcement", 2,
            "\"Administrative enforcement. A signed document. No examinations, no floggings, no spectacle. The state gets its paper trail. The scholars keep their skin.\"",
            "The signed-document regime is implemented. Scholars queue at the qadi's office, sign a formulaic affirmation ('I attest that the Quran is the created speech of God, glory be to Him'), and leave. Some sign with visible reluctance. Some sign and immediately go to the mosque to teach that the Quran is uncreated. The document sits in a drawer. No one reads it.\n\nIbn Hanbal refuses to sign. Of course he does—even administrative compliance violates his principle. But he is now the only holdout. The spectacle of mass refusal is replaced by the spectacle of one man's stubbornness. It is less dramatic, less galvanizing, less useful as a rallying point.\n\nThe Mihna becomes a filing exercise. The theological question is not resolved—it is bureaucratized. Ibn Abi Du'ad is disgusted. \"You have reduced God's truth to a signature on a form.\" Perhaps. But forms don't leave scars.",
            [fx("char_player", "Compliance_Resistance", 0.045), fx("char_player", "pCompliance_Resistance", 0.022),
             fx("char_player", "Public_Standing", 0.024), fx("char_player", "pPublic_Standing", 0.012),
             fx("char_player", "Theological_Conviction", -0.024),
             fx("char_caliph", "Compliance_Resistance", 0.024),
             fx("char_amma", "Compliance_Resistance", 0.024)]),
    ],
    desirability=6.0, gx=800, gy=100))


# ═══════════════════════════════════════════════════════════════════════════════
# 7. THE TRANSLATION PRIORITY
# ═══════════════════════════════════════════════════════════════════════════════

policy_encounters.append(policy_enc("page_pol_translation", "What the House of Wisdom Translates Next",
    "The House of Wisdom's translation bureau has capacity for one major project this year. Three manuscripts have arrived from Constantinople, purchased at enormous expense by al-Ma'mun's agents:\n\nPlato's Republic—the complete text, including the sections on the philosopher-king, the allegory of the cave, and the noble lie. (The Mu'tazili scholars want this desperately: a rational model for the just state, authored by the greatest pagan philosopher.)\n\nGalen's De Usu Partium (On the Usefulness of Parts)—a complete anatomical treatise that would revolutionize medicine. The bimaristan physicians are begging for it.\n\nA collection of Indian mathematical texts including the Brahmasphutasiddhanta, which contains the concept of zero, negative numbers, and techniques for solving what will later be called quadratic equations.\n\nThe committee must choose one. Translation is expensive: the scholars who can read Greek or Sanskrit are rare, and the calligraphy alone takes months.",
    [
        popt("page_pol_translation", 0,
            "Translate Plato's Republic. A rational theory of justice is what the Mihna's architects need—and what its critics need to refute.",
            "The Republic enters Arabic as al-Siyasa al-Madaniyya. Its impact is seismic. The Mu'tazili scholars seize on the philosopher-king concept—the Caliph as rational arbiter of truth, justified by wisdom rather than lineage. The noble lie section is quietly suppressed in the first copies; then someone leaks it, and the traditionalists have a field day. \"Your Greek philosopher advocates lying to the masses for their own good. How is this different from the Mihna?\"\n\nAl-Farabi, a generation later, will build his entire political philosophy on the Republic's framework. But the damage is done: Plato's political philosophy becomes permanently associated with the Mihna's coercive rationalism. The Republic is the most important and most dangerous text the House of Wisdom has ever produced.\n\nThe medical and mathematical texts wait. People continue to die from treatable conditions. Accountants continue to use clumsy Roman numerals. You chose philosophy over utility. Whether that was wise depends on how you weigh the life of the mind against the life of the body.",
            [fx("char_player", "Aql_Naql", 0.060), fx("char_player", "pAql_Naql", 0.030),
             fx("char_player", "Public_Standing", -0.024),
             fx("char_caliph", "Aql_Naql", 0.045),
             fx("char_player", "Theological_Conviction", 0.024)]),
        popt("page_pol_translation", 1,
            "Translate Galen's anatomy. Medicine saves lives regardless of theology. The bimaristan needs this now.",
            "The anatomical translation enters the bimaristan within the year. Physicians immediately begin identifying errors in their existing practices. A surgeon discovers that Galen's description of the liver has seven lobes; human livers have four. The tradition of empirical correction of Greek authority begins here—in a dissection room, not a theology seminar.\n\nAl-Razi (Rhazes), a generation later, will build on this tradition to produce the first clinical distinction between smallpox and measles. Ibn al-Nafis will use it to discover pulmonary circulation three centuries before William Harvey.\n\nThe Mu'tazili scholars are disappointed. They wanted the Republic. The mathematicians are disappointed. They wanted zero. The physicians are saving lives. When the plague hits Baghdad in the next decade, the translated Galen will save more people than any theological position, Mu'tazili or Hanbali, ever could.",
            [fx("char_player", "Aql_Naql", 0.024), fx("char_player", "pAql_Naql", 0.012),
             fx("char_player", "Public_Standing", 0.045), fx("char_player", "pPublic_Standing", 0.022),
             fx("char_amma", "Public_Standing", 0.045),
             fx("char_player", "Theological_Conviction", 0.024)]),
        popt("page_pol_translation", 2,
            "Translate the Indian mathematics. Zero, negative numbers, and quadratic equations will transform commerce, astronomy, and engineering.",
            "The Indian texts are translated by a team that includes al-Khwarizmi himself. The concept of zero enters Islamic mathematics—and through it, eventually, the entire world. The positional number system (what Europe will call 'Arabic numerals') replaces the clumsy alphabetic system. Merchants can now do in minutes what took hours.\n\nThe impact is infrastructural, not dramatic. No one writes poems about zero. No theologian debates its implications. But within a generation, the Abbasid tax system is reformed, astronomical tables are recalculated with unprecedented precision, and the engineering of bridges, canals, and irrigation systems advances by a century.\n\nThe Republic and Galen wait. The philosophical and medical revolutions are delayed. But the mathematical foundation—the operating system on which all other sciences will run—is laid. You chose the invisible infrastructure. History will not credit you specifically. History will credit the number zero.",
            [fx("char_player", "Aql_Naql", 0.024), fx("char_player", "pAql_Naql", 0.012),
             fx("char_player", "Public_Standing", 0.024), fx("char_player", "pPublic_Standing", 0.012),
             fx("char_player", "Theological_Conviction", 0.024), fx("char_player", "pTheological_Conviction", 0.012),
             fx("char_amma", "Aql_Naql", 0.024)]),
    ],
    desirability=5.5, gx=800, gy=200))


# ═══ Wire encounters into spool and save ═════════════════════════════════════

policy_ids = [e["id"] for e in policy_encounters]
for sp in sw["spools"]:
    if sp["id"] == "spool_policy":
        sp["encounters"] = policy_ids

sw["encounters"].extend(policy_encounters)

with open(path, "w", encoding="utf-8") as f:
    json.dump(sw, f, indent=2, ensure_ascii=False)

print(f"Added {len(policy_encounters)} policy encounters. Total encounters: {len(sw['encounters'])}")
print("Policy encounters:")
for e in policy_encounters:
    nopts = len(e["options"])
    print(f"  {e['id']:30s} {e['title']:45s} opts={nopts}")
