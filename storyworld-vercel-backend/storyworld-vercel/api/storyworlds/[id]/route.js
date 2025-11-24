import { sql } from '@vercel/postgres';
import { NextResponse } from 'next/server';

export const runtime = 'edge';

// GET /api/storyworlds/[id] - Get a specific storyworld
export async function GET(request, { params }) {
  try {
    const { id } = params;

    // Fetch the storyworld
    const result = await sql`
      SELECT *
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

    // Increment view count
    await sql`
      UPDATE storyworlds
      SET views = views + 1
      WHERE id = ${id}
    `;

    return NextResponse.json({
      storyworld: result.rows[0]
    });
  } catch (error) {
    console.error('Error fetching storyworld:', error);
    return NextResponse.json(
      { error: 'Failed to fetch storyworld', details: error.message },
      { status: 500 }
    );
  }
}

// PATCH /api/storyworlds/[id] - Update a storyworld
export async function PATCH(request, { params }) {
  try {
    const { id } = params;
    const body = await request.json();
    
    const updates = [];
    const values = [];
    
    // Build dynamic update query
    if (body.title !== undefined) {
      updates.push('title = $' + (updates.length + 1));
      values.push(body.title);
    }
    if (body.description !== undefined) {
      updates.push('description = $' + (updates.length + 1));
      values.push(body.description);
    }
    if (body.is_public !== undefined) {
      updates.push('is_public = $' + (updates.length + 1));
      values.push(body.is_public);
    }
    
    if (updates.length === 0) {
      return NextResponse.json(
        { error: 'No fields to update' },
        { status: 400 }
      );
    }
    
    updates.push('updated_at = NOW()');
    
    const result = await sql.query(
      `UPDATE storyworlds 
       SET ${updates.join(', ')} 
       WHERE id = $${updates.length + 1}
       RETURNING *`,
      [...values, id]
    );

    if (result.rows.length === 0) {
      return NextResponse.json(
        { error: 'Storyworld not found' },
        { status: 404 }
      );
    }

    return NextResponse.json({
      success: true,
      storyworld: result.rows[0]
    });
  } catch (error) {
    console.error('Error updating storyworld:', error);
    return NextResponse.json(
      { error: 'Failed to update storyworld', details: error.message },
      { status: 500 }
    );
  }
}

// DELETE /api/storyworlds/[id] - Delete a storyworld
export async function DELETE(request, { params }) {
  try {
    const { id } = params;

    const result = await sql`
      DELETE FROM storyworlds
      WHERE id = ${id}
      RETURNING id
    `;

    if (result.rows.length === 0) {
      return NextResponse.json(
        { error: 'Storyworld not found' },
        { status: 404 }
      );
    }

    return NextResponse.json({
      success: true,
      message: 'Storyworld deleted'
    });
  } catch (error) {
    console.error('Error deleting storyworld:', error);
    return NextResponse.json(
      { error: 'Failed to delete storyworld', details: error.message },
      { status: 500 }
    );
  }
}
