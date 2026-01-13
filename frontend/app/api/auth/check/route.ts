import { NextResponse } from 'next/server'
import { cookies } from 'next/headers'

export async function GET() {
  try {
    // Get cookies from the request
    const cookieStore = await cookies()
    const cookieHeader = cookieStore.toString()

    // Check authentication by trying to access a protected endpoint
    const response = await fetch('http://localhost:8000/api/parameters', {
      method: 'GET',
      headers: {
        Cookie: cookieHeader,
      },
      credentials: 'include',
    })

    if (response.ok) {
      // User is authenticated - get user info from session
      // We'll need to parse the main page or create a dedicated endpoint
      const mainPageResponse = await fetch('http://localhost:8000/', {
        method: 'GET',
        headers: {
          Cookie: cookieHeader,
        },
        redirect: 'manual',
      })

      if (mainPageResponse.ok) {
        const html = await mainPageResponse.text()
        const usernameMatch = html.match(/Logged in as: <strong>(\w+)<\/strong>/)
        const roleMatch = html.match(/\((\w+)\)/)
        const subteamMatch = html.match(/user-subteam" content="([^"]*)"/)

        if (usernameMatch && roleMatch) {
          return NextResponse.json({
            username: usernameMatch[1],
            role: roleMatch[1],
            subteam: subteamMatch && subteamMatch[1] ? subteamMatch[1] : null,
          })
        }
      }
    }

    return NextResponse.json({ error: 'Not authenticated' }, { status: 401 })
  } catch (error) {
    return NextResponse.json({ error: 'Authentication check failed' }, { status: 401 })
  }
}
