"use client";

import { useMemo, useState, useCallback, useEffect } from "react";
import { useRouter } from "next/navigation";
import {
  Box,
  Button,
  Typography,
  TextField,
  Alert,
  CircularProgress,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  IconButton,
} from "@mui/material";
import { Add as AddIcon, Refresh as RefreshIcon } from "@mui/icons-material";
import { useListScheduleSolves } from "@/api/client/schedule-solves/schedule-solves";
import { useQueryClient } from "@tanstack/react-query";
import { ScheduleSolvesTable } from "@/components/schedule-solves/ScheduleSolvesTable";
import { ScheduleSolveResponse } from "@/api/models";
import { SchedulerApiDbModelsEnumsScheduleSolveStatus } from "@/api/models/schedulerApiDbModelsEnumsScheduleSolveStatus";

export default function ScheduleSolvesPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());

  // API hook with polling for active solves
  const { data, isLoading, error, refetch } = useListScheduleSolves({
    query: {
      refetchInterval: 5000, // Poll every 5 seconds for real-time updates
    },
  });

  // Extract solves from response
  const solves = useMemo(() => {
    if (!data) return [];
    // Handle both array response and { data: array } response
    return Array.isArray(data) ? data : data.data || [];
  }, [data]);

  // Filter solves based on search term and status
  const filteredSolves = useMemo(() => {
    let filtered = solves;

    // Apply status filter
    if (statusFilter !== "all") {
      filtered = filtered.filter((solve) => solve.status === statusFilter);
    }

    // Apply search filter
    if (searchTerm.trim()) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(
        (solve) =>
          solve.id.toLowerCase().includes(term) ||
          solve.schedule_template_id.toLowerCase().includes(term)
      );
    }

    return filtered;
  }, [solves, statusFilter, searchTerm]);

  // Count solves by status
  const statusCounts = useMemo(() => {
    const counts: Record<string, number> = {
      all: solves.length,
    };

    solves.forEach((solve) => {
      counts[solve.status] = (counts[solve.status] || 0) + 1;
    });

    return counts;
  }, [solves]);

  // Handle view details
  const handleView = useCallback(
    (solveId: string) => {
      router.push(`/solves/${solveId}`);
    },
    [router],
  );

  // Handle view results (for completed solves)
  const handleViewResults = useCallback(
    (solveId: string) => {
      router.push(`/solves/${solveId}#results`);
    },
    [router],
  );

  const handleCreate = () => {
    router.push("/solves/new");
  };

  // Handle manual refresh
  const handleRefresh = useCallback(() => {
    refetch();
    setLastRefresh(new Date());
  }, [refetch]);

  // Format time since last refresh
  const formatTimeSince = (date: Date) => {
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffSec = Math.floor(diffMs / 1000);

    if (diffSec < 60) return `${diffSec}s ago`;
    const diffMin = Math.floor(diffSec / 60);
    return `${diffMin}m ago`;
  };

  // Error state - check both React Query error and Orval HTTP error pattern
  const hasError = error || (data && data.status && data.status !== 200);
  if (hasError) {
    return <Alert severity="error">Error loading schedule solves.</Alert>;
  }

  // Loading state
  if (isLoading && !data) {
    return (
      <Box sx={{ display: "flex", justifyContent: "center", p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  // Empty state
  if (solves.length === 0) {
    return (
      <Box>
        <Box
          sx={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            mb: 3,
          }}
        >
          <Typography variant="h4">Schedule Solves</Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleCreate}
          >
            New Solve
          </Button>
        </Box>
        <Box sx={{ textAlign: "center", p: 4 }}>
          <Typography variant="h6" gutterBottom>
            No schedule solves found
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Get started by creating your first schedule solve.
          </Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleCreate}
          >
            Create First Solve
          </Button>
        </Box>
      </Box>
    );
  }

  return (
    <Box>
      <Box
        sx={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          mb: 3,
        }}
      >
        <Box>
          <Typography variant="h4">Schedule Solves</Typography>
          <Typography variant="body2" color="text.secondary">
            Real-time monitoring of genetic algorithm optimizations
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleCreate}
        >
          New Solve
        </Button>
      </Box>

      {/* Status Filter Chips */}
      <Box sx={{ mb: 2, display: "flex", gap: 1, flexWrap: "wrap" }}>
        <Chip
          label={`All (${statusCounts.all})`}
          onClick={() => setStatusFilter("all")}
          color={statusFilter === "all" ? "primary" : "default"}
          variant={statusFilter === "all" ? "filled" : "outlined"}
          size="small"
        />
        {Object.entries(SchedulerApiDbModelsEnumsScheduleSolveStatus).map(([key, value]) => (
          <Chip
            key={key}
            label={`${value} (${statusCounts[value] || 0})`}
            onClick={() => setStatusFilter(value)}
            color={statusFilter === value ? "primary" : "default"}
            variant={statusFilter === value ? "filled" : "outlined"}
            size="small"
          />
        ))}
      </Box>

      {/* Search and Controls */}
      <Box sx={{ mb: 2, display: "flex", gap: 1, alignItems: "center" }}>
        <TextField
          size="small"
          placeholder="Search by ID or template..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          sx={{ width: 300 }}
        />

        <FormControl size="small" sx={{ minWidth: 120 }}>
          <InputLabel id="status-filter-label">Status</InputLabel>
          <Select
            labelId="status-filter-label"
            value={statusFilter}
            label="Status"
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <MenuItem value="all">All Statuses</MenuItem>
            {Object.values(SchedulerApiDbModelsEnumsScheduleSolveStatus).map((status) => (
              <MenuItem key={status} value={status}>
                {status.charAt(0).toUpperCase() + status.slice(1)}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        <Box sx={{ ml: "auto", display: "flex", alignItems: "center", gap: 1 }}>
          <Typography variant="body2" color="text.secondary">
            Last updated: {formatTimeSince(lastRefresh)}
          </Typography>
          <IconButton
            size="small"
            onClick={handleRefresh}
            title="Refresh now"
            disabled={isLoading}
          >
            <RefreshIcon fontSize="small" />
          </IconButton>
        </Box>
      </Box>

      {/* Active solves indicator */}
      {solves.some(s => ["pending", "queued", "running"].includes(s.status)) && (
        <Alert severity="info" sx={{ mb: 2 }}>
          Active solves are being monitored in real-time (updates every 5 seconds).
        </Alert>
      )}

      <ScheduleSolvesTable
        solves={filteredSolves}
        onView={handleView}
        onViewResults={handleViewResults}
      />
    </Box>
  );
}
