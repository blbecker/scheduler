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
import { ShiftTemplateResponse } from "@/api/models";

interface ShiftTemplatesTableProps {
  shiftTemplates: ShiftTemplateResponse[];
  onView: (shiftTemplateId: string) => void;
  onDelete: (shiftTemplate: ShiftTemplateResponse) => void;
}

export function ShiftTemplatesTable({
  shiftTemplates,
  onView,
  onDelete,
}: ShiftTemplatesTableProps) {
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
            <TableCell>Schedule Template ID</TableCell>
            <TableCell>Name</TableCell>
            <TableCell>Start Time</TableCell>
            <TableCell>End Time</TableCell>
            <TableCell>Created At</TableCell>
            <TableCell>Updated At</TableCell>
            <TableCell>Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {shiftTemplates.length === 0 ? (
            <TableRow>
              <TableCell colSpan={8} align="center">
                No shift templates match your search
              </TableCell>
            </TableRow>
          ) : (
            shiftTemplates.map((shiftTemplate) => (
              <TableRow key={shiftTemplate.id}>
                <TableCell>{shiftTemplate.id}</TableCell>
                <TableCell>{shiftTemplate.schedule_template_id}</TableCell>
                <TableCell>{shiftTemplate.name}</TableCell>
                <TableCell>{formatTime(shiftTemplate.start_time)}</TableCell>
                <TableCell>{formatTime(shiftTemplate.end_time)}</TableCell>
                <TableCell>{formatDate(shiftTemplate.created_at)}</TableCell>
                <TableCell>{formatDate(shiftTemplate.updated_at)}</TableCell>
                <TableCell>
                  <IconButton
                    size="small"
                    onClick={() => onView(shiftTemplate.id)}
                    title="View"
                  >
                    <VisibilityIcon fontSize="small" />
                  </IconButton>
                  <IconButton
                    size="small"
                    onClick={() => onDelete(shiftTemplate)}
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
