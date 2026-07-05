import { screen, waitFor, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { http, HttpResponse } from "msw";
import { setupServer } from "msw/node";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render } from "@testing-library/react";
import { WorkersDataGrid } from "@/components/workers/WorkersDataGrid";
import { getListWorkersResponseMock } from "@/api/client/workers/workers.msw";
import type { WorkerResponse } from "@/api/models";

// Mock next/navigation
vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push: vi.fn(),
  }),
}));

// Create mock data
const mockWorkers: WorkerResponse[] = [
  {
    id: "worker-1",
    name: "John Doe",
    created_at: "2024-01-01T10:00:00Z",
    updated_at: "2024-01-02T10:00:00Z",
  },
  {
    id: "worker-2",
    name: "Jane Smith",
    created_at: "2024-01-01T11:00:00Z",
    updated_at: "2024-01-02T11:00:00Z",
  },
];

// Setup MSW server
const server = setupServer(
  http.get("*/workers/", () => {
    return HttpResponse.json(mockWorkers);
  })
);

describe("WorkersDataGrid", () => {
  beforeAll(() => server.listen());
  afterEach(() => server.resetHandlers());
  afterAll(() => server.close());

  it("renders loading state initially", () => {
    const queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
          staleTime: Infinity,
        },
      },
    });

    render(
      <QueryClientProvider client={queryClient}>
        <WorkersDataGrid />
      </QueryClientProvider>
    );

    expect(screen.getByRole("progressbar")).toBeInTheDocument();
  });

  it("renders workers data after loading", async () => {
    const queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
          staleTime: Infinity,
        },
      },
    });

    render(
      <QueryClientProvider client={queryClient}>
        <WorkersDataGrid />
      </QueryClientProvider>
    );

    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText("John Doe")).toBeInTheDocument();
      expect(screen.getByText("Jane Smith")).toBeInTheDocument();
    });
  });

  it("shows empty state when no workers", async () => {
    // Override handler for empty response
    server.use(
      http.get("*/workers/", () => {
        return HttpResponse.json([]);
      })
    );

    const queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
          staleTime: Infinity,
        },
      },
    });

    render(
      <QueryClientProvider client={queryClient}>
        <WorkersDataGrid />
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText("No workers found")).toBeInTheDocument();
      expect(screen.getByText("Add First Worker")).toBeInTheDocument();
    });
  });

  it("shows error state when API fails", async () => {
    // Override handler for error response
    server.use(
      http.get("*/workers/", () => {
        return new HttpResponse(null, { status: 500 });
      })
    );

    const queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
          staleTime: Infinity,
        },
      },
    });

    render(
      <QueryClientProvider client={queryClient}>
        <WorkersDataGrid />
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText(/Error loading workers/)).toBeInTheDocument();
    });
  });

  it("filters workers based on search term", async () => {
    const queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
          staleTime: Infinity,
        },
      },
    });

    render(
      <QueryClientProvider client={queryClient}>
        <WorkersDataGrid />
      </QueryClientProvider>
    );

    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText("John Doe")).toBeInTheDocument();
    });

    // Find search input and type "John"
    const searchInput = screen.getByPlaceholderText("Search workers...");
    fireEvent.change(searchInput, { target: { value: "John" } });

    // John should still be visible, Jane should be filtered out
    await waitFor(() => {
      expect(screen.getByText("John Doe")).toBeInTheDocument();
      expect(screen.queryByText("Jane Smith")).not.toBeInTheDocument();
    });
  });
});