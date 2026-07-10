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
import { ShiftResponse } from "@/api/models";

interface ShiftsTableProps {
  shifts: ShiftResponse[];
  onView: (shiftId: string) => void;
  onDelete: (shift: ShiftResponse) => void;
}

export function ShiftsTable({ shifts, onView, onDelete }: ShiftsTableProps) {
  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleDateString();
    } catch {
      return dateString;
    }
  };

  const formatTime = (timeString: string) => {
    try {
      return new Date(`2000-01-01T${timeString}`).toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch {
      return timeString;
    }
  };

  return (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>ID</TableCell>
            <TableCell>Schedule ID</TableCell>
            <TableCell>Shift Template ID</TableCell>
            <TableCell>Name</TableCell>
            <TableCell>Start Time</TableCell>
            <TableCell>End Time</TableCell>
            <TableCell>Created At</TableCell>
            <TableCell>Updated At</TableCell>
            <TableCell>Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {shifts.length === 0 ? (
            <TableRow>
              <TableCell colSpan={9} align="center">
                No shifts match your search
              </TableCell>
            </TableRow>
          ) : (
            shifts.map((shift) => (
              <TableRow key={shift.id}>
                <TableCell>{shift.id}</TableCell>
                <TableCell>{shift.schedule_id}</TableCell>
                <TableCell>{shift.shift_template_id}</TableCell>
                <TableCell>{shift.name}</TableCell>
                <TableCell>{formatTime(shift.start_time)}</TableCell>
                <TableCell>{formatTime(shift.end_time)}</TableCell>
                <TableCell>{formatDate(shift.created_at)}</TableCell>
                <TableCell>{formatDate(shift.updated_at)}</TableCell>
                <TableCell>
                  <IconButton
                    size="small"
                    onClick={() => onView(shift.id)}
                    title="View"
                  >
                    <VisibilityIcon fontSize="small" />
                  </IconButton>
                  <IconButton
                    size="small"
                    onClick={() => onDelete(shift)}
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
