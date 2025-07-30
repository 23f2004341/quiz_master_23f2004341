import Vue from 'vue';
import Router from 'vue-router';

//Import your views here
// Example:
import Register from '../views/user/Register.vue';
import Login from '../views/user/Login.vue';
//import Home from '../views/Home.vue';
import ManageQuizzes from '../views/admin/ManageQuizzes.vue';
import Charts from '../views/admin/Charts.vue';
import ManageChapters from '../views/admin/ManageChapters.vue'; 
import ManageQuestions from '../views/admin/ManageQuestions.vue';
import ManageSubjects from '../views/admin/ManageSubjects.vue';
import ManageUsers from '../views/admin/ManageUsers.vue';
import Search from '../views/admin/Search.vue';
import QuizAttempt from '../views/user/QuizAttempt.vue';
import QuizHistory from '../views/user/QuizHistory.vue';    
import UserDashboard from '../views/user/UserDashboard.vue';


Vue.use(Router);

export default new Router({
  mode: 'history',
  routes: [
   { path: '/register', component: Register },
   { path: '/login', component: Login },
   { path: '/admin/dashboard', component: require('../views/admin/AdminDashboard.vue').default },
   { path: '/admin/users', component: ManageUsers },
   { path: '/admin/subjects', component: ManageSubjects },
   { path: '/admin/chapters', component: ManageChapters },
   { path: '/admin/quizzes', component: ManageQuizzes },
   { path: '/admin/questions', component: ManageQuestions },
   { path: '/admin/charts', component: Charts },
   { path: '/admin/search', component: Search },
   { path: '/user/dashboard', component: UserDashboard },
   { path: '/user/quiz/:id/attempt', component: QuizAttempt, props: true },
   { path: '/user/quiz_history', component: QuizHistory },
   { path: '/', redirect: '/login' }
 ]
});



