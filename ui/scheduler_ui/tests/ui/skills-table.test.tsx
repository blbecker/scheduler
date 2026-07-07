import { screen, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { render } from "@testing-library/react";
import { SkillsTable } from "@/components/skills/SkillsTable";
import type { SkillResponse } from "@/api/models";

const mockSkills: SkillResponse[] = [
  {
    id: "1",
    name: "Python Programming",
    description: "Advanced Python development skills",
    created_at: "2023-01-01T00:00:00Z",
    updated_at: "2023-01-02T00:00:00Z",
  },
  {
    id: "2",
    name: "Project Management",
    description: null,
    created_at: "2023-01-03T00:00:00Z",
    updated_at: "2023-01-04T00:00:00Z",
  },
  {
    id: "3",
    name: "Data Analysis",
    description: "Data analysis with SQL and Python",
    created_at: "2023-01-05T00:00:00Z",
    updated_at: "2023-01-06T00:00:00Z",
  },
];

describe("SkillsTable", () => {
  const mockOnView = vi.fn();
  const mockOnDelete = vi.fn();

  it("renders skills data", () => {
    render(
      <SkillsTable
        skills={mockSkills}
        onView={mockOnView}
        onDelete={mockOnDelete}
      />,
    );

    expect(screen.getByText("Python Programming")).toBeInTheDocument();
    expect(screen.getByText("Project Management")).toBeInTheDocument();
    expect(screen.getByText("Data Analysis")).toBeInTheDocument();
    expect(screen.getByText("Advanced Python development skills")).toBeInTheDocument();
    expect(screen.getByText("Data analysis with SQL and Python")).toBeInTheDocument();
    expect(screen.getByText("No description")).toBeInTheDocument();
    
    expect(screen.getByText("ID")).toBeInTheDocument();
    expect(screen.getByText("Name")).toBeInTheDocument();
    expect(screen.getByText("Description")).toBeInTheDocument();
    expect(screen.getByText("Created At")).toBeInTheDocument();
    expect(screen.getByText("Updated At")).toBeInTheDocument();
    expect(screen.getByText("Actions")).toBeInTheDocument();
  });

  it("shows empty state when no skills", () => {
    render(
      <SkillsTable skills={[]} onView={mockOnView} onDelete={mockOnDelete} />,
    );

    expect(
      screen.getByText("No skills match your search"),
    ).toBeInTheDocument();
  });

  it("calls onView when view button is clicked", () => {
    render(
      <SkillsTable
        skills={mockSkills}
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
      <SkillsTable
        skills={mockSkills}
        onView={mockOnView}
        onDelete={mockOnDelete}
      />,
    );

    const deleteButtons = screen.getAllByTitle("Delete");
    fireEvent.click(deleteButtons[0]);
    expect(mockOnDelete).toHaveBeenCalledWith(mockSkills[0]);
  });
});