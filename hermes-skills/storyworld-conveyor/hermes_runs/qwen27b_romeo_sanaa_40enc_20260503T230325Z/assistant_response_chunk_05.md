The user wants me to produce chunk 5 of a storyworld design packet. This is the final chunk covering Act 3 (the endgame). Let me think through what needs to be included:

1. **6 encounters** with IDs `c05_33` through `c05_38`
2. All in `act3`
3. Each has exactly 3 visible options, plus secret options on c05_34 and c05_37
4. Coverage: failed messenger repair, night refuge, apparent death/disappearance (no cheap melodrama), final public witness gathering, last pre-verdict choice

Let me design the encounters:

**c05_33 - Failed Messenger Repair**: The lovers try one more time to get their families to listen through intermediaries. The messenger (perhaps a respected elder or cleric) fails to bridge the gap - revealing how deep and calcified the feud has become.

**c05_34 - Night Refuge**: After the failed repair, they seek shelter somewhere - perhaps an old mosque courtyard, abandoned house, or hospital/clinic. This is where secret_option could trigger the "secret witness" path.

**c05_35 - Apparent Death/Disappearance**: Not melodramatic poison, but something grounded - maybe one disappears into exile routes, or is believed dead after a collapse from stress/starvation in hiding, or fakes death through careful planning with sympathetic contacts.

**c05_36 - Final Public Witness Gathering**: The families and community gather for some occasion (funeral, tribunal, public statement) where the truth comes out or must be faced.

**c05_37 - Last Pre-Verdict Choice**: The moment of reckoning - what do they choose when everything is on the line? Secret option here could lead to forcing testimony about the feud's machinery.

**c05_38 - Final Choice Scene**: Actually wait, I need 6 encounters total c05_33-38 = 6 encounters. Let me reconsider...


I'll restructure the sequence to fit exactly six encounters, ensuring each serves a critical narrative purpose while maintaining the dramatic tension and emotional depth required for this final chunk of the storyworld design packet.

The encounters will map out a precise journey: from the initial failed messenger repair through night refuge, apparent death or disappearance, public witness gathering, the final pre-verdict choice, culminating in what appears to be the decisive moment before resolution. I'll carefully track how each encounter connects thematically and emotionally, ensuring the narrative arc builds toward its inevitable conclusion while leaving room for nuanced interpretation. I need 6 encounters total (c05_33 through c05_38), then the final_encounter text block, secret_bridge text, and endings array.

So:
- c05_33 - Failed messenger repair attempt
- c05_34 - Night refuge sought (secret_option here)
- c05_35 - Apparent death/disappearance (grounded)
- c05_36 - Final public witness gathering
- c05_37 - Last pre-verdict choice (secret_option here)
- c05_38 - The verdict/confrontation scene

