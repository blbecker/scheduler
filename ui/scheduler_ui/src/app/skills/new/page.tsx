"use client";

import { ArrowBack as ArrowBackIcon } from "@mui/icons-material";
import { Box, Button, Typography } from "@mui/material";
import { useRouter } from "next/navigation";
import { CreateSkillCardForm } from "@/components/skills/CreateSkillCardForm";

export default function CreateSkillPage() {
  const router = useRouter();

  const handleSuccess = () => {
    router.push("/skills");
  };

  const handleCancel = () => {
    router.back();
  };

  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={() => router.push("/skills")}
          sx={{ mb: 2 }}
        >
          Back to Skills
        </Button>

        <Typography variant="h4">Add New Skill</Typography>
        <Typography variant="body2" color="text.secondary">
          Create a new skill by providing the required information
        </Typography>
      </Box>

      <CreateSkillCardForm onSuccess={handleSuccess} onCancel={handleCancel} />
    </Box>
  );
}