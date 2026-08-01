"use client";

import React from "react";
import { Box, Typography } from "@mui/material";
import { ScheduleSolveDetailCard } from "@/components/schedule-solves/ScheduleSolveDetailCard";

interface ScheduleSolveDetailPageProps {
  params: Promise<{
    id: string;
  }>;
}

export default function ScheduleSolveDetailPage({ params }: ScheduleSolveDetailPageProps) {
  const resolvedParams = React.use(params);
  const solveId = resolvedParams.id;

  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4">Schedule Solve Details</Typography>
        <Typography variant="body2" color="text.secondary">
          Real-time monitoring of genetic algorithm optimization progress
        </Typography>
      </Box>

      <ScheduleSolveDetailCard solveId={solveId} />
    </Box>
  );
}
