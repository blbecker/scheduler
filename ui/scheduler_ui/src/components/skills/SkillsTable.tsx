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
import { SkillResponse } from "@/api/models";

interface SkillsTableProps {
  skills: SkillResponse[];
  onView: (skillId: string) => void;
  onDelete: (skill: SkillResponse) => void;
}

export function SkillsTable({ skills, onView, onDelete }: SkillsTableProps) {
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
            <TableCell>Description</TableCell>
            <TableCell>Created At</TableCell>
            <TableCell>Updated At</TableCell>
            <TableCell>Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {skills.length === 0 ? (
            <TableRow>
              <TableCell colSpan={6} align="center">
                No skills match your search
              </TableCell>
            </TableRow>
          ) : (
            skills.map((skill) => (
              <TableRow key={skill.id}>
                <TableCell>{skill.id}</TableCell>
                <TableCell>{skill.name}</TableCell>
                <TableCell>
                  {skill.description || (
                    <span style={{ color: "#999", fontStyle: "italic" }}>
                      No description
                    </span>
                  )}
                </TableCell>
                <TableCell>{formatDate(skill.created_at)}</TableCell>
                <TableCell>{formatDate(skill.updated_at)}</TableCell>
                <TableCell>
                  <IconButton
                    size="small"
                    onClick={() => onView(skill.id)}
                    title="View"
                  >
                    <VisibilityIcon fontSize="small" />
                  </IconButton>
                  <IconButton
                    size="small"
                    onClick={() => onDelete(skill)}
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