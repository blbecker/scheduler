import type { RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: '',
        component: () => import('pages/IndexPage.vue'),
      },
    ],
  },
  {
    path: '/shifts',
    component: () => import('layouts/ShiftLayout.vue'),
    children: [
      {
        path: '',
        component: () => import('pages/ShiftsPage.vue'),
        name: 'shifts',
      },
      {
        path: ':id',
        component: () => import('pages/ShiftDetailPage.vue'),
        name: 'shift-detail',
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
