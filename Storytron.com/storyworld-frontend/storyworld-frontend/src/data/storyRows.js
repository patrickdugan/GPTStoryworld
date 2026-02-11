export const featuredStory = {
  id: 'featured_diplomacy',
  title: 'The Ninth Embassy',
  description:
    'A shattered peace summit forces rival envoys into a city where every favor is tracked and every promise can rewrite the next encounter.',
  // TODO: Replace placeholder image URLs with project-approved storyworld art assets.
  image:
    'https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?auto=format&fit=crop&w=1800&q=80'
}

const placeholderImages = [
  'https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=900&q=80',
  'https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?auto=format&fit=crop&w=900&q=80',
  'https://images.unsplash.com/photo-1516414447565-b14be0adf13e?auto=format&fit=crop&w=900&q=80',
  'https://images.unsplash.com/photo-1517022812141-23620dba5c23?auto=format&fit=crop&w=900&q=80',
  'https://images.unsplash.com/photo-1521295121783-8a321d551ad2?auto=format&fit=crop&w=900&q=80',
  'https://images.unsplash.com/photo-1526778548025-fa2f459cd5ce?auto=format&fit=crop&w=900&q=80'
]

const card = (id, title, meta, imageIndex) => ({
  id,
  title,
  meta,
  image: placeholderImages[imageIndex % placeholderImages.length]
})

export const storyRows = [
  {
    id: 'row_trending',
    title: 'Trending Diplomacy Worlds',
    items: [
      card('trend_01', 'Ashfall Accord', '3 active factions', 0),
      card('trend_02', 'Ivory Harbor', '12 branching outcomes', 1),
      card('trend_03', 'Silent Convoy', 'Sanctions and sabotage', 2),
      card('trend_04', 'Winter Truce', 'Resource scarcity arc', 3),
      card('trend_05', 'The Mirror Bureau', 'Loyalty pressure loop', 4),
      card('trend_06', 'Dawn Protocol', 'Counterintelligence thriller', 5)
    ]
  },
  {
    id: 'row_new',
    title: 'Newly Authored',
    items: [
      card('new_01', 'Tideglass Republic', 'Open negotiation sandbox', 2),
      card('new_02', 'Basilica Station', 'Council-driven campaign', 4),
      card('new_03', 'Crownfire Delegate', 'Legacy choice memory', 1),
      card('new_04', 'Ghostwire Embassy', 'High-risk mediation', 5),
      card('new_05', 'The Quorum Trial', 'Procedural narrative', 0),
      card('new_06', 'Riftline Charter', 'Escalation simulator', 3)
    ]
  },
  {
    id: 'row_labs',
    title: 'Experimental Story Labs',
    items: [
      card('lab_01', 'Zero-Sum Garden', 'Asymmetric option trees', 5),
      card('lab_02', 'Palace of Tones', 'Mood-reactive encounters', 3),
      card('lab_03', 'Granite Rain', 'Conditional event kernels', 1),
      card('lab_04', 'Archive of Ash', 'High token-efficiency mode', 2),
      card('lab_05', 'Hand of the Meridian', 'Multi-agent tension', 0),
      card('lab_06', 'Brass Meridian', 'Stateful long arcs', 4)
    ]
  }
]
