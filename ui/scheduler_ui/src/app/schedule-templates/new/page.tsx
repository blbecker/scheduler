"use client";

import { ArrowBack as ArrowBackIcon } from "@mui/icons-material";
import { Box, Button, Typography } from "@mui/material";
import { useRouter } from "next/navigation";
import { CreateScheduleTemplateCardForm } from "@/components/schedule-templates/CreateScheduleTemplateCardForm";

export default function CreateScheduleTemplatePage() {
  const router = useRouter();

  const handleSuccess = () => {
    router.push("/schedule-templates");
  };

  const handleCancel = () => {
    router.back();
  };

  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={() => router.push("/schedule-templates")}
          sx={{ mb: 2 }}
        >
          Back to Schedule Templates
        </Button>

        <Typography variant="h4">Add New Schedule Template</Typography>
        <Typography variant="body2" color="text.secondary">
          Create a new schedule template by providing the required information
        </Typography>
      </Box>

      <CreateScheduleTemplateCardForm onSuccess={handleSuccess} onCancel={handleCancel} />
    </Box>
  );
}