import MainLayout from 'layouts/MainLayout.vue';
import ShiftLayout from 'layouts/ShiftLayout.vue';
import SkillLayout from 'layouts/SkillLayout.vue';
import WorkerLayout from 'layouts/WorkerLayout.vue';

import ShiftListPage from 'pages/shifts/ShiftListPage.vue';
import SkillListPage from 'pages/skills/SkillListPage.vue';
import WorkerListPage from 'pages/workers/WorkerListPage.vue';

const routes = [
  {
    path: '/',
    component: MainLayout,
    children: [
      // Redirect root to /shifts
      { path: '', redirect: '/shifts' },

      // Shifts section
      {
        path: 'shifts',
        component: ShiftLayout,
        children: [
          {
            path: '',
            name: 'ShiftList',
            component: ShiftListPage,
          },
          // Add additional shift-specific pages here
          // { path: ':id', name: 'ShiftDetail', component: ShiftDetailPage }
        ],
      },

      // Skills section
      {
        path: 'skills',
        component: SkillLayout,
        children: [
          {
            path: '',
            name: 'SkillList',
            component: SkillListPage,
          },
        ],
      },

      // Workers section
      {
        path: 'workers',
        component: WorkerLayout,
        children: [
          {
            path: '',
            name: 'WorkerList',
            component: WorkerListPage,
          },
        ],
      },
    ],
  },

  // Catch-all route redirects back to root
  { path: '/:catchAll(.*)*', redirect: '/' },
];

export default routes;
