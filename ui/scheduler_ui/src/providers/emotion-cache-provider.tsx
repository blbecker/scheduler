"use client";

import { CacheProvider } from "@emotion/react";
import type * as React from "react";
import createEmotionCache from "@/lib/emotion-cache";

const clientCache = createEmotionCache();

export default function EmotionCacheProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  return <CacheProvider value={clientCache}>{children}</CacheProvider>;
}
