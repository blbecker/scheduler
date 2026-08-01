"use client";

import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Chip,
  Box,
  LinearProgress,
} from "@mui/material";
import {
  Visibility as VisibilityIcon,
  BarChart as BarChartIcon,
} from "@mui/icons-material";
import { ScheduleSolveResponse } from "@/api/models";
import { SchedulerApiDbModelsEnumsScheduleSolveStatus } from "@/api/models/schedulerApiDbModelsEnumsScheduleSolveStatus";

interface ScheduleSolvesTableProps {
  solves: ScheduleSolveResponse[];
  onView: (solveId: string) => void;
  onViewResults: (solveId: string) => void;
}

export function ScheduleSolvesTable({ solves, onView, onViewResults }: ScheduleSolvesTableProps) {
  // Format date
  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleDateString();
    } catch {
      return dateString;
    }
  };

  // Format fitness to percentage
  const formatFitness = (fitness: number | null) => {
    if (fitness === null) return "-";
    return `${(fitness * 100).toFixed(1)}%`;
  };

  // Get status chip color
  const getStatusColor = (status: SchedulerApiDbModelsEnumsScheduleSolveStatus) => {
    switch (status) {
      case "pending": return "default";
      case "queued": return "info";
      case "running": return "warning";
      case "completed": return "success";
      case "failed": return "error";
      case "cancelled": return "default";
      default: return "default";
    }
  };

  // Check if solve is active (should show progress)
  const isActive = (status: SchedulerApiDbModelsEnumsScheduleSolveStatus) => {
    return ["pending", "queued", "running"].includes(status);
  };

  // Check if results are available
  const hasResults = (status: SchedulerApiDbModelsEnumsScheduleSolveStatus) => {
    return ["completed", "failed", "cancelled"].includes(status);
  };

  return (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>ID</TableCell>
            <TableCell>Template</TableCell>
            <TableCell>Status</TableCell>
            <TableCell>Progress</TableCell>
            <TableCell>Generation</TableCell>
            <TableCell>Best Fitness</TableCell>
            <TableCell>Created At</TableCell>
            <TableCell>Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {solves.length === 0 ? (
            <TableRow>
              <TableCell colSpan={8} align="center">
                No schedule solves found
              </TableCell>
            </TableRow>
          ) : (
            solves.map((solve) => (
              <TableRow key={solve.id}>
                <TableCell>{solve.id.substring(0, 8)}...</TableCell>
                <TableCell>{solve.schedule_template_id.substring(0, 8)}...</TableCell>
                <TableCell>
                  <Chip
                    label={solve.status}
                    color={getStatusColor(solve.status)}
                    size="small"
                    variant="outlined"
                  />
                </TableCell>
                <TableCell>
                  {isActive(solve.status) ? (
                    <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                      <Box sx={{ width: "100%" }}>
                        <LinearProgress
                          variant="determinate"
                          value={(solve.progress || 0) * 100}
                          sx={{ height: 8, borderRadius: 4 }}
                        />
                      </Box>
                      <Box sx={{ minWidth: 35 }}>
                        <span>{Math.round((solve.progress || 0) * 100)}%</span>
                      </Box>
                    </Box>
                  ) : (
                    <span>{Math.round((solve.progress || 0) * 100)}%</span>
                  )}
                </TableCell>
                <TableCell>
                  {solve.current_generation !== null ? solve.current_generation : "-"}
                </TableCell>
                <TableCell>
                  {formatFitness(solve.best_fitness)}
                </TableCell>
                <TableCell>{formatDate(solve.created_at)}</TableCell>
                <TableCell>
                  <IconButton
                    size="small"
                    onClick={() => onView(solve.id)}
                    title="View Details"
                  >
                    <VisibilityIcon fontSize="small" />
                  </IconButton>
                  {hasResults(solve.status) && (
                    <IconButton
                      size="small"
                      onClick={() => onViewResults(solve.id)}
                      title="View Results"
                      color="primary"
                    >
                      <BarChartIcon fontSize="small" />
                    </IconButton>
                  )}
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
    </TableContainer>
  );
}
