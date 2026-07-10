import { screen, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { render } from "@testing-library/react";
import { ShiftTemplatesTable } from "@/components/shift-templates/ShiftTemplatesTable";
import type { ShiftTemplateResponse } from "@/api/models";

const mockShiftTemplates: ShiftTemplateResponse[] = [
  {
    id: "1",
    schedule_template_id: "schedule-1",
    name: "Morning Shift",
    start_time: "09:00",
    end_time: "17:00",
    created_at: "2023-01-01T00:00:00Z",
    updated_at: "2023-01-02T00:00:00Z",
  },
  {
    id: "2",
    schedule_template_id: "schedule-2",
    name: "Night Shift",
    start_time: "22:00",
    end_time: "06:00",
    created_at: "2023-01-03T00:00:00Z",
    updated_at: "2023-01-04T00:00:00Z",
  },
  {
    id: "3",
    schedule_template_id: "schedule-1",
    name: "Weekend Shift",
    start_time: "10:00",
    end_time: "18:00",
    created_at: "2023-01-05T00:00:00Z",
    updated_at: "2023-01-06T00:00:00Z",
  },
];

describe("ShiftTemplatesTable", () => {
  const mockOnView = vi.fn();
  const mockOnDelete = vi.fn();

  it("renders shift templates data", () => {
    render(
      <ShiftTemplatesTable
        shiftTemplates={mockShiftTemplates}
        onView={mockOnView}
        onDelete={mockOnDelete}
      />,
    );

    expect(screen.getByText("Morning Shift")).toBeInTheDocument();
    expect(screen.getByText("Night Shift")).toBeInTheDocument();
    expect(screen.getByText("Weekend Shift")).toBeInTheDocument();

    const schedule1Elements = screen.getAllByText("schedule-1");
    expect(schedule1Elements).toHaveLength(2);
    const schedule2Elements = screen.getAllByText("schedule-2");
    expect(schedule2Elements).toHaveLength(1);

    expect(screen.getByText("ID")).toBeInTheDocument();
    expect(screen.getByText("Schedule Template ID")).toBeInTheDocument();
    expect(screen.getByText("Name")).toBeInTheDocument();
    expect(screen.getByText("Start Time")).toBeInTheDocument();
    expect(screen.getByText("End Time")).toBeInTheDocument();
    expect(screen.getByText("Created At")).toBeInTheDocument();
    expect(screen.getByText("Updated At")).toBeInTheDocument();
    expect(screen.getByText("Actions")).toBeInTheDocument();
  });

  it("shows empty state when no shift templates", () => {
    render(
      <ShiftTemplatesTable shiftTemplates={[]} onView={mockOnView} onDelete={mockOnDelete} />,
    );

    expect(
      screen.getByText("No shift templates match your search"),
    ).toBeInTheDocument();
  });

  it("calls onView when view button is clicked", () => {
    render(
      <ShiftTemplatesTable
        shiftTemplates={mockShiftTemplates}
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
      <ShiftTemplatesTable
        shiftTemplates={mockShiftTemplates}
        onView={mockOnView}
        onDelete={mockOnDelete}
      />,
    );

    const deleteButtons = screen.getAllByTitle("Delete");
    fireEvent.click(deleteButtons[0]);
    expect(mockOnDelete).toHaveBeenCalledWith(mockShiftTemplates[0]);
  });
});
