"use client";

import { CacheProvider } from "@emotion/react";
import { useServerInsertedHTML } from "next/navigation";
import * as React from "react";
import createEmotionCache from "@/lib/emotion-cache";

export default function EmotionRegistry({
  children,
}: {
  children: React.ReactNode;
}) {
  const [{ cache }] = React.useState(() => {
    const cache = createEmotionCache();
    cache.compat = true;
    return { cache };
  });

  useServerInsertedHTML(() => {
    const styles = cache.sheet.tags.map((tag) => tag.innerHTML).join("");

    if (!styles) return null;

    return (
      <style
        data-emotion={`${cache.key}`}
        dangerouslySetInnerHTML={{ __html: styles }}
      />
    );
  });

  return <CacheProvider value={cache}>{children}</CacheProvider>;
}
