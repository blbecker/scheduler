"use client";

import { useEffect, useState, useRef } from "react";
import { darkTheme, lightTheme } from "@/lib/theme";

export type ThemeMode = "light" | "dark";

export function useTheme() {
  const [mode, setMode] = useState<ThemeMode>("light");
  const [mounted, setMounted] = useState(false);

  const toggleTheme = () => {
    setMode((prev) => {
      const newMode = prev === "light" ? "dark" : "light";
      localStorage.setItem("theme-mode", newMode);
      return newMode;
    });
  };

  const initializedRef = useRef(false);

  useEffect(() => {
    setMounted(true);

    // Initialize theme from localStorage or system preference
    // Only run once on mount
    if (!initializedRef.current) {
      initializedRef.current = true;

      const saved = localStorage.getItem("theme-mode") as ThemeMode | null;
      if (saved && (saved === "light" || saved === "dark")) {
        setMode(saved);
      } else {
        const prefersDark = window.matchMedia(
          "(prefers-color-scheme: dark)",
        ).matches;
        setMode(prefersDark ? "dark" : "light");
      }
    }

    // Listen for system theme changes
    const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
    const handleChange = (e: MediaQueryListEvent) => {
      if (!localStorage.getItem("theme-mode")) {
        setMode(e.matches ? "dark" : "light");
      }
    };

    mediaQuery.addEventListener("change", handleChange);
    return () => mediaQuery.removeEventListener("change", handleChange);
  }, []);

  return {
    mode,
    theme: mounted ? (mode === "light" ? lightTheme : darkTheme) : lightTheme,
    toggleTheme,
    isDark: mode === "dark",
    isLight: mode === "light",
    mounted,
  };
}