Then final_encounter is the actual ending choice text. Let me write this out now.
BEGIN_STORYWORLD_PACKET
{
  "title": "Sana'a Hearts",
  "subtitle": "A Story of Love in Divided Streets",
  "about": "Romeo and Juliet reimagined between a Sunni boy and Shia girl in Sana'a, where family honor and sectarian divides collide with young love. The tragedy route remains possible, but reconciliation, exile, public witness, and a secret ending are all available.",

  "characters": [
    {"id": "karim", "name": "Karim", "role": "protagonist", "family": "Al-Zahrani", "sect": "Sunni", "description": "Son of a respected merchant, twenty-one, studying law at the university"},
    {"id": "layla", "name": "Layla", "role": "protagonist", "family": "Al-Husayni", "sect": "Shia", "description": "Daughter of a judge's brother, nineteen, teaching at a community school"},
    {"id": "omar_karim_father", "name": "Omar Al-Zahrani", "role": "antagonist", "family": "Al-Zahrani", "sect": "Sunni", "description": "Karim's father, merchant council member"},
    {"id": "ahmed_layla_father", "name": "Ahmed Al-Husayni", "role": "antagonist", "family": "Al-Husayni", "sect": "Shia", "description": "Layla's father, retired judge"}
  ],

  "variables": {
    "Secrecy_Disclosure": {"range": [0, 100], "description": "How publicly known the relationship is"},
    "Family_Truce": {"range": [0, 100], "description": "Willingness of families to negotiate peace"},
    "Sectarian_Trust": {"range": [0, 100], "description": "Community-level trust between Sunni and Shia factions"},
    "Love_Duty": {"range": [-50, 50], "description": "Lovers' balance: positive favors love over duty, negative the reverse"}
  },

  "encounters": [
    {
      "id": "c05_33",
      "title": "The Last Messenger",
      "act": "act3",
      "description": "You seek Shaykh Ibrahim, an elder known to counsel both families. He agrees to hear your pleaâ€”but warns you the feud runs deeper than one conversation.",
      "text": "Shaykh Ibrahim listens in silence as you explain. When you finish, he sighs, removing his glasses. 'The Al-Zahrani and Al-Husayni families have been enemies since before either of you was born,' he says. 'Your grandfather killed my cousin's brother-in-law over a land dispute mixed with sectarian rhetoric. The wound has festered through three generations.' He pauses. 'I can tryâ€”but I cannot promise the men will listen to reason when fear and reputation speak louder.'",
      "options": [
        {
          "id": "o1",
          "text": "Ask him to meet with both fathers together, presenting your case directly",
          "effect": {"Family_Truce": 10, "Secrecy_Disclosure": 20},
          "next": "c05_34"
        },
        {
          "id": "o2",
          "text": "Request he speak to each father separately first, then bring them together",
          "effect": {"Family_Truce": 5, "Secrecy_Disclosure": 10},
          "next": "c05_34"
        },
        {
          "id": "o3",
          "text": "Accept his warning and prepare for another path entirely",
          "effect": {"Family_Truce": -5, "Love_Duty": -10},
          "next": "c05_34"
        }
      ]
    },

    {
      "id": "c05_34",
      "title": "Night Refuge in the Old Quarter",
      "act": "act3",
      "description": "The shaykh's attempt failsâ€”each father refuses even to enter the same room. You and Layla seek refuge in an abandoned courtyard house in the old quarter, where a sympathetic midwife lets you stay.",
      "text": "Midnight. The courtyard is quiet except for distant prayer calls blending from Sunni and Shia mosques nearby. Layla sits beside you on the stone floor, her head on your shoulder. 'We cannot stay hidden forever,' she whispers. 'The midwife cannot protect us indefinitely.' You look at each otherâ€”lovers who have found no shelter in this city of divided loyalties.",
      "options": [
        {
          "id": "o1",
          "text": "Plan to flee Sana'a together while the night still offers cover",
          "effect": {"Secrecy_Disclosure": -20, "Love_Duty": 15},
          "next": "c05_35"
        },
        {
          "id": "o2",
          "text": "Stay hidden longerâ€”hope may yet find a way through",
          "effect": {"Secrecy_Disclosure": -10, "Family_Truce": 5},
          "next": "c05_35"
        },
        {
          "id": "o3",
          "text": "Make a public statement tomorrowâ€”force the city to witness your love",
          "effect": {"Secrecy_Disclosure": 40, "Sectarian_Trust": -10},
          "next": "c05_36"
        }
      ],
      "secret_option": {
        "id": "so_bridge",
        "text": "[Hidden] Speak with the midwife about gathering witnesses to the feud's machinery",
        "requirement": "Sectarian_Trust >= 40 AND player has chosen 'community' or 'consensus' in previous encounters",
        "effect": {"unlock_secret_bridge": true, "Secrecy_Disclosure": 25},
        "next": "c05_37"
      }
    },

    {
      "id": "c05_35",
      "title": "The Disappearance",
      "act": "act3",
      "description": "Days pass. Rumors spread through Sana'a's markets and mosquesâ€”whispers that Layla has vanished, or worse.",
      "text": "Your mother finds you at the university: 'They say she collapsed in hiding and died alone.' But you know Layla better than death knows her heart. You search the old quarter, the clinic where she sometimes volunteers, the mosque courtyard where you first kissed. Nothing. Then a letter arrivesâ€”not from her hand, but sealed with Al-Husayni insignia: 'She has been taken to Taiz by relatives for her safety.'",
      "options": [
        {
          "id": "o1",
          "text": "Ride to Taiz immediatelyâ€”nothing will stop you from reaching her",
          "effect": {"Love_Duty": 20, "Family_Truce": -15},
          "next": "c05_36"
        },
        {
          "id": "o2",
          "text": "Wait and send a message through the midwife first",
          "effect": {"Love_Duty": 5, "Secrecy_Disclosure": -5},
          "next": "c05_36"
        },
        {
          "id": "o3",
          "text": "Confront your fatherâ€”demand he help you find her before it's too late",
          "effect": {"Family_Truce": 15, "Secrecy_Disclosure": 20},
          "next": "c05_36"
        }
      ]
    },

    {
      "id": "c05_36",
      "title": "The Gathering at Al-Sumayya Mosque",
      "act": "act3",
      "description": "A community gathering is calledâ€”not for prayer, but to address the growing scandal. Both families are present. The city watches.",
      "text": "Al-Sumayya mosque courtyard fills with men and women from both quarters. Your father stands beside Omar Al-Husayniâ€”Layla's uncleâ€”who holds a letter in his hand. 'We have received word,' he announces, 'that the young woman is alive, but has fled Sana'a with her lover.' Silence falls. Eyes turn toward you. The city demands an account.",
      "options": [
        {
          "id": "o1",
          "text": "Step forward and admit everythingâ€”take full responsibility",
          "effect": {"Secrecy_Disclosure": 50, "Family_Truce": -10},
          "next": "c05_37"
        },
        {
          "id": "o2",
          "text": "Remain silentâ€”let the elders speak first",
          "effect": {"Secrecy_Disclosure": 10, "Family_Truce": 5},
          "next": "c05_37"
        },
        {
          "id": "o3",
          "text": "Speak of love transcending divisionâ€”appeal to the community's better nature",
          "effect": {"Sectarian_Trust": 15, "Family_Truce": 10},
          "next": "c05_37"
        }
      ]
    },

    {
      "id": "c05_37",
      "title": "The Choice Before the Verdict",
      "act": "act3",
      "description": "The elders reach a preliminary consensus. You have one moment to speak before the final judgment is delivered.",
      "text": "Shaykh Ibrahim turns to you: 'The community must decide your fate, young man. Will you be exiled for dishonoring both families? Will you be forced into marriage with another woman to repair the Al-Zahrani name? Or will some other path be found?' He looks at your father, then at Omar Al-Husayni. The men exchange glancesâ€”calculations of reputation, fear, and something softer that might be regret.",
      "options": [
        {
          "id": "o1",
          "text": "Accept exileâ€”leave Sana'a to preserve family honor while staying with Layla",
          "effect": {"Family_Truce": 20, "Love_Duty": 25},
          "next": "final_encounter"
        },
        {
          "id": "o2",
          "text": "Demand the right to marry Layla properlyâ€”through all due channels",
          "effect": {"Family_Truce": 30, "Secrecy_Disclosure": 40},
          "next": "final_encounter"
        },
        {
          "id": "o3",
          "text": "Offer yourself to community serviceâ€”work for reconciliation as penance",
          "effect": {"Sectarian_Trust": 25, "Family_Truce": 15},
          "next": "final_encounter"
        }
      ],
      "secret_option": {
        "id": "so_witness",
        "text": "[Hidden] Call for the community itself to testify about how it produced this tragedy",
        "requirement": "unlock_secret_bridge is true OR player has chosen 'witness' or 'disclosure' three times",
        "effect": {"trigger_secret_bridge": true, "Sectarian_Trust": 30},
        "next": "secret_bridge"
      }
    },

    {
      "id": "c05_38",
      "title": "The City's Judgment",
      "act": "act3",
      "description": "The verdict approaches. Families, clerics, and neighbors gather for the final decision that will determine your future.",
      "text": "Sunset paints Sana'a in gold and crimson. The courtyard has become a courtroom of tradition and fear. Your father's face shows conflictâ€”pride warring with something like love. Omar Al-Husayni clears his throat: 'The girl is found to be alive, hiding in Taiz. She has sent word she will not return without him.' He looks at you. 'We have three options before us. And the city waits for our wisdomâ€”or our judgment.'",
      "options": [
        {
          "id": "o1",
          "text": "Accept whatever verdict comesâ€”trust that justice and mercy will balance",
          "effect": {"Family_Truce": 10},
          "next": "final_encounter"
        },
        {
          "id": "o2",
          "text": "Appeal to higher authoritiesâ€”the governor, the university board",
          "effect": {"Secrecy_Disclosure": 30, "Family_Truce": -5},
          "next": "final_encounter"
        },
        {
          "id": "o3",
          "text": "Propose a truce ceremonyâ€”publicly declare both families' commitment to peace",
          "effect": {"Family_Truce": 40, "Sectarian_Trust": 20},
          "next": "final_encounter"
        }
      ]
    }
  ],

  "final_encounter": "The courtyard falls silent as the elders deliver their verdict. Your father looks at you with eyes that hold both anger and grief. Omar Al-Husayni speaks first: 'We will not kill our children for loving.' Then your father: 'But we cannot let love destroy honor.' The compromise emergesâ€”exile, marriage elsewhere, a fragile peace between families bought with your absence from the city that made you.",

  "secret_bridge": "You stand before the gathered crowd and speak not of your own fate, but of theirs. 'Who taught us to hate?' you ask. 'Which checkpoint man first stopped Shia children from playing in Sunni streets? Which cleric first called our brothers heretics? Which merchant first refused trade on sectarian grounds?' One by one, men step forwardâ€”clerics admitting fear drove their rhetoric, checkpoint guards confessing they enforced division for power, neighbors revealing how rumors were manufactured. The tragedy becomes collective testimony.",

  "endings": [
    {
      "id": "ending_admin_truce",
      "title": "Administrative Truce",
      "text": "The governor intervenes with bureaucratic efficiency. A memorandum is signed: the Al-Zahrani and Al-Husayni families shall cease hostilities under penalty of fines. You and Layla are permitted to marry, provided you register your union within thirty days and relocate outside Sana'a's city limits. Love survives, administered by state machinery that neither understands nor cares about hearts.",
      "requirements": {"Family_Truce": 25}
    },

    {
      "id": "ending_family_victory",
      "title": "Family Victory",
      "text": "Honor prevails. Your father arranges your marriage to the daughter of a respected Sunni family in Aden. Layla is wed to her cousin in Beirut, far from Sana'a's divided streets. Years later, you hear rumorsâ€”she writes poetry about a boy she loved once; you keep a green scarf tucked inside your Quran. Both families celebrate their victory over love.",
      "requirements": {"Family_Truce": -10}
    },

    {
      "id": "ending_exile_together",
      "title": "Exile Together",
      "text": "You flee Sana'a under cover of night, heading north toward Aleppo where neither family's reach extends. In a small apartment overlooking the Syrian coast, you build a lifeâ€”no grand ceremonies, no community blessing, just two hearts that found each other against impossible odds. Sometimes you pray for home, but home is wherever Layla sleeps beside you.",
      "requirements": {"Love_Duty": 20}
    },

    {
      "id": "ending_tragic_deaths",
      "title": "The Tragedy",
      "text": "Desperate and cornered, you seek each other one final night in the abandoned house where you first made love. A vial of medicineâ€”meant for your mother's painâ€”is mislabeled, misunderstood. You drink together, promising to meet wherever death leads. When your families find you, they hold each other's hands across the bodies of children who died believing love could conquer division.",
      "requirements": {"Love_Duty": -20}
    },

    {
      "id": "ending_clinic_reconciliation",
      "title": "Clinic Reconciliation",
      "text": "You propose working together at a neutral clinic on the border between Sunni and Shia quarters. For six months, you treat patients side by sideâ€”Sunni mothers, Shia fathers, all bleeding the same red blood. Your fathers watch from afar as their children heal strangers without asking sect or family. Eventually, they approach each otherâ€”not as enemies, but as parents who finally understand.",
      "requirements": {"Sectarian_Trust": 30}
    },

    {
      "id": "ending_poetic_legend",
      "title": "Poetic Legend",
      "text": "Your story becomes Sana'a's own Romeo and Julietâ€”sung by mothers to restless daughters, quoted by lovers who believe theirs is the first great love. A poet writes a qasida about Karim and Layla that spreads through Yemen and beyond. Your families eventually reconcile, not for your sakes but because your legend brought shame to their feud. You are dead to them, yet alive in poetry forever.",
      "requirements": {"Secrecy_Disclosure": 50}
    },

    {
      "id": "ending_intercommunal_council",
      "title": "Fragile Council",
      "text": "Your trial becomes the catalyst for something larger. Sunni and Shia elders form a reconciliation council, meeting monthly to address grievances before they become violence. You serve as secretary; Layla teaches at a joint school. Progress is slowâ€”attacks still happen, old hatreds resurfaceâ€”but children now play in streets once divided by invisible walls. Peace, fragile but real.",
      "requirements": {"Sectarian_Trust": 40}
    },

    {
      "id": "ending_social_machinery_witness",
      "title": "Social Machinery Witness (Secret)",
      "text": "You force the city to testify about itself. Checkpoint guards admit they enforced division for power. Clerics confess fear drove their rhetoric. Merchants reveal how economic competition became sectarian warfare. Your trial becomes an inquest into Sana'a's soul, and the verdict is collective responsibility. Families don't just reconcileâ€”they transform. The social machinery that produced tragedy must now produce peace.",
      "requirements": {"trigger_secret_bridge": true}
    }
  ]
}
END_STORYWORLD_PACKET
