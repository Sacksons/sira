// Vercel Edge Function: catch-all proxy for /api/* requests to Render backend.
// This ensures API calls work even if Vercel rewrites fail or JS base URL is wrong.
export const config = { runtime: 'edge' };

const BACKEND = 'https://sira-7oeu.onrender.com';

export default async function handler(request) {
  const url = new URL(request.url);
  const target = BACKEND + url.pathname + url.search;

  // Forward all headers except host
  const headers = new Headers();
  for (const [key, value] of request.headers.entries()) {
    if (key.toLowerCase() !== 'host') {
      headers.set(key, value);
    }
  }

  const init = {
    method: request.method,
    headers,
  };

  // Forward request body for non-GET methods
  if (request.method !== 'GET' && request.method !== 'HEAD') {
    init.body = await request.text();
  }

  try {
    const resp = await fetch(target, init);

    // Build response with CORS headers
    const respHeaders = new Headers(resp.headers);
    respHeaders.set('Access-Control-Allow-Origin', '*');
    respHeaders.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS, PATCH');
    respHeaders.set('Access-Control-Allow-Headers', 'Content-Type, Authorization, Accept');
    respHeaders.delete('transfer-encoding');

    return new Response(resp.body, {
      status: resp.status,
      statusText: resp.statusText,
      headers: respHeaders,
    });
  } catch (err) {
    return new Response(JSON.stringify({ detail: 'Backend unreachable', error: err.message }), {
      status: 502,
      headers: { 'Content-Type': 'application/json' },
    });
  }
}
