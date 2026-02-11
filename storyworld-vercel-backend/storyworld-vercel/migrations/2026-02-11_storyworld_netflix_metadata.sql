-- Adds Netflix-style catalog metadata to existing storyworld deployments.
ALTER TABLE storyworlds ADD COLUMN IF NOT EXISTS genre VARCHAR(64) DEFAULT 'Diplomacy';
ALTER TABLE storyworlds ADD COLUMN IF NOT EXISTS size_tag VARCHAR(16) DEFAULT 'standard';
ALTER TABLE storyworlds ADD COLUMN IF NOT EXISTS theme_variant VARCHAR(24) DEFAULT 'midnight';
ALTER TABLE storyworlds ADD COLUMN IF NOT EXISTS cover_image TEXT;
ALTER TABLE storyworlds ADD COLUMN IF NOT EXISTS banner_image TEXT;
ALTER TABLE storyworlds ADD COLUMN IF NOT EXISTS tags TEXT[] DEFAULT ARRAY[]::TEXT[];

CREATE INDEX IF NOT EXISTS idx_storyworlds_genre
  ON storyworlds(genre);

CREATE INDEX IF NOT EXISTS idx_storyworlds_size_tag
  ON storyworlds(size_tag);

CREATE INDEX IF NOT EXISTS idx_storyworlds_theme_variant
  ON storyworlds(theme_variant);

CREATE INDEX IF NOT EXISTS idx_storyworlds_tags
  ON storyworlds USING GIN (tags);
