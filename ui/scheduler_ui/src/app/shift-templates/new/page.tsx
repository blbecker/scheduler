"use client";

import { ArrowBack as ArrowBackIcon } from "@mui/icons-material";
import { Box, Button, Typography } from "@mui/material";
import { useRouter } from "next/navigation";
import { CreateShiftTemplateCardForm } from "@/components/shift-templates/CreateShiftTemplateCardForm";

export default function CreateShiftTemplatePage() {
  const router = useRouter();

  const handleSuccess = () => {
    router.push("/shift-templates");
  };

  const handleCancel = () => {
    router.back();
  };

  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={() => router.push("/shift-templates")}
          sx={{ mb: 2 }}
        >
          Back to Shift Templates
        </Button>

        <Typography variant="h4">Add New Shift Template</Typography>
        <Typography variant="body2" color="text.secondary">
          Create a new shift template by providing the required information
        </Typography>
      </Box>

      <CreateShiftTemplateCardForm onSuccess={handleSuccess} onCancel={handleCancel} />
    </Box>
  );
}