"use client";

import {
  ArrowBack as ArrowBackIcon,
  BarChart as BarChartIcon,
  Calculate as CalculateIcon,
  Schedule as ScheduleIcon,
  Timelapse as TimelapseIcon,
  TrendingUp as TrendingUpIcon,
  Error as ErrorIcon,
} from "@mui/icons-material";
import {
  Alert,
  Box,
  Button,
  Card,
  CardActions,
  CardContent,
  Chip,
  CircularProgress,
  Divider,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Typography,
} from "@mui/material";
import { useQueryClient } from "@tanstack/react-query";
import { format } from "date-fns";
import { useRouter } from "next/navigation";
import {
  useGetScheduleSolveStatus,
  useGetScheduleSolveResult
} from "@/api/client/schedule-solves/schedule-solves";
import { SchedulerApiDbModelsEnumsScheduleSolveStatus } from "@/api/models/schedulerApiDbModelsEnumsScheduleSolveStatus";

interface ScheduleSolveDetailCardProps {
  solveId: string;
}

export function ScheduleSolveDetailCard({ solveId }: ScheduleSolveDetailCardProps) {
  const router = useRouter();
  const queryClient = useQueryClient();

  // API hooks with polling for active solves
  const { data: statusData, isLoading: statusLoading, error: statusError, refetch: refetchStatus } = useGetScheduleSolveStatus(solveId, {
    query: {
      refetchInterval: (data) => {
        const isActive = data?.status && ["pending", "queued", "running"].includes(data.status);
        return isActive ? 5000 : false;
      },
    },
  });

  const { data: resultData, isLoading: resultLoading, error: resultError } = useGetScheduleSolveResult(solveId, {
    query: {
      enabled: statusData?.status === "completed",
    },
  });

  const solve = statusData?.data;
  const result = resultData?.data;

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

  // Check if solve is active
  const isActive = (status: SchedulerApiDbModelsEnumsScheduleSolveStatus) => {
    return ["pending", "queued", "running"].includes(status);
  };

  // Format date for display
  const formatDate = (dateString: string | null) => {
    if (!dateString) return "Not started";
    try {
      return format(new Date(dateString), "PPP 'at' pp");
    } catch {
      return dateString;
    }
  };

  // Format fitness to percentage
  const formatFitness = (fitness: number | null) => {
    if (fitness === null) return "N/A";
    return `${(fitness * 100).toFixed(2)}%`;
  };

  // Format duration
  const formatDuration = (started: string | null, finished: string | null) => {
    if (!started || !finished) return "N/A";
    try {
      const start = new Date(started);
      const end = new Date(finished);
      const diffMs = end.getTime() - start.getTime();
      const diffSec = Math.round(diffMs / 1000);

      if (diffSec < 60) return `${diffSec}s`;
      const diffMin = Math.round(diffSec / 60);
      return `${diffMin}m`;
    } catch {
      return "N/A";
    }
  };

  // Loading state
  if (statusLoading) {
    return (
      <Box
        sx={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          height: 400,
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  // Error state
  if (statusError) {
    return (
      <Alert severity="error">
        Error loading schedule solve: {(statusError as Error).message}
      </Alert>
    );
  }

  // Not found state
  if (!solve) {
    return <Alert severity="warning">Schedule solve not found</Alert>;
  }

  return (
    <>
      <Card>
        <CardContent>
          <Box sx={{ display: "flex", alignItems: "center", mb: 3, gap: 2 }}>
            <CalculateIcon color="primary" sx={{ fontSize: 40 }} />
            <Box>
              <Typography variant="h5" component="div">
                Schedule Solve
              </Typography>
              <Typography variant="body2" color="text.secondary">
                ID: {solve.id}
              </Typography>
            </Box>
            <Box sx={{ ml: "auto" }}>
              <Chip
                label={solve.status}
                color={getStatusColor(solve.status)}
                size="medium"
                variant={isActive(solve.status) ? "filled" : "outlined"}
              />
            </Box>
          </Box>

          <Divider sx={{ my: 2 }} />

          {/* Progress Section for Active Solves */}
          {isActive(solve.status) && (
            <Box sx={{ mb: 4 }}>
              <Typography variant="h6" gutterBottom>
                Progress
              </Typography>
              <Box sx={{ display: "flex", alignItems: "center", gap: 2, mb: 2 }}>
                <Box sx={{ flex: 1 }}>
                  <LinearProgress
                    variant="determinate"
                    value={solve.progress ? solve.progress * 100 : 0}
                    sx={{ height: 10, borderRadius: 5 }}
                  />
                </Box>
                <Typography variant="body2">
                  {solve.progress ? Math.round(solve.progress * 100) : 0}%
                </Typography>
              </Box>
              <Box sx={{ display: "flex", gap: 4 }}>
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Current Generation
                  </Typography>
                  <Typography variant="h6">
                    {solve.current_generation || 0}
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Best Fitness
                  </Typography>
                  <Typography variant="h6">
                    {formatFitness(solve.best_fitness)}
                  </Typography>
                </Box>
              </Box>
            </Box>
          )}

          {/* Solve Details */}
          <Box sx={{ mb: 4 }}>
            <Typography variant="h6" gutterBottom>
              Solve Details
            </Typography>
            <TableContainer component={Paper} variant="outlined">
              <Table size="small">
                <TableBody>
                  <TableRow>
                    <TableCell component="th" scope="row">
                      <ScheduleIcon fontSize="small" sx={{ mr: 1 }} />
                      Template ID
                    </TableCell>
                    <TableCell>{solve.template_id}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell component="th" scope="row">
                      <TimelapseIcon fontSize="small" sx={{ mr: 1 }} />
                      Status
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={solve.status}
                        color={getStatusColor(solve.status)}
                        size="small"
                      />
                    </TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell component="th" scope="row">
                      Created
                    </TableCell>
                    <TableCell>{formatDate(solve.created_at)}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell component="th" scope="row">
                      Started
                    </TableCell>
                    <TableCell>{formatDate(solve.started_at)}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell component="th" scope="row">
                      Finished
                    </TableCell>
                    <TableCell>{formatDate(solve.finished_at)}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell component="th" scope="row">
                      Duration
                    </TableCell>
                    <TableCell>{formatDuration(solve.started_at, solve.finished_at)}</TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </TableContainer>
          </Box>

          {/* Parameters */}
          {solve.parameters && (
            <Box sx={{ mb: 4 }}>
              <Typography variant="h6" gutterBottom>
                Parameters
              </Typography>
              <TableContainer component={Paper} variant="outlined">
                <Table size="small">
                  <TableBody>
                    {Object.entries(solve.parameters).map(([key, value]) => (
                      <TableRow key={key}>
                        <TableCell component="th" scope="row">
                          {key.replace(/_/g, ' ')}
                        </TableCell>
                        <TableCell>{String(value)}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>
          )}

          {/* Results for Completed Solves */}
          {solve.status === "completed" && result && (
            <Box sx={{ mb: 4 }}>
              <Typography variant="h6" gutterBottom>
                <BarChartIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                Results
              </Typography>
              <TableContainer component={Paper} variant="outlined">
                <Table size="small">
                  <TableBody>
                    <TableRow>
                      <TableCell component="th" scope="row">
                        <TrendingUpIcon fontSize="small" sx={{ mr: 1 }} />
                        Final Fitness
                      </TableCell>
                      <TableCell>
                        <Typography variant="body1" color="success.main">
                          {formatFitness(result.best_fitness)}
                        </Typography>
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell component="th" scope="row">
                        Generations
                      </TableCell>
                      <TableCell>{result.generations}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell component="th" scope="row">
                        Elapsed Time
                      </TableCell>
                      <TableCell>{result.elapsed_time.toFixed(2)}s</TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>
          )}

          {/* Error Details for Failed Solves */}
          {solve.status === "failed" && solve.error_message && (
            <Box sx={{ mb: 4 }}>
              <Typography variant="h6" gutterBottom>
                <ErrorIcon color="error" sx={{ mr: 1, verticalAlign: 'middle' }} />
                Error Details
              </Typography>
              <Alert severity="error">
                {solve.error_message}
              </Alert>
            </Box>
          )}
        </CardContent>

        <CardActions sx={{ p: 2, justifyContent: "space-between" }}>
          <Button
            startIcon={<ArrowBackIcon />}
            onClick={() => router.push("/solves")}
          >
            Back to Solves
          </Button>

          <Box sx={{ display: "flex", gap: 2 }}>
            {isActive(solve.status) && (
              <Button
                variant="outlined"
                onClick={() => refetchStatus()}
                disabled={statusLoading}
              >
                Refresh Status
              </Button>
            )}
            {solve.status === "completed" && result && (
              <Button
                variant="contained"
                startIcon={<BarChartIcon />}
                onClick={() => {
                  // In a real implementation, this might navigate to a results visualization page
                  // or open a dialog with detailed results
                  console.log("View detailed results:", result);
                }}
              >
                View Detailed Results
              </Button>
            )}
          </Box>
        </CardActions>
      </Card>
    </>
  );
}
