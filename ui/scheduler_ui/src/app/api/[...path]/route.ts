import type { NextRequest } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL ?? "http://api:9000";

async function handler(
  req: NextRequest,
  context: { params: { path: string[] } },
) {
  const path = context.params.path.join("/");
  const url = `${BACKEND_URL}/api/${path}`;

  // Preserve query string
  const search = req.nextUrl.search;

  const targetUrl = `${url}${search}`;

  // Clone headers (strip host-related ones)
  const headers = new Headers(req.headers);
  headers.delete("host");

  const method = req.method;

  const hasBody = !["GET", "HEAD"].includes(method);

  const body = hasBody ? await req.arrayBuffer() : undefined;

  const res = await fetch(targetUrl, {
    method,
    headers,
    body,
    redirect: "manual",
  });

  return new Response(res.body, {
    status: res.status,
    statusText: res.statusText,
    headers: res.headers,
  });
}

export const GET = handler;
export const POST = handler;
export const PUT = handler;
export const PATCH = handler;
export const DELETE = handler;
export const OPTIONS = handler;
