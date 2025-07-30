<template>
  <div class="admin-dashboard-bg min-vh-100 py-4">
    <div class="container">
      <div class="d-flex justify-content-between align-items-center mb-4">
        <h2 class="dashboard-title"><i class="fas fa-user-shield me-2"></i>Admin Dashboard</h2>
        <button class="btn btn-danger btn-lg px-4" @click="logout"><i class="fas fa-sign-out-alt me-2"></i>Logout</button>
      </div>

      <!-- Summary Cards -->
      <div class="row g-3 mb-4">
        <div class="col-6 col-md-3">
          <div class="card shadow-sm text-center stat-card bg-primary text-white">
            <div class="card-body">
              <div class="display-5 mb-2"><i class="fas fa-users"></i></div>
              <h3 class="card-title mb-0">Users</h3>
              <p class="card-text">Manage all users</p>
            </div>
          </div>
        </div>
        <div class="col-6 col-md-3">
          <div class="card shadow-sm text-center stat-card bg-success text-white">
            <div class="card-body">
              <div class="display-5 mb-2"><i class="fas fa-book"></i></div>
              <h3 class="card-title mb-0">Subjects</h3>
              <p class="card-text">Manage subjects</p>
            </div>
          </div>
        </div>
        <div class="col-6 col-md-3">
          <div class="card shadow-sm text-center stat-card bg-warning text-white">
            <div class="card-body">
              <div class="display-5 mb-2"><i class="fas fa-layer-group"></i></div>
              <h3 class="card-title mb-0">Chapters</h3>
              <p class="card-text">Manage chapters</p>
            </div>
          </div>
        </div>
        <div class="col-6 col-md-3">
          <div class="card shadow-sm text-center stat-card bg-info text-white">
            <div class="card-body">
              <div class="display-5 mb-2"><i class="fas fa-question-circle"></i></div>
              <h3 class="card-title mb-0">Quizzes</h3>
              <p class="card-text">Manage quizzes</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Navigation Cards -->
      <div class="row g-4 mb-4">
        <div class="col-md-4" v-for="card in adminCards" :key="card.title">
          <div class="card h-100 shadow admin-card">
            <div class="card-body d-flex flex-column justify-content-between">
              <div>
                <h5 class="card-title mb-2"><i :class="card.icon + ' me-2'"></i>{{ card.title }}</h5>
                <p class="card-text text-secondary">{{ card.desc }}</p>
              </div>
              <router-link :to="card.route" class="btn btn-primary mt-3 w-100"><i :class="card.icon + ' me-2'"></i>Go to {{ card.title }}</router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
export default {
  name: 'AdminDashboard',
  data() {
    return {
      adminCards: [
        { title: 'Manage Users', desc: 'View, edit, or delete users.', route: '/admin/users', icon: 'fas fa-users-cog' },
        { title: 'Manage Subjects', desc: 'Create, edit, or delete subjects.', route: '/admin/subjects', icon: 'fas fa-book' },
        { title: 'Manage Chapters', desc: 'Create, edit, or delete chapters.', route: '/admin/chapters', icon: 'fas fa-layer-group' },
        { title: 'Manage Quizzes', desc: 'Create, edit, or delete quizzes.', route: '/admin/quizzes', icon: 'fas fa-question-circle' },
        { title: 'Manage Questions', desc: 'Create, edit, or delete quiz questions.', route: '/admin/questions', icon: 'fas fa-edit' },
        { title: 'Charts & Analytics', desc: 'View quiz performance analytics.', route: '/admin/charts', icon: 'fas fa-chart-bar' },
        { title: 'Search', desc: 'Search users, quizzes, subjects, and more.', route: '/admin/search', icon: 'fas fa-search' }
      ]
    };
  },
  methods: {
    async logout() {
      await axios.post('/api/logout');
      localStorage.clear();
      this.$router.push('/login');
    }
  }
};
</script>

<style scoped>
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');
.admin-dashboard-bg {
  background: linear-gradient(135deg, #f8fafc 0%, #e0e7ef 100%);
  font-family: 'Segoe UI', 'Roboto', Arial, sans-serif;
}
.dashboard-title {
  color: #2c3e50;
  font-weight: 700;
  letter-spacing: 1px;
}
.admin-card {
  border: none;
  border-radius: 1rem;
  transition: box-shadow 0.2s, transform 0.2s;
  box-shadow: 0 2px 12px rgba(44, 62, 80, 0.08);
  background: #fff;
}
.admin-card:hover {
  box-shadow: 0 6px 24px rgba(44, 62, 80, 0.18);
  transform: translateY(-4px) scale(1.03);
}
.card-title {
  font-size: 1.3rem;
  color: #1a237e;
}
.btn-primary {
  background: linear-gradient(90deg, #4f8cff 0%, #1a73e8 100%);
  border: none;
  font-weight: 600;
  letter-spacing: 0.5px;
}
.btn-primary:hover {
  background: linear-gradient(90deg, #1a73e8 0%, #4f8cff 100%);
}
.btn-danger {
  font-weight: 600;
  letter-spacing: 0.5px;
}
.stat-card {
  min-height: 140px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.bg-success {
  background: linear-gradient(90deg, #43e97b 0%, #38f9d7 100%) !important;
  color: #fff !important;
  font-weight: 600;
}
.bg-primary {
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%) !important;
}
.bg-warning {
  background: linear-gradient(90deg, #f093fb 0%, #f5576c 100%) !important;
}
.bg-info {
  background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%) !important;
}
</style> 