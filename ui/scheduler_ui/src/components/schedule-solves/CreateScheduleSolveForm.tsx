"use client";

import {
  Calculate as CalculateIcon,
  Save as SaveIcon,
  Cancel as CancelIcon,
  Schedule as ScheduleIcon,
} from "@mui/icons-material";
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Divider,
  FormControl,
  FormHelperText,
  InputLabel,
  MenuItem,
  Select,
  Slider,
  TextField,
  Typography,
  Grid,
} from "@mui/material";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useCreateScheduleSolve } from "@/api/client/schedule-solves/schedule-solves";
import { useListScheduleTemplates } from "@/api/client/schedule-templates/schedule-templates";
import { ScheduleSolveRequest } from "@/api/models";

interface CreateScheduleSolveFormProps {
  onSuccess?: () => void;
  onCancel?: () => void;
}

export function CreateScheduleSolveForm({ onSuccess, onCancel }: CreateScheduleSolveFormProps) {
  const router = useRouter();

  // State
  const [templateId, setTemplateId] = useState<string>("");
  const [parameters, setParameters] = useState({
    population_size: 100,
    max_generations: 1000,
    mutation_rate: 0.01,
    selection_top_n: 5,
    elite_size: 5,
  });
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});

  // API hooks
  const { data: templatesData, isLoading: templatesLoading, error: templatesError } = useListScheduleTemplates();
  const createMutation = useCreateScheduleSolve();

  // Extract templates from response
  const templates = templatesData?.data || [];

  // Handle parameter changes
  const handleParameterChange = (field: string, value: number) => {
    setParameters(prev => ({ ...prev, [field]: value }));

    // Clear error for this field
    if (formErrors[field]) {
      setFormErrors(prev => ({ ...prev, [field]: "" }));
    }
  };

  // Handle template selection
  const handleTemplateChange = (value: string) => {
    setTemplateId(value);

    // Clear error for template
    if (formErrors.template_id) {
      setFormErrors(prev => ({ ...prev, template_id: "" }));
    }
  };

  // Validate form
  const validateForm = () => {
    const errors: Record<string, string> = {};

    if (!templateId.trim()) {
      errors.template_id = "Please select a schedule template";
    }

    if (parameters.population_size < 5 || parameters.population_size > 1000) {
      errors.population_size = "Population size must be between 5 and 1000";
    }

    if (parameters.max_generations < 1 || parameters.max_generations > 10000) {
      errors.max_generations = "Max generations must be between 1 and 10000";
    }

    if (parameters.mutation_rate < 0 || parameters.mutation_rate > 1) {
      errors.mutation_rate = "Mutation rate must be between 0 and 1";
    }

    if (parameters.selection_top_n < 1 || parameters.selection_top_n > 1000) {
      errors.selection_top_n = "Selection top N must be between 1 and 1000";
    }

    if (parameters.elite_size < 0 || parameters.elite_size > 100) {
      errors.elite_size = "Elite size must be between 0 and 100";
    }

    if (parameters.elite_size > parameters.population_size) {
      errors.elite_size = "Elite size cannot be larger than population size";
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    try {
      const request: ScheduleSolveRequest = {
        template_id: templateId,
        parameters,
      };

      const response = await createMutation.mutateAsync({ data: request });

      if (response.status === 202 && response.data?.id) {
        // Redirect to the solve detail page
        router.push(`/solves/${response.data.id}`);
        onSuccess?.();
      } else {
        // Handle API error
        setFormErrors({ submit: "Failed to create schedule solve. Please try again." });
      }
    } catch (error) {
      console.error("Error creating schedule solve:", error);
      setFormErrors({ submit: "An unexpected error occurred. Please try again." });
    }
  };

  // Loading state for templates
  if (templatesLoading) {
    return (
      <Box
        sx={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          height: 400,
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  // Error state for templates
  if (templatesError) {
    return (
      <Alert severity="error">
        Error loading schedule templates: {(templatesError as Error).message}
      </Alert>
    );
  }

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: "flex", alignItems: "center", mb: 3, gap: 2 }}>
          <CalculateIcon color="primary" sx={{ fontSize: 40 }} />
          <Box>
            <Typography variant="h5" component="div">
              Create Schedule Solve
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Configure parameters for genetic algorithm optimization
            </Typography>
          </Box>
        </Box>

        <Divider sx={{ my: 2 }} />

        <form onSubmit={handleSubmit}>
          {/* Template Selection */}
          <Box sx={{ mb: 4 }}>
            <Typography variant="h6" gutterBottom>
              <ScheduleIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
              Schedule Template
            </Typography>
            <FormControl fullWidth error={!!formErrors.template_id}>
              <InputLabel id="template-select-label">Select Template</InputLabel>
              <Select
                labelId="template-select-label"
                value={templateId}
                label="Select Template"
                onChange={(e) => handleTemplateChange(e.target.value)}
              >
                {templates.length === 0 ? (
                  <MenuItem disabled value="">
                    No templates available
                  </MenuItem>
                ) : (
                  templates.map((template) => (
                    <MenuItem key={template.id} value={template.id}>
                      {template.name || template.id.substring(0, 8)}...
                    </MenuItem>
                  ))
                )}
              </Select>
              {formErrors.template_id && (
                <FormHelperText>{formErrors.template_id}</FormHelperText>
              )}
            </FormControl>
            {templates.length === 0 && (
              <Alert severity="warning" sx={{ mt: 2 }}>
                No schedule templates found. Please create a schedule template first.
              </Alert>
            )}
          </Box>

          <Divider sx={{ my: 3 }} />

          {/* Parameters Section */}
          <Typography variant="h6" gutterBottom sx={{ mb: 3 }}>
            Genetic Algorithm Parameters
          </Typography>

          <Grid container spacing={3}>
            {/* Population Size */}
            <Grid item xs={12} md={6}>
              <Box>
                <Typography gutterBottom>
                  Population Size: {parameters.population_size}
                </Typography>
                <Slider
                  value={parameters.population_size}
                  onChange={(_, value) => handleParameterChange("population_size", value as number)}
                  min={5}
                  max={1000}
                  step={5}
                  marks={[
                    { value: 5, label: "5" },
                    { value: 500, label: "500" },
                    { value: 1000, label: "1000" },
                  ]}
                  valueLabelDisplay="auto"
                />
                <Typography variant="caption" color="text.secondary">
                  Number of candidate solutions per generation
                </Typography>
                {formErrors.population_size && (
                  <Typography variant="caption" color="error">
                    {formErrors.population_size}
                  </Typography>
                )}
              </Box>
            </Grid>

            {/* Max Generations */}
            <Grid item xs={12} md={6}>
              <Box>
                <Typography gutterBottom>
                  Max Generations: {parameters.max_generations}
                </Typography>
                <Slider
                  value={parameters.max_generations}
                  onChange={(_, value) => handleParameterChange("max_generations", value as number)}
                  min={1}
                  max={10000}
                  step={100}
                  marks={[
                    { value: 1, label: "1" },
                    { value: 5000, label: "5000" },
                    { value: 10000, label: "10000" },
                  ]}
                  valueLabelDisplay="auto"
                />
                <Typography variant="caption" color="text.secondary">
                  Maximum number of generations to run
                </Typography>
                {formErrors.max_generations && (
                  <Typography variant="caption" color="error">
                    {formErrors.max_generations}
                  </Typography>
                )}
              </Box>
            </Grid>

            {/* Mutation Rate */}
            <Grid item xs={12} md={6}>
              <Box>
                <Typography gutterBottom>
                  Mutation Rate: {parameters.mutation_rate.toFixed(3)}
                </Typography>
                <Slider
                  value={parameters.mutation_rate}
                  onChange={(_, value) => handleParameterChange("mutation_rate", value as number)}
                  min={0}
                  max={0.1}
                  step={0.001}
                  marks={[
                    { value: 0, label: "0" },
                    { value: 0.05, label: "0.05" },
                    { value: 0.1, label: "0.1" },
                  ]}
                  valueLabelDisplay="auto"
                />
                <Typography variant="caption" color="text.secondary">
                  Probability of mutation per gene (0-1)
                </Typography>
                {formErrors.mutation_rate && (
                  <Typography variant="caption" color="error">
                    {formErrors.mutation_rate}
                  </Typography>
                )}
              </Box>
            </Grid>

            {/* Selection Top N */}
            <Grid item xs={12} md={6}>
              <Box>
                <Typography gutterBottom>
                  Selection Top N: {parameters.selection_top_n}
                </Typography>
                <Slider
                  value={parameters.selection_top_n}
                  onChange={(_, value) => handleParameterChange("selection_top_n", value as number)}
                  min={1}
                  max={100}
                  step={1}
                  marks={[
                    { value: 1, label: "1" },
                    { value: 50, label: "50" },
                    { value: 100, label: "100" },
                  ]}
                  valueLabelDisplay="auto"
                />
                <Typography variant="caption" color="text.secondary">
                  Number of top solutions to select for reproduction
                </Typography>
                {formErrors.selection_top_n && (
                  <Typography variant="caption" color="error">
                    {formErrors.selection_top_n}
                  </Typography>
                )}
              </Box>
            </Grid>

            {/* Elite Size */}
            <Grid item xs={12} md={6}>
              <Box>
                <Typography gutterBottom>
                  Elite Size: {parameters.elite_size}
                </Typography>
                <Slider
                  value={parameters.elite_size}
                  onChange={(_, value) => handleParameterChange("elite_size", value as number)}
                  min={0}
                  max={Math.min(100, parameters.population_size)}
                  step={1}
                  marks={[
                    { value: 0, label: "0" },
                    { value: Math.min(50, parameters.population_size), label: `${Math.min(50, parameters.population_size)}` },
                    { value: Math.min(100, parameters.population_size), label: `${Math.min(100, parameters.population_size)}` },
                  ]}
                  valueLabelDisplay="auto"
                />
                <Typography variant="caption" color="text.secondary">
                  Number of best solutions preserved unchanged
                </Typography>
                {formErrors.elite_size && (
                  <Typography variant="caption" color="error">
                    {formErrors.elite_size}
                  </Typography>
                )}
              </Box>
            </Grid>
          </Grid>

          {/* Submit Error */}
          {formErrors.submit && (
            <Alert severity="error" sx={{ mt: 3 }}>
              {formErrors.submit}
            </Alert>
          )}

          {/* Form Actions */}
          <Box sx={{ mt: 4, display: "flex", justifyContent: "flex-end", gap: 2 }}>
            <Button
              variant="outlined"
              startIcon={<CancelIcon />}
              onClick={onCancel}
              disabled={createMutation.isPending}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant="contained"
              startIcon={<SaveIcon />}
              disabled={createMutation.isPending || templates.length === 0}
            >
              {createMutation.isPending ? (
                <>
                  <CircularProgress size={20} sx={{ mr: 1 }} />
                  Creating...
                </>
              ) : (
                "Create Schedule Solve"
              )}
            </Button>
          </Box>
        </form>
      </CardContent>
    </Card>
  );
}
