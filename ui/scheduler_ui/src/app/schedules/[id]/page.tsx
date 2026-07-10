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
import { useGetSchedule } from "@/api/client/schedules/schedules";
import { EditScheduleForm, ConfirmDeleteSchedule } from "@/components/schedules";
import type { ScheduleResponse, HTTPValidationError } from "@/api/models";

export default function ScheduleDetailPage() {
  const params = useParams();
  const router = useRouter();
  const scheduleId = params.id as string;

  const { data: schedule, isLoading, refetch } = useGetSchedule(scheduleId);
  const [showEditForm, setShowEditForm] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);

  const handleEditSuccess = () => {
    setShowEditForm(false);
    refetch();
  };

  const handleDeleteSuccess = () => {
    setShowDeleteDialog(false);
    router.push("/schedules");
  };

  if (isLoading) {
    return <Typography>Loading schedule...</Typography>;
  }

  if (!schedule) {
    return <Typography>Schedule not found</Typography>;
  }

  // Type guard to check if it's a ScheduleResponse (has id property)
  const isScheduleResponse = (
    data: HTTPValidationError | ScheduleResponse,
  ): data is ScheduleResponse => {
    return "id" in data;
  };

  if (!isScheduleResponse(schedule.data)) {
    return <Typography>Schedule not found or error occurred</Typography>;
  }

  const scheduleData = schedule.data;

  return (
    <Box>
      <Box sx={{ display: "flex", alignItems: "center", gap: 2, mb: 3 }}>
        <Button startIcon={<ArrowBackIcon />} onClick={() => router.push("/schedules")}>
          Back
        </Button>
        <Typography variant="h4">Schedule Details</Typography>
        <Box sx={{ flexGrow: 1 }} />
        <IconButton onClick={() => setShowEditForm(true)} title="Edit Schedule">
          <EditIcon />
        </IconButton>
        <IconButton
          onClick={() => setShowDeleteDialog(true)}
          title="Delete Schedule"
          color="error"
        >
          <DeleteIcon />
        </IconButton>
      </Box>

      <Card>
        <CardHeader title={scheduleData.name} />
        <CardContent>
          <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
            <div>
              <Typography variant="subtitle2" color="text.secondary">
                ID
              </Typography>
              <Typography>{scheduleData.id}</Typography>
            </div>
            <div>
              <Typography variant="subtitle2" color="text.secondary">
                Schedule Template ID
              </Typography>
              <Typography>{scheduleData.schedule_template_id}</Typography>
            </div>
            <div>
              <Typography variant="subtitle2" color="text.secondary">
                Created At
              </Typography>
              <Typography>
                {new Date(scheduleData.created_at).toLocaleDateString()}
              </Typography>
            </div>
            <div>
              <Typography variant="subtitle2" color="text.secondary">
                Updated At
              </Typography>
              <Typography>
                {new Date(scheduleData.updated_at).toLocaleDateString()}
              </Typography>
            </div>
          </Box>
        </CardContent>
      </Card>

      {showEditForm && (
        <EditScheduleForm
schedule={scheduleData}
          open={showEditForm}
          onClose={() => setShowEditForm(false)}
          onSuccess={handleEditSuccess}
        />
      )}

      <ConfirmDeleteSchedule
        schedule={scheduleData}
        open={showDeleteDialog}
        onClose={() => setShowDeleteDialog(false)}
        onSuccess={handleDeleteSuccess}
      />
    </Box>
  );
}
