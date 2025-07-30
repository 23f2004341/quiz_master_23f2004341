<template>
  <div class="container mt-4">
    <h2>Quiz Analytics Charts</h2>
    <div class="row">
      <div class="col-md-6">
        <h5>Quiz Attempts Over Time</h5>
        <canvas id="attemptsChart"></canvas>
      </div>
      <div class="col-md-6">
        <h5>Top Scoring Users</h5>
        <canvas id="topUsersChart"></canvas>
      </div>
    </div>
  </div>
</template>
<script>
import axios from 'axios';
import Chart from 'chart.js/auto';
export default {
  data() {
    return {
      attemptsData: [],
      topUsersData: [],
      attemptsChart: null,
      topUsersChart: null,
      refreshInterval: null
    };
  },
  async mounted() {
    await this.fetchAnalytics();
    this.renderCharts();
    this.refreshInterval = setInterval(async () => {
      await this.fetchAnalytics();
      this.renderCharts();
    }, 30000); // 30 seconds
  },
  beforeDestroy() {
    if (this.refreshInterval) clearInterval(this.refreshInterval);
    if (this.attemptsChart) this.attemptsChart.destroy();
    if (this.topUsersChart) this.topUsersChart.destroy();
  },
  methods: {
    async fetchAnalytics() {
      const res = await axios.get('/api/admin/analytics');
      this.attemptsData = res.data.attempts_over_time;
      this.topUsersData = res.data.top_users;
    },
    renderCharts() {
      // Destroy previous charts if they exist
      if (this.attemptsChart) this.attemptsChart.destroy();
      if (this.topUsersChart) this.topUsersChart.destroy();
      // Quiz Attempts Over Time
      this.attemptsChart = new Chart(document.getElementById('attemptsChart'), {
        type: 'line',
        data: {
          labels: this.attemptsData.map(a => a.date),
          datasets: [{
            label: 'Attempts',
            data: this.attemptsData.map(a => a.count),
            borderColor: 'blue',
            fill: false
          }]
        }
      });
      // Top Scoring Users
      this.topUsersChart = new Chart(document.getElementById('topUsersChart'), {
        type: 'bar',
        data: {
          labels: this.topUsersData.map(u => u.name),
          datasets: [{
            label: 'Total Score',
            data: this.topUsersData.map(u => u.score),
            backgroundColor: 'green'
          }]
        }
      });
    }
  }
};
</script>
