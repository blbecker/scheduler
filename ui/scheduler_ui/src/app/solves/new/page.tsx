"use client";

import { ArrowBack as ArrowBackIcon } from "@mui/icons-material";
import { Box, Button, Typography } from "@mui/material";
import { useRouter } from "next/navigation";
import { CreateScheduleSolveForm } from "@/components/schedule-solves/CreateScheduleSolveForm";

export default function CreateScheduleSolvePage() {
  const router = useRouter();

  const handleSuccess = () => {
    // The form handles navigation to the solve detail page
  };

  const handleCancel = () => {
    router.push("/solves");
  };

  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={() => router.push("/solves")}
          sx={{ mb: 2 }}
        >
          Back to Schedule Solves
        </Button>

        <Typography variant="h4">Create New Schedule Solve</Typography>
        <Typography variant="body2" color="text.secondary">
          Configure genetic algorithm parameters to optimize worker-shift assignments
        </Typography>
      </Box>

      <CreateScheduleSolveForm onSuccess={handleSuccess} onCancel={handleCancel} />
    </Box>
  );
}
