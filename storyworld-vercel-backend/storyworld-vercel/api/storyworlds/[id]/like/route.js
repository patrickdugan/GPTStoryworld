import { sql } from '@vercel/postgres';
import { NextResponse } from 'next/server';

export const runtime = 'edge';

// POST /api/storyworlds/[id]/like - Toggle like on a storyworld
export async function POST(request, { params }) {
  try {
    const { id } = params;
    const { searchParams } = new URL(request.url);
    const action = searchParams.get('action'); // 'like' or 'unlike'

    if (action === 'like') {
      // Increment likes
      await sql`
        UPDATE storyworlds
        SET likes = likes + 1
        WHERE id = ${id}
      `;
    } else if (action === 'unlike') {
      // Decrement likes (but don't go below 0)
      await sql`
        UPDATE storyworlds
        SET likes = GREATEST(likes - 1, 0)
        WHERE id = ${id}
      `;
    } else {
      return NextResponse.json(
        { error: 'Invalid action. Use ?action=like or ?action=unlike' },
        { status: 400 }
      );
    }

    // Get updated storyworld
    const result = await sql`
      SELECT id, likes
      FROM storyworlds
      WHERE id = ${id}
      LIMIT 1
    `;

    if (result.rows.length === 0) {
      return NextResponse.json(
        { error: 'Storyworld not found' },
        { status: 404 }
      );
    }

    return NextResponse.json({
      success: true,
      id: result.rows[0].id,
      likes: result.rows[0].likes
    });
  } catch (error) {
    console.error('Error toggling like:', error);
    return NextResponse.json(
      { error: 'Failed to toggle like', details: error.message },
      { status: 500 }
    );
  }
}
