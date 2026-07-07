"use client";

import { Box } from "@mui/material";
import { MainContent } from "@/components/layout/MainContent";
import { SidePanel } from "@/components/layout/SidePanel";

interface MainLayoutProps {
  children: React.ReactNode;
}

export function MainLayout({ children }: MainLayoutProps) {
  return (
    <Box sx={{ display: "flex" }}>
      <SidePanel />
      <MainContent>
        <Box sx={{ mt: 8, p: 3 }}>{children}</Box>
      </MainContent>
    </Box>
  );
}
