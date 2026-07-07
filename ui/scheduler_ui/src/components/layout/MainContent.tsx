"use client";

import { Box, Button } from "@mui/material";
import type { ReactNode } from "react";
import { useState } from "react";

interface MainContentProps {
  children: ReactNode;
}

export function MainContent({ children }: MainContentProps) {
  const [skipLinkVisible, setSkipLinkVisible] = useState(false);

  const handleSkipLinkClick = () => {
    const mainContent = document.getElementById("main-content");
    if (mainContent) {
      mainContent.focus();
      mainContent.scrollIntoView({ behavior: "smooth" });
    }
  };

  return (
    <>
      {/* Skip to main content link - visible on focus for keyboard users */}
      <Button
        variant="contained"
        size="small"
        onClick={handleSkipLinkClick}
        onFocus={() => setSkipLinkVisible(true)}
        onBlur={() => setSkipLinkVisible(false)}
        sx={{
          position: "absolute",
          top: 8,
          left: 8,
          zIndex: 9999,
          opacity: skipLinkVisible ? 1 : 0,
          transform: skipLinkVisible ? "translateY(0)" : "translateY(-100%)",
          transition: "opacity 0.2s, transform 0.2s",
          "&:focus": {
            opacity: 1,
            transform: "translateY(0)",
          },
        }}
        aria-label="Skip to main content"
      >
        Skip to main content
      </Button>

      <Box
        component="main"
        id="main-content"
        tabIndex={-1}
        sx={{
          flexGrow: 1,
          p: 3,
          width: "100%",
          minHeight: "100vh",
          backgroundColor: "background.default",
          outline: "none",
        }}
      >
        {children}
      </Box>
    </>
  );
}
