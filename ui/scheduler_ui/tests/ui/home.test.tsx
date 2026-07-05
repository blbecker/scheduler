import { screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Page from "@/app/page";
import { renderWithProviders } from "@/test/utils/render";

describe("Home page", () => {
  it('renders "page.tsx"', () => {
    renderWithProviders(<Page />);
    expect(screen.getByRole("heading")).toBeInTheDocument();
  });
});
