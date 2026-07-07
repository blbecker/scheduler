import { screen, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { render } from "@testing-library/react";
import { SchedulesTable } from "@/components/schedules/SchedulesTable";
import type { ScheduleResponse } from "@/api/models";

const mockSchedules: ScheduleResponse[] = [
  {
    id: "1",
    schedule_template_id: "template-1",
    name: "Week 1 Schedule",
    created_at: "2023-01-01T00:00:00Z",
    updated_at: "2023-01-02T00:00:00Z",
  },
  {
    id: "2",
    schedule_template_id: "template-2",
    name: "Week 2 Schedule",
    created_at: "2023-01-03T00:00:00Z",
    updated_at: "2023-01-04T00:00:00Z",
  },
  {
    id: "3",
    schedule_template_id: "template-1",
    name: "Week 3 Schedule",
    created_at: "2023-01-05T00:00:00Z",
    updated_at: "2023-01-06T00:00:00Z",
  },
];

describe("SchedulesTable", () => {
  const mockOnView = vi.fn();
  const mockOnDelete = vi.fn();

  it("renders schedules data", () => {
    render(
      <SchedulesTable
        schedules={mockSchedules}
        onView={mockOnView}
        onDelete={mockOnDelete}
      />,
    );

    expect(screen.getByText("Week 1 Schedule")).toBeInTheDocument();
    expect(screen.getByText("Week 2 Schedule")).toBeInTheDocument();
    expect(screen.getByText("Week 3 Schedule")).toBeInTheDocument();
    
    const template1Elements = screen.getAllByText("template-1");
    expect(template1Elements).toHaveLength(2);
    const template2Elements = screen.getAllByText("template-2");
    expect(template2Elements).toHaveLength(1);
    
    expect(screen.getByText("ID")).toBeInTheDocument();
    expect(screen.getByText("Schedule Template ID")).toBeInTheDocument();
    expect(screen.getByText("Name")).toBeInTheDocument();
    expect(screen.getByText("Created At")).toBeInTheDocument();
    expect(screen.getByText("Updated At")).toBeInTheDocument();
    expect(screen.getByText("Actions")).toBeInTheDocument();
  });

  it("shows empty state when no schedules", () => {
    render(
      <SchedulesTable schedules={[]} onView={mockOnView} onDelete={mockOnDelete} />,
    );

    expect(
      screen.getByText("No schedules match your search"),
    ).toBeInTheDocument();
  });

  it("calls onView when view button is clicked", () => {
    render(
      <SchedulesTable
        schedules={mockSchedules}
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
      <SchedulesTable
        schedules={mockSchedules}
        onView={mockOnView}
        onDelete={mockOnDelete}
      />,
    );

    const deleteButtons = screen.getAllByTitle("Delete");
    fireEvent.click(deleteButtons[0]);
    expect(mockOnDelete).toHaveBeenCalledWith(mockSchedules[0]);
  });
});