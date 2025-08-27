import type { RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    // component: () => import('layouts/MainLayout.vue'),
    component: () => import('layouts/ShiftLayout.vue'),
    children: [
      {
        path: '',
        component: () => import('pages/ShiftListPage.vue'),
      },
    ],
  },
  {
    path: '/shifts',
    component: () => import('layouts/ShiftLayout.vue'),
    children: [
      {
        path: '',
        component: () => import('pages/ShiftListPage.vue'),
      },
    ],
  },

  // Always leave this as last one,
  // but you can also remove it
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue'),
  },
];

export default routes;
