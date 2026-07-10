"use client";

import { Box, Button, Typography } from "@mui/material";
import { ArrowBack as ArrowBackIcon } from "@mui/icons-material";
import { useRouter } from "next/navigation";
import { CreateScheduleCardForm } from "@/components/schedules";

export default function NewSchedulePage() {
  const router = useRouter();

  const handleSuccess = () => {
    router.push("/schedules");
  };

  return (
    <Box>
      <Box sx={{ display: "flex", alignItems: "center", gap: 2, mb: 3 }}>
        <Button startIcon={<ArrowBackIcon />} onClick={() => router.push("/schedules")}>
          Back
        </Button>
        <Typography variant="h4">Create New Schedule</Typography>
      </Box>

      <CreateScheduleCardForm onSuccess={handleSuccess} />
    </Box>
  );
}
