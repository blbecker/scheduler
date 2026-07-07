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
import { ScheduleTemplateResponse } from "@/api/models";

interface ScheduleTemplatesTableProps {
  scheduleTemplates: ScheduleTemplateResponse[];
  onView: (scheduleTemplateId: string) => void;
  onDelete: (scheduleTemplate: ScheduleTemplateResponse) => void;
}

export function ScheduleTemplatesTable({
  scheduleTemplates,
  onView,
  onDelete,
}: ScheduleTemplatesTableProps) {
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
          {scheduleTemplates.length === 0 ? (
            <TableRow>
              <TableCell colSpan={5} align="center">
                No schedule templates match your search
              </TableCell>
            </TableRow>
          ) : (
            scheduleTemplates.map((scheduleTemplate) => (
              <TableRow key={scheduleTemplate.id}>
                <TableCell>{scheduleTemplate.id}</TableCell>
                <TableCell>{scheduleTemplate.name}</TableCell>
                <TableCell>{formatDate(scheduleTemplate.created_at)}</TableCell>
                <TableCell>{formatDate(scheduleTemplate.updated_at)}</TableCell>
                <TableCell>
                  <IconButton
                    size="small"
                    onClick={() => onView(scheduleTemplate.id)}
                    title="View"
                  >
                    <VisibilityIcon fontSize="small" />
                  </IconButton>
                  <IconButton
                    size="small"
                    onClick={() => onDelete(scheduleTemplate)}
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