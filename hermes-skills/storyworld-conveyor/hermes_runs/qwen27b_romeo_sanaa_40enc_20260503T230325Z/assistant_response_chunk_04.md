Let me analyze what's being asked:

1. This is a request for "chunk 4" of a storyworld design packet
2. The theme is Romeo and Juliet set in Sana'a between a Sunni boy and Shia girl
3. I need to create exactly 8 encounters with specific IDs (c04_25 through c04_32)
4. Encounters c04_25-28 are act2, c04_29-32 are act3
5. Each encounter needs exactly 3 visible options
6. Secret options on c04_28 and c04_31
7. Content themes: exile threat, family ultimatum, Zahra's clinic plan, Rami's hiding place, false death rumor, elders witnessing costs

The user says "Do not use tools" - so I should just produce the content directly without calling any of my available tools.

Let me create this storyworld packet with proper JSON structure:
- title, subtitle, about, characters, variables, encounters fields required
- 8 encounters with specific IDs
- Each encounter has options (3 visible) + some have secret_option

I need to ensure the JSON is valid and parses correctly.
BEGIN_STORYWORLD_PACKET
{
  "title": "Sana'a Hearts",
  "subtitle": "A Story of Two Families, One City",
  "about": "Romeo and Juliet reimagined in contemporary Sana'a, where a Sunni boy named Rami and a Shia girl named Zahra discover love amid ancient divides. After their secret meeting is witnessed publicly, the city itself becomes an obstacle as families, reputation, and fear collide.",
  "characters": {
    "Rami": "Sunni boy, 19, studying medicine at Sana'a University. Quietly rebellious against family expectations to join his father's business.",
    "Zahra": "Shia girl, 18, volunteer at a neighborhood clinic. Sharp-witted and protective of her community's dignity.",
    "Abdullah": "Rami's father, respected Sunni merchant who believes in tradition as the glue holding families together.",
    "Hassan": "Zahra's uncle, Shia community elder who sees political opportunity in the scandal.",
    "Amina": "Zahra's mother, weary widow trying to keep her daughter safe while preserving family honor."
  },
  "variables": {
    "Secrecy_Disclosure": "Tracks whether the relationship is hidden or known. Low = secret kept; High = widely disclosed.",
    "Family_Truce": "Whether both families have agreed to pause hostilities temporarily.",
    "Sectarian_Trust": "The level of inter-community cooperation available for resolution.",
    "Love_Duty": "Internal conflict between romantic commitment and familial obligation."
  },
  "encounters": [
    {
      "id": "c04_25",
      "title": "The Exile Threat",
      "act": "act2",
      "description": "Abdullah has summoned Rami to the family compound. News travels fast in Sana'a, and your father says he can no longer protect you here if you continue this path.",
      "text": "\"You have shamed us,\" Abdullah says from behind his desk. \"A Shia girl. In public. With half the market watching.\" He slides a paper across the mahogany. \"My brother's family has arrangements in Dammam. You will leave tomorrow.\"",
      "options": [
        {
          "label": "[procedure] Request time to finish exams before leaving",
          "effect": {"Family_Truce": 1, "Love_Duty": -1},
          "next": "c04_26"
        },
        {
          "label": "[justice] Demand to know what punishment Zahra faces",
          "effect": {"Sectarian_Trust": -1, "Family_Truce": -1},
          "next": "c04_27"
        },
        {
          "label": "[disclosure] Reveal you've already told her family about us",
          "effect": {"Secrecy_Disclosure": 2, "Family_Truce": 2},
          "next": "c04_25_branch_disclosed"
        }
      ]
    },
    {
      "id": "c04_26",
      "title": "Family Ultimatum",
      "act": "act2",
      "description": "You've stalled the exile, but Abdullah has brought in reinforcements. A cousin from Riyadh is here to discuss 'arrangements' for both your future.",
      "text": "The air in the room grows heavy with the presence of Uncle Mahmoud from Riyadh. He brings news of a suitable brideâ€”daughter of a prominent family in Jeddah, well-educated, understanding. \"You're twenty,\" he says. \"It's time to think like a man, not a boy dreaming fantasies.\"",
      "options": [
        {
          "label": "[order] Agree to meet the woman, buy more time",
          "effect": {"Family_Truce": 2, "Love_Duty": -2},
          "next": "c04_27"
        },
        {
          "label": "[identity] Reject outrightâ€”say you've already chosen",
          "effect": {"Family_Truce": -3, "Secrecy_Disclosure": 1},
          "next": "c04_28"
        },
        {
          "label": "[symbol] Show them Zahra's clinic volunteer certificateâ€”she helps everyone",
          "effect": {"Sectarian_Trust": 1, "Family_Truce": 0},
          "next": "c04_27"
        }
      ]
    },
    {
      "id": "c04_27",
      "title": "Zahra's Clinic Plan",
      "act": "act2",
      "description": "You slip away to the clinic where Zahra works. She's heard rumors and has a plan of her own.",
      "text": "\"My uncle wants to use us as leverage,\" Zahra says, voice low behind the pharmacy counter. \"But my motherâ€”she doesn't want war.\" She shows you papers: transfer records for a student exchange program in Beirut. Two universities with partnerships. \"We study together there. The distance makes us forget nothing, but makes everything survivable.\"",
      "options": [
        {
          "label": "[transmission] Agreeâ€”send the application tomorrow",
          "effect": {"Love_Duty": 2, "Family_Truce": -1},
          "next": "c04_28"
        },
        {
          "label": "[community] Suggest involving respected teachers as intermediaries first",
          "effect": {"Sectarian_Trust": 2, "Love_Duty": 1},
          "next": "c04_29"
        },
        {
          "label": "[mercy] Tell her you can't leave your family like thisâ€”they need me",
          "effect": {"Love_Duty": -2, "Family_Truce": 1},
          "next": "c04_28"
        }
      ]
    },
    {
      "id": "c04_28",
      "title": "Rami's Hiding Place",
      "act": "act2",
      "description": "The pressure is too much. You need somewhere to think, somewhere the city can't find you.",
      "text": "You find yourself at the old Ottoman-era house your grandfather once ownedâ€”now abandoned, keys hidden under a loose stone in the courtyard wall. Inside, time has stood still. Your grandmother's calligraphy hangs on one wall. A place where she taught you to read before she died, before the divide hardened between Sunni and Shia neighbors.",
      "options": [
        {
          "label": "[spirit] Pray here, ask for clarity",
          "effect": {"Love_Duty": 1},
          "next": "c04_29"
        },
        {
          "label": "[letter] Write to Zahraâ€”tell her everything you've been afraid to say",
          "effect": {"Secrecy_Disclosure": 0, "Love_Duty": 2},
          "next": "c04_30"
        },
        {
          "label": "[purpose] Make a decision: you won't let them break this",
          "effect": {"Sectarian_Trust": -1, "Family_Truce": -2},
          "next": "c04_29"
        }
      ],
      "secret_option": {
        "label": "[witness] Find your grandmother's old notebookâ€”she wrote about her own forbidden love",
        "requirement": "Love_Duty >= 3 or has item 'grandmother's ring'",
        "effect": {"Sectarian_Trust": 2, "identity": "unlocked"},
        "next": "c04_31"
      }
    },
    {
      "id": "c04_29",
      "title": "The False Death Rumor",
      "act": "act3",
      "description": "Morning brings news that stops the city in its tracks.",
      "text": "By dawn, whispers have become certainty: Zahra is dead. A car accident on the way to university. The rumor spreads faster than truthâ€”through mosque announcements, WhatsApp groups, market gossip. You find yourself outside her family's house as men arrive with condolences.",
      "options": [
        {
          "label": "[reason] Knock and ask directly before believing",
          "effect": {"Secrecy_Disclosure": 1},
          "next": "c04_30"
        },
        {
          "label": "[transmission] Call her phoneâ€”she won't answer if she's gone",
          "effect": {},
          "next": "c04_30_branch_call"
        },
        {
          "label": "[veil] Let it passâ€”some truths aren't yours to confirm yet",
          "effect": {"Love_Duty": -2},
          "next": "c04_31"
        }
      ]
    },
    {
      "id": "c04_30",
      "title": "The Living Truth",
      "act": "act3",
      "description": "You find Zahra at the clinic, bruised and angry.",
      "text": "\"Someone wanted our families to stop negotiating,\" she says, pressing ice to a cut on her temple. \"Uncle Hassan's friends spread it. If my family thinks you're grieving, they'll push for blood money or revengeâ€”and that locks us into being enemies forever.\" She looks at you with something harder than love now.",
      "options": [
        {
          "label": "[consensus] Go together to both familiesâ€”end the rumors publicly",
          "effect": {"Secrecy_Disclosure": 3, "Sectarian_Trust": 2},
          "next": "c04_31"
        },
        {
          "label": "[mercy] Leave her beâ€”she needs to handle her own family",
          "effect": {"Love_Duty": -1, "Family_Truce": 0},
          "next": "c04_32"
        },
        {
          "label": "[justice] Confront Hassan directlyâ€”he started this",
          "effect": {"Sectarian_Trust": -2, "Family_Truce": -1},
          "next": "c04_31"
        }
      ]
    },
    {
      "id": "c04_31",
      "title": "Elders as Witnesses",
      "act": "act3",
      "description": "You've gathered a small groupâ€”two Sunni elders, two Shia. They sit in a quiet teahouse on the edge of the old city.",
      "text": "\"We're not here to bless anything,\" says Sheikh Omar, Sunni elder and respected teacher. \"But if tragedy is coming, I want it known that we tried otherwise.\" Zahra's uncle Hassan arrives late, scowling. The city has heard you plan to meetâ€”someone will be watching.",
      "options": [
        {
          "label": "[precedent] Share the story of your grandmother and her lost love",
          "effect": {"Sectarian_Trust": 2, "Family_Truce": 1},
          "next": "c04_32"
        },
        {
          "label": "[community] Ask them to mediate a formal truce between families",
          "effect": {"Family_Truce": 2, "Sectarian_Trust": 2},
          "next": "c04_32_branch_truce"
        },
        {
          "label": "[order] Propose the Beirut plan formallyâ€”let them decide",
          "effect": {"Love_Duty": 1, "Secrecy_Disclosure": 1},
          "next": "c04_32"
        }
      ],
      "secret_option": {
        "label": "[witness] Present evidence that Hassan orchestrated the death rumor",
        "requirement": "has item 'clinic security footage' or Sectarian_Trust <= -1",
        "effect": {"Sectarian_Trust": 3, "Family_Truce": 2},
        "next": "c04_32"
      }
    },
    {
      "id": "c04_32",
      "title": "The City Watches",
      "act": "act3",
      "description": "The meeting breaks up as shouts echo from the street. Someone has brought your families here.",
      "text": "Abdullah stands at the teahouse entrance, face unreadable. Behind him, Amina holds Zahra's hand tightly. The elders rise uncertainly. Sheikh Omar speaks first: \"You've come for answers. But the question is whether you're ready to hear what repair actually costs.\" The street fills with onlookers.",
      "options": [
        {
          "label": "[disclosure] Step forward and take Zahra's handâ€”let the city see",
          "effect": {"Secrecy_Disclosure": 4, "Love_Duty": 3},
          "next": "ENDING_public_choice"
        },
        {
          "label": "[mercy] Let your father speak firstâ€”give him dignity",
          "effect": {"Family_Truce": 2, "Secrecy_Disclosure": -1},
          "next": "ENDING_family_dignity"
        },
        {
          "label": "[symbol] Offer the Beirut papers as a third path",
          "effect": {"Sectarian_Trust": 1, "Family_Truce": 1},
          "next": "ENDING_beirut_path"
        }
      ]
    }
  ]
}
END_STORYWORLD_PACKET
