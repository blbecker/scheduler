import type { RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    // component: () => import('layouts/MainLayout.vue'),
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
        component: () => import('pages/ShiftListPage.vue'),
      },
      {
        path: ':id',
        component: () => import('pages/ShiftDetailPage.vue'),
      },
    ],
  },
  {
    path: '/skills',
    component: () => import('layouts/SkillLayout.vue'),
    children: [
      {
        path: '',
        component: () => import('pages/SkillListPage.vue'),
      },
      {
        path: ':id',
        component: () => import('pages/SkillDetailPage.vue'),
      },
    ],
  },
  {
    path: '/workers',
    component: () => import('layouts/WorkerLayout.vue'),
    children: [
      {
        path: '',
        component: () => import('pages/WorkerListPage.vue'),
      },
      {
        path: ':id',
        component: () => import('pages/WorkerDetailPage.vue'),
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
