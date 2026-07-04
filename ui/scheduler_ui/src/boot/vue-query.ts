import { QueryClient, VueQueryPlugin } from "@tanstack/vue-query";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

export default ({ app }) => {
  app.use(VueQueryPlugin, { queryClient });
};
