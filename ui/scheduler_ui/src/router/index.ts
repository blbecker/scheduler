import { createRouter, createWebHashHistory, type RouterOptions } from 'vue-router';
import routes from './routes';

export default function defineRouter() {
  const routerOptions: RouterOptions = {
    history: createWebHashHistory(),
    routes,
  };

  return createRouter(routerOptions);
}
