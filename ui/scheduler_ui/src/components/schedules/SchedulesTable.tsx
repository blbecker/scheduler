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
import { ScheduleResponse } from "@/api/models";

interface SchedulesTableProps {
  schedules: ScheduleResponse[];
  onView: (scheduleId: string) => void;
  onDelete: (schedule: ScheduleResponse) => void;
}

export function SchedulesTable({ schedules, onView, onDelete }: SchedulesTableProps) {
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
            <TableCell>Schedule Template ID</TableCell>
            <TableCell>Name</TableCell>
            <TableCell>Created At</TableCell>
            <TableCell>Updated At</TableCell>
            <TableCell>Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {schedules.length === 0 ? (
            <TableRow>
              <TableCell colSpan={6} align="center">
                No schedules match your search
              </TableCell>
            </TableRow>
          ) : (
            schedules.map((schedule) => (
              <TableRow key={schedule.id}>
                <TableCell>{schedule.id}</TableCell>
                <TableCell>{schedule.schedule_template_id}</TableCell>
                <TableCell>{schedule.name}</TableCell>
                <TableCell>{formatDate(schedule.created_at)}</TableCell>
                <TableCell>{formatDate(schedule.updated_at)}</TableCell>
                <TableCell>
                  <IconButton
                    size="small"
                    onClick={() => onView(schedule.id)}
                    title="View"
                  >
                    <VisibilityIcon fontSize="small" />
                  </IconButton>
                  <IconButton
                    size="small"
                    onClick={() => onDelete(schedule)}
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