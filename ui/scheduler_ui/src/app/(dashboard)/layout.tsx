"use client";

import { Box } from "@mui/material";
import { SidePanel } from "@/components/layout/SidePanel";
import { MainContent } from "@/components/layout/MainContent";

interface DashboardLayoutProps {
  children: React.ReactNode;
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  return (
    <Box sx={{ display: "flex" }}>
      <SidePanel />
      <MainContent>
        <Box sx={{ mt: 8 }}>{children}</Box>
      </MainContent>
    </Box>
  );
}