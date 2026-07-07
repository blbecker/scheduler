"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import {
  Box,
  Button,
  Card,
  CardContent,
  CardHeader,
  Typography,
  IconButton,
} from "@mui/material";
import {
  ArrowBack as ArrowBackIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
} from "@mui/icons-material";
import { useGetShift } from "@/api/client/shifts/shifts";
import { EditShiftForm, ConfirmDeleteShift } from "@/components/shifts";
import type { ShiftResponse, HTTPValidationError } from "@/api/models";

export default function ShiftDetailPage() {
  const params = useParams();
  const router = useRouter();
  const shiftId = params.id as string;

  const { data: shift, isLoading, refetch } = useGetShift(shiftId);
  const [showEditForm, setShowEditForm] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);

  const handleEditSuccess = () => {
    setShowEditForm(false);
    refetch();
  };

  const handleDeleteSuccess = () => {
    setShowDeleteDialog(false);
    router.push("/shifts");
  };

  if (isLoading) {
    return <Typography>Loading shift...</Typography>;
  }

  if (!shift) {
    return <Typography>Shift not found</Typography>;
  }

  // Type guard to check if it's a ShiftResponse (has id property)
  const isShiftResponse = (
    data: HTTPValidationError | ShiftResponse,
  ): data is ShiftResponse => {
    return "id" in data;
  };

  if (!isShiftResponse(shift.data)) {
    return <Typography>Shift not found or error occurred</Typography>;
  }

  const shiftData = shift.data;

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
    <Box>
      <Box sx={{ display: "flex", alignItems: "center", gap: 2, mb: 3 }}>
        <Button startIcon={<ArrowBackIcon />} onClick={() => router.push("/shifts")}>
          Back
        </Button>
        <Typography variant="h4">Shift Details</Typography>
        <Box sx={{ flexGrow: 1 }} />
        <IconButton onClick={() => setShowEditForm(true)} title="Edit Shift">
          <EditIcon />
        </IconButton>
        <IconButton
          onClick={() => setShowDeleteDialog(true)}
          title="Delete Shift"
          color="error"
        >
          <DeleteIcon />
        </IconButton>
      </Box>

      <Card>
        <CardHeader title={shiftData.name} />
        <CardContent>
          <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
            <div>
              <Typography variant="subtitle2" color="text.secondary">
                ID
              </Typography>
              <Typography>{shiftData.id}</Typography>
            </div>
            <div>
              <Typography variant="subtitle2" color="text.secondary">
                Schedule ID
              </Typography>
              <Typography>{shiftData.schedule_id}</Typography>
            </div>
            <div>
              <Typography variant="subtitle2" color="text.secondary">
                Shift Template ID
              </Typography>
              <Typography>{shiftData.shift_template_id}</Typography>
            </div>
            <div>
              <Typography variant="subtitle2" color="text.secondary">
                Start Time
              </Typography>
              <Typography>{formatTime(shiftData.start_time)}</Typography>
            </div>
            <div>
              <Typography variant="subtitle2" color="text.secondary">
                End Time
              </Typography>
              <Typography>{formatTime(shiftData.end_time)}</Typography>
            </div>
            <div>
              <Typography variant="subtitle2" color="text.secondary">
                Created At
              </Typography>
              <Typography>
                {new Date(shiftData.created_at).toLocaleDateString()}
              </Typography>
            </div>
            <div>
              <Typography variant="subtitle2" color="text.secondary">
                Updated At
              </Typography>
              <Typography>
                {new Date(shiftData.updated_at).toLocaleDateString()}
              </Typography>
            </div>
          </Box>
        </CardContent>
      </Card>

      {showEditForm && (
        <EditShiftForm
          shift={shiftData}
          open={showEditForm}
          onClose={() => setShowEditForm(false)}
          onSuccess={handleEditSuccess}
        />
      )}

      <ConfirmDeleteShift
        shift={shiftData}
        open={showDeleteDialog}
        onClose={() => setShowDeleteDialog(false)}
        onSuccess={handleDeleteSuccess}
      />
    </Box>
  );
}