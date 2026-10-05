import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "sonner";
import { App } from "@/App";
import "@/index.css";

/**
 * Server state is TanStack Query's job, with retries off: this is a debugging tool for a
 * local platform, and a hidden retry would turn "the fixture is missing" into a spinner.
 */
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
      refetchOnWindowFocus: false,
    },
  },
});

const root = document.getElementById("root");
if (!root) throw new Error("#root is missing from index.html");

createRoot(root).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <App />
        <Toaster position="bottom-right" closeButton />
      </BrowserRouter>
    </QueryClientProvider>
  </StrictMode>,
);
