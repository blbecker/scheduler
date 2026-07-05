"use client";

import { Box } from "@mui/material";
import { ReactNode } from "react";

interface MainContentProps {
  children: ReactNode;
}

export function MainContent({ children }: MainContentProps) {
  return (
    <Box
      component="main"
      sx={{
        flexGrow: 1,
        p: 3,
        width: "100%",
        minHeight: "100vh",
        backgroundColor: "background.default",
      }}
    >
      {children}
    </Box>
  );
}