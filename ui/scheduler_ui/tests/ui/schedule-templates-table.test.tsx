import { screen, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { render } from "@testing-library/react";
import { ScheduleTemplatesTable } from "@/components/schedule-templates/ScheduleTemplatesTable";
import type { ScheduleTemplateResponse } from "@/api/models";

const mockScheduleTemplates: ScheduleTemplateResponse[] = [
  {
    id: "1",
    name: "Weekly Schedule",
    created_at: "2023-01-01T00:00:00Z",
    updated_at: "2023-01-02T00:00:00Z",
  },
  {
    id: "2",
    name: "Monthly Rotation",
    created_at: "2023-01-03T00:00:00Z",
    updated_at: "2023-01-04T00:00:00Z",
  },
  {
    id: "3",
    name: "Shift Rotation",
    created_at: "2023-01-05T00:00:00Z",
    updated_at: "2023-01-06T00:00:00Z",
  },
];

describe("ScheduleTemplatesTable", () => {
  const mockOnView = vi.fn();
  const mockOnDelete = vi.fn();

  it("renders schedule templates data", () => {
    render(
      <ScheduleTemplatesTable
        scheduleTemplates={mockScheduleTemplates}
        onView={mockOnView}
        onDelete={mockOnDelete}
      />,
    );

    expect(screen.getByText("Weekly Schedule")).toBeInTheDocument();
    expect(screen.getByText("Monthly Rotation")).toBeInTheDocument();
    expect(screen.getByText("Shift Rotation")).toBeInTheDocument();
    
    expect(screen.getByText("ID")).toBeInTheDocument();
    expect(screen.getByText("Name")).toBeInTheDocument();
    expect(screen.getByText("Created At")).toBeInTheDocument();
    expect(screen.getByText("Updated At")).toBeInTheDocument();
    expect(screen.getByText("Actions")).toBeInTheDocument();
  });

  it("shows empty state when no schedule templates", () => {
    render(
      <ScheduleTemplatesTable scheduleTemplates={[]} onView={mockOnView} onDelete={mockOnDelete} />,
    );

    expect(
      screen.getByText("No schedule templates match your search"),
    ).toBeInTheDocument();
  });

  it("calls onView when view button is clicked", () => {
    render(
      <ScheduleTemplatesTable
        scheduleTemplates={mockScheduleTemplates}
        onView={mockOnView}
        onDelete={mockOnDelete}
      />,
    );

    const viewButtons = screen.getAllByTitle("View");
    fireEvent.click(viewButtons[0]);
    expect(mockOnView).toHaveBeenCalledWith("1");
  });

  it("calls onDelete when delete button is clicked", () => {
    render(
      <ScheduleTemplatesTable
        scheduleTemplates={mockScheduleTemplates}
        onView={mockOnView}
        onDelete={mockOnDelete}
      />,
    );

    const deleteButtons = screen.getAllByTitle("Delete");
    fireEvent.click(deleteButtons[0]);
    expect(mockOnDelete).toHaveBeenCalledWith(mockScheduleTemplates[0]);
  });
});