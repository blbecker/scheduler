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
    path: '/shift',
    component: () => import('layouts/ShiftLayout.vue'),
    children: [
      {
        path: 'list',
        component: () => import('pages/ShiftListPage.vue'),
      },
      {
        path: ':id',
        component: () => import('pages/ShiftDetailPage.vue'),
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
