"use client";

import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Button,
} from "@mui/material";
import { People as PeopleIcon, Add as AddIcon } from "@mui/icons-material";
import { useRouter } from "next/navigation";

export default function DashboardPage() {
  const router = useRouter();

  const handleNavigateToWorkers = () => {
    router.push("/workers");
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Welcome to Scheduler
      </Typography>
      
      <Typography variant="body1" color="text.secondary" paragraph>
        Manage your workforce, schedules, and optimize assignments with our
        scheduling system.
      </Typography>
      
      <Grid container spacing={3} sx={{ mt: 4 }}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box
                sx={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  mb: 2,
                }}
              >
                <Typography variant="h6">Workers</Typography>
                <PeopleIcon color="primary" />
              </Box>
              
              <Typography variant="body2" color="text.secondary" paragraph>
                Manage your workforce. Add, edit, or remove workers from the
                system.
              </Typography>
              
              <Box sx={{ display: "flex", gap: 2 }}>
                <Button
                  variant="contained"
                  startIcon={<PeopleIcon />}
                  onClick={handleNavigateToWorkers}
                >
                  View Workers
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<AddIcon />}
                  onClick={() => router.push("/workers/new")}
                >
                  Add Worker
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Quick Stats
              </Typography>
              
              <Typography variant="body2" color="text.secondary">
                More features coming soon: Skills management, schedule
                templates, and optimization tools.
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}