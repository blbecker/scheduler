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
} from "@mui/material";
import {
  Delete as DeleteIcon,
  Visibility as VisibilityIcon,
} from "@mui/icons-material";
import { WorkerResponse } from "@/api/models";

interface WorkersTableProps {
  workers: WorkerResponse[];
  onView: (workerId: string) => void;
  onDelete: (worker: WorkerResponse) => void;
}

export function WorkersTable({ workers, onView, onDelete }: WorkersTableProps) {
  // Format date
  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleDateString();
    } catch {
      return dateString;
    }
  };

  return (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>ID</TableCell>
            <TableCell>Name</TableCell>
            <TableCell>Created At</TableCell>
            <TableCell>Updated At</TableCell>
            <TableCell>Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {workers.length === 0 ? (
            <TableRow>
              <TableCell colSpan={5} align="center">
                No workers match your search
              </TableCell>
            </TableRow>
          ) : (
            workers.map((worker) => (
              <TableRow key={worker.id}>
                <TableCell>{worker.id}</TableCell>
                <TableCell>{worker.name}</TableCell>
                <TableCell>{formatDate(worker.created_at)}</TableCell>
                <TableCell>{formatDate(worker.updated_at)}</TableCell>
                <TableCell>
                  <IconButton
                    size="small"
                    onClick={() => onView(worker.id)}
                    title="View"
                  >
                    <VisibilityIcon fontSize="small" />
                  </IconButton>
                  <IconButton
                    size="small"
                    onClick={() => onDelete(worker)}
                    title="Delete"
                    color="error"
                  >
                    <DeleteIcon fontSize="small" />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
    </TableContainer>
  );
}
