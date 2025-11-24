import { sql } from '@vercel/postgres';
import { NextResponse } from 'next/server';

export const runtime = 'edge';

// GET /api/stats - Get platform statistics
export async function GET() {
  try {
    // Get total counts
    const statsResult = await sql`
      SELECT 
        COUNT(*) as total_storyworlds,
        SUM(views) as total_views,
        SUM(likes) as total_likes,
        SUM(fork_count) as total_forks
      FROM storyworlds
      WHERE is_public = true
    `;

    // Get trending (most liked in last 7 days)
    const trendingResult = await sql`
      SELECT 
        id,
        title,
        description,
        num_characters,
        num_themes,
        num_variables,
        encounter_length,
        views,
        likes,
        fork_count,
        created_at
      FROM storyworlds
      WHERE is_public = true
        AND created_at > NOW() - INTERVAL '7 days'
      ORDER BY likes DESC, views DESC
      LIMIT 10
    `;

    // Get recently created
    const recentResult = await sql`
      SELECT 
        id,
        title,
        description,
        num_characters,
        num_themes,
        num_variables,
        encounter_length,
        views,
        likes,
        fork_count,
        created_at
      FROM storyworlds
      WHERE is_public = true
      ORDER BY created_at DESC
      LIMIT 10
    `;

    // Get most viewed
    const popularResult = await sql`
      SELECT 
        id,
        title,
        description,
        num_characters,
        num_themes,
        num_variables,
        encounter_length,
        views,
        likes,
        fork_count,
        created_at
      FROM storyworlds
      WHERE is_public = true
      ORDER BY views DESC
      LIMIT 10
    `;

    return NextResponse.json({
      stats: statsResult.rows[0],
      trending: trendingResult.rows,
      recent: recentResult.rows,
      popular: popularResult.rows
    });
  } catch (error) {
    console.error('Error fetching stats:', error);
    return NextResponse.json(
      { error: 'Failed to fetch stats', details: error.message },
      { status: 500 }
    );
  }
}
