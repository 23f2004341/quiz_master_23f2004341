import { createRouter, createWebHistory } from 'vue-router';
import Login from './views/Login.vue';
import Register from './views/Register.vue';
import UserDashboard from './views/UserDashboard.vue';
import AdminDashboard from './views/AdminDashboard.vue';
import QuizAttempt from './views/QuizAttempt.vue';
import QuizHistory from './views/QuizHistory.vue';
import ManageSubjects from './views/admin/ManageSubjects.vue';
import ManageChapters from './views/admin/ManageChapters.vue';
import ManageQuizzes from './views/admin/ManageQuizzes.vue';
import ManageQuestions from './views/admin/ManageQuestions.vue';
import ManageUsers from './views/admin/ManageUsers.vue';
import Search from './views/admin/Search.vue';
import Charts from './views/admin/Charts.vue';

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', component: Login },
  { path: '/register', component: Register },
  { path: '/user/dashboard', component: UserDashboard },
  { path: '/user/quiz/:id/attempt', component: QuizAttempt },
  { path: '/user/quiz_history', component: QuizHistory },
  { path: '/admin/dashboard', component: AdminDashboard },
  { path: '/admin/subjects', component: ManageSubjects },
  { path: '/admin/chapters', component: ManageChapters },
  { path: '/admin/quizzes', component: ManageQuizzes },
  { path: '/admin/questions', component: ManageQuestions },
  { path: '/admin/users', component: ManageUsers },
  { path: '/admin/search', component: Search },
  { path: '/admin/charts', component: Charts }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
