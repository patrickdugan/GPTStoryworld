import { sql } from '@vercel/postgres';
import { NextResponse } from 'next/server';

export const runtime = 'edge';

// POST /api/storyworlds - Create a new storyworld
export async function POST(request) {
  try {
    const body = await request.json();
    
    const {
      title,
      description,
      num_characters,
      num_themes,
      num_variables,
      encounter_length,
      custom_prompt,
      encounter,
      system_prompt,
      is_public = true,
      model_used = 'gpt-4',
      temperature = 0.8
    } = body;

    // Validate required fields
    if (!title || !encounter || !num_characters || !num_themes || !num_variables || !encounter_length) {
      return NextResponse.json(
        { error: 'Missing required fields' },
        { status: 400 }
      );
    }

    // Insert into database
    const result = await sql`
      INSERT INTO storyworlds (
        title,
        description,
        num_characters,
        num_themes,
        num_variables,
        encounter_length,
        custom_prompt,
        encounter,
        system_prompt,
        is_public,
        model_used,
        temperature
      ) VALUES (
        ${title},
        ${description},
        ${num_characters},
        ${num_themes},
        ${num_variables},
        ${encounter_length},
        ${custom_prompt},
        ${JSON.stringify(encounter)},
        ${system_prompt},
        ${is_public},
        ${model_used},
        ${temperature}
      )
      RETURNING *
    `;

    return NextResponse.json({
      success: true,
      storyworld: result.rows[0]
    });
  } catch (error) {
    console.error('Error creating storyworld:', error);
    return NextResponse.json(
      { error: 'Failed to create storyworld', details: error.message },
      { status: 500 }
    );
  }
}

// GET /api/storyworlds - List all public storyworlds
export async function GET(request) {
  try {
    const { searchParams } = new URL(request.url);
    const limit = parseInt(searchParams.get('limit') || '20');
    const offset = parseInt(searchParams.get('offset') || '0');
    const sort = searchParams.get('sort') || 'created_at';
    const order = searchParams.get('order') || 'desc';

    // Validate sort field to prevent SQL injection
    const allowedSorts = ['created_at', 'views', 'likes', 'fork_count'];
    const sortField = allowedSorts.includes(sort) ? sort : 'created_at';
    const sortOrder = order === 'asc' ? 'ASC' : 'DESC';

    const result = await sql`
      SELECT 
        id,
        title,
        description,
        num_characters,
        num_themes,
        num_variables,
        encounter_length,
        custom_prompt,
        encounter,
        views,
        likes,
        fork_count,
        model_used,
        created_at
      FROM storyworlds
      WHERE is_public = true
      ORDER BY ${sql.raw(sortField)} ${sql.raw(sortOrder)}
      LIMIT ${limit}
      OFFSET ${offset}
    `;

    // Get total count
    const countResult = await sql`
      SELECT COUNT(*) as total
      FROM storyworlds
      WHERE is_public = true
    `;

    return NextResponse.json({
      storyworlds: result.rows,
      total: parseInt(countResult.rows[0].total),
      limit,
      offset
    });
  } catch (error) {
    console.error('Error fetching storyworlds:', error);
    return NextResponse.json(
      { error: 'Failed to fetch storyworlds', details: error.message },
      { status: 500 }
    );
  }
}
