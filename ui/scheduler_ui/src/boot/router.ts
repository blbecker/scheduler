import { boot } from 'quasar/wrappers';
import createRouter from 'src/router'; // the default export from router/index.ts

export default boot(({ app }) => {
  const router = createRouter();
  app.use(router);
});
