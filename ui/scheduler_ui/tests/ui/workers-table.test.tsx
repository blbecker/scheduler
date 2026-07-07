import { screen, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { render } from "@testing-library/react";
import { WorkersTable } from "@/components/workers/WorkersTable";
import type { WorkerResponse } from "@/api/models";

// Create mock data
const mockWorkers: WorkerResponse[] = [
  {
    id: "1",
    name: "John Doe",
    created_at: "2023-01-01T00:00:00Z",
    updated_at: "2023-01-02T00:00:00Z",
  },
  {
    id: "2",
    name: "Jane Smith",
    created_at: "2023-01-03T00:00:00Z",
    updated_at: "2023-01-04T00:00:00Z",
  },
];

describe("WorkersTable", () => {
  const mockOnView = vi.fn();
  const mockOnDelete = vi.fn();

  it("renders workers data", () => {
    render(
      <WorkersTable
        workers={mockWorkers}
        onView={mockOnView}
        onDelete={mockOnDelete}
      />,
    );

    expect(screen.getByText("John Doe")).toBeInTheDocument();
    expect(screen.getByText("Jane Smith")).toBeInTheDocument();
    expect(screen.getByText("ID")).toBeInTheDocument();
    expect(screen.getByText("Name")).toBeInTheDocument();
    expect(screen.getByText("Created At")).toBeInTheDocument();
    expect(screen.getByText("Updated At")).toBeInTheDocument();
    expect(screen.getByText("Actions")).toBeInTheDocument();
  });

  it("shows empty state when no workers", () => {
    render(
      <WorkersTable workers={[]} onView={mockOnView} onDelete={mockOnDelete} />,
    );

    expect(
      screen.getByText("No workers match your search"),
    ).toBeInTheDocument();
  });

  it("calls onView when view button is clicked", () => {
    render(
      <WorkersTable
        workers={mockWorkers}
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
      <WorkersTable
        workers={mockWorkers}
        onView={mockOnView}
        onDelete={mockOnDelete}
      />,
    );

    const deleteButtons = screen.getAllByTitle("Delete");
    fireEvent.click(deleteButtons[0]);
    expect(mockOnDelete).toHaveBeenCalledWith(mockWorkers[0]);
  });
});
