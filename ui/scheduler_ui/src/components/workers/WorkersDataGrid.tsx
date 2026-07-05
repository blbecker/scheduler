"use client";

import { useState, useMemo, useCallback } from "react";
import {
  Box,
  TextField,
  InputAdornment,
  IconButton,
  CircularProgress,
  Alert,
  Button,
  Typography,
} from "@mui/material";
import {
  DataGrid,
  GridColDef,
  GridToolbarContainer,
  GridToolbarColumnsButton,
  GridToolbarFilterButton,
  GridToolbarDensitySelector,
  GridActionsCellItem,
  GridRowId,
} from "@mui/x-data-grid";
import {
  Search as SearchIcon,
  Clear as ClearIcon,
  Visibility as VisibilityIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
} from "@mui/icons-material";
import { format } from "date-fns";
import { useRouter } from "next/navigation";
import { useListWorkers, useDeleteWorker } from "@/api/client/workers/workers";
import type { WorkerResponse } from "@/api/models";
import { ConfirmationDialog } from "@/components/common/ConfirmationDialog";
import { ExportButton } from "@/components/common/ExportButton";
import { useQueryClient } from "@tanstack/react-query";

interface WorkersDataGridProps {
  onCreate?: () => void;
}

export function WorkersDataGrid({ onCreate }: WorkersDataGridProps) {
  const router = useRouter();
  const queryClient = useQueryClient();
  
  // State
  const [searchTerm, setSearchTerm] = useState("");
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [workerToDelete, setWorkerToDelete] = useState<WorkerResponse | null>(null);
  const [selectedRows, setSelectedRows] = useState<GridRowId[]>([]);

  // API hooks
  const { data, isLoading, error } = useListWorkers();
  const deleteMutation = useDeleteWorker();

  // Data preparation
  const workers = useMemo(() => data?.data || [], [data]);
  
  // Filter workers based on search term
  const filteredWorkers = useMemo(() => {
    if (!searchTerm.trim()) return workers;
    
    const term = searchTerm.toLowerCase();
    return workers.filter((worker) =>
      worker.name.toLowerCase().includes(term) ||
      worker.id.toLowerCase().includes(term)
    );
  }, [workers, searchTerm]);

  // Handle delete
  const handleDeleteClick = useCallback((worker: WorkerResponse) => {
    setWorkerToDelete(worker);
    setDeleteDialogOpen(true);
  }, []);

  const handleDeleteConfirm = useCallback(async () => {
    if (!workerToDelete) return;
    
    try {
      await deleteMutation.mutateAsync({ workerId: workerToDelete.id });
      queryClient.invalidateQueries({ queryKey: ["/api/v1/workers/"] });
      setDeleteDialogOpen(false);
      setWorkerToDelete(null);
    } catch (error) {
      console.error("Failed to delete worker:", error);
    }
  }, [workerToDelete, deleteMutation, queryClient]);

  const handleDeleteCancel = useCallback(() => {
    setDeleteDialogOpen(false);
    setWorkerToDelete(null);
  }, []);

  // Handle view/edit
  const handleView = useCallback((workerId: string) => {
    router.push(`/workers/${workerId}`);
  }, [router]);

  const handleEdit = useCallback((workerId: string) => {
    router.push(`/workers/${workerId}`);
  }, [router]);

  // Format date for display
  const formatDate = (dateString: string) => {
    try {
      return format(new Date(dateString), "MMM dd, yyyy HH:mm");
    } catch {
      return dateString;
    }
  };

  // Define columns
  const columns: GridColDef<WorkerResponse>[] = [
    {
      field: "id",
      headerName: "ID",
      width: 200,
      hideable: false,
    },
    {
      field: "name",
      headerName: "Name",
      width: 200,
      editable: false,
    },
    {
      field: "created_at",
      headerName: "Created",
      width: 180,
      valueFormatter: (value) => formatDate(value),
    },
    {
      field: "updated_at",
      headerName: "Updated",
      width: 180,
      valueFormatter: (value) => formatDate(value),
    },
    {
      field: "actions",
      headerName: "Actions",
      type: "actions",
      width: 150,
      getActions: (params) => [
        <GridActionsCellItem
          key="view"
          icon={<VisibilityIcon />}
          label="View"
          onClick={() => handleView(params.row.id)}
          showInMenu
        />,
        <GridActionsCellItem
          key="edit"
          icon={<EditIcon />}
          label="Edit"
          onClick={() => handleEdit(params.row.id)}
          showInMenu
        />,
        <GridActionsCellItem
          key="delete"
          icon={<DeleteIcon />}
          label="Delete"
          onClick={() => handleDeleteClick(params.row)}
          showInMenu
        />,
      ],
    },
  ];

  // Custom toolbar with search and actions
  const CustomToolbar = () => (
    <GridToolbarContainer sx={{ p: 2, gap: 2 }}>
      <Box sx={{ display: "flex", alignItems: "center", gap: 2, flexGrow: 1 }}>
        <TextField
          size="small"
          placeholder="Search workers..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
            endAdornment: searchTerm && (
              <InputAdornment position="end">
                <IconButton size="small" onClick={() => setSearchTerm("")}>
                  <ClearIcon />
                </IconButton>
              </InputAdornment>
            ),
          }}
          sx={{ width: 300 }}
        />
        
        <Box sx={{ display: "flex", gap: 1, ml: "auto" }}>
          <ExportButton<WorkerResponse>
            data={filteredWorkers}
            filename="workers"
            getHeaders={() => ["ID", "Name", "Created At", "Updated At"]}
            getRowData={(worker) => [
              worker.id,
              worker.name,
              worker.created_at,
              worker.updated_at,
            ]}
            disabled={filteredWorkers.length === 0}
          />
          
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={onCreate}
          >
            Add Worker
          </Button>
        </Box>
      </Box>
      
      <Box sx={{ display: "flex", gap: 1 }}>
        <GridToolbarColumnsButton />
        <GridToolbarFilterButton />
        <GridToolbarDensitySelector />
      </Box>
    </GridToolbarContainer>
  );

  // Loading state
  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height={400}>
        <CircularProgress />
      </Box>
    );
  }

  // Error state
  if (error) {
    return (
      <Alert severity="error" sx={{ m: 2 }}>
        Error loading workers: {(error as Error).message}
      </Alert>
    );
  }

  // Empty state
  if (workers.length === 0) {
    return (
      <Box textAlign="center" p={4}>
        <Typography variant="h6" gutterBottom>
          No workers found
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          Get started by adding your first worker.
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={onCreate}
        >
          Add First Worker
        </Button>
      </Box>
    );
  }

  return (
    <>
      <Box sx={{ height: 600, width: "100%" }}>
        <DataGrid
          rows={filteredWorkers}
          columns={columns}
          loading={isLoading}
          checkboxSelection
          disableRowSelectionOnClick
          onRowSelectionModelChange={(selection) => setSelectedRows(selection)}
          rowSelectionModel={selectedRows}
          slots={{
            toolbar: CustomToolbar,
          }}
          initialState={{
            pagination: {
              paginationModel: { pageSize: 25, page: 0 },
            },
            sorting: {
              sortModel: [{ field: "name", sort: "asc" }],
            },
          }}
          pageSizeOptions={[10, 25, 50, 100]}
          sx={{
            "& .MuiDataGrid-cell:focus": {
              outline: "none",
            },
            "& .MuiDataGrid-columnHeader:focus": {
              outline: "none",
            },
          }}
        />
      </Box>

      <ConfirmationDialog
        open={deleteDialogOpen}
        title="Delete Worker"
        message={`Are you sure you want to delete worker "${workerToDelete?.name}"? This action cannot be undone.`}
        confirmText="Delete"
        cancelText="Cancel"
        onConfirm={handleDeleteConfirm}
        onCancel={handleDeleteCancel}
        severity="error"
      />
    </>
  );
}