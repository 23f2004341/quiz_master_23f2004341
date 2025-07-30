<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script>
export default {
  name: "App"
};
</script>

<style>
body {
  background: linear-gradient(135deg, #f8fafc 0%, #e0e7ef 100%);
  font-family: 'Segoe UI', 'Roboto', Arial, sans-serif;
  color: #2c3e50;
  margin: 0;
  min-height: 100vh;
}
#app {
  min-height: 100vh;
}
.card, .table, .form-control, .btn, .list-group-item {
  border-radius: 1rem !important;
  box-shadow: 0 2px 12px rgba(44, 62, 80, 0.08);
}
.card {
  background: #fff;
  border: none;
  margin-bottom: 1.5rem;
}
.table {
  background: #fff;
  border: none;
  margin-bottom: 0;
}
.table th, .table td {
  vertical-align: middle;
  font-size: 1.05rem;
}
.btn-primary {
  background: linear-gradient(90deg, #4f8cff 0%, #1a73e8 100%);
  border: none;
  font-weight: 600;
  letter-spacing: 0.5px;
  color: #fff;
  box-shadow: 0 2px 8px rgba(76, 140, 255, 0.08);
}
.btn-primary:hover {
  background: linear-gradient(90deg, #1a73e8 0%, #4f8cff 100%);
}
.btn-danger {
  background: linear-gradient(90deg, #ff6a6a 0%, #ff8c42 100%);
  border: none;
  font-weight: 600;
  letter-spacing: 0.5px;
  color: #fff;
}
.btn-danger:hover {
  background: linear-gradient(90deg, #ff8c42 0%, #ff6a6a 100%);
}
.btn-info {
  background: linear-gradient(90deg, #00c6ff 0%, #0072ff 100%);
  border: none;
  font-weight: 600;
  color: #fff;
}
.btn-info:hover {
  background: linear-gradient(90deg, #0072ff 0%, #00c6ff 100%);
}
.form-control {
  border: 1px solid #e0e7ef;
  background: #f8fafc;
  font-size: 1.05rem;
  padding: 0.6rem 1rem;
  margin-bottom: 0.5rem;
  box-shadow: none;
}
.form-control:focus {
  border-color: #4f8cff;
  outline: none;
  background: #fff;
}
h1, h2, h3, h4, h5 {
  color: #1a237e;
  font-weight: 700;
  letter-spacing: 1px;
}
label {
  font-weight: 500;
  color: #2c3e50;
}
.list-group-item {
  background: #f8fafc;
  border: none;
  font-size: 1.1rem;
}
input[type="radio"] {
  accent-color: #4f8cff;
}
.alert-info {
  background: #e3f2fd;
  color: #1565c0;
  border: none;
  border-radius: 0.75rem;
}
::-webkit-scrollbar {
  width: 8px;
  background: #e0e7ef;
}
::-webkit-scrollbar-thumb {
  background: #b0bec5;
  border-radius: 4px;
}
</style>
