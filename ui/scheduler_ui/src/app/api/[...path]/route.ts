import type { NextRequest } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL;

function assertBackendUrl(): string {
  if (!BACKEND_URL) {
    throw new Error("BACKEND_URL is not defined");
  }
  return BACKEND_URL;
}

async function handler(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> },
) {
  const { path } = await context.params;

  const backendUrl = assertBackendUrl();

  const url = new URL(`${backendUrl}/api/${path.join("/")}`);

  // forward query string
  url.search = request.nextUrl.search;

  const isBodyAllowed = request.method !== "GET" && request.method !== "HEAD";

  const upstreamResponse = await fetch(url, {
    method: request.method,
    headers: request.headers,
    body: isBodyAllowed ? await request.arrayBuffer() : undefined,
    duplex: isBodyAllowed ? "half" : undefined,
  });

  return upstreamResponse;
}

export const GET = handler;
export const POST = handler;
export const PUT = handler;
export const PATCH = handler;
export const DELETE = handler;
export const OPTIONS = handler;
