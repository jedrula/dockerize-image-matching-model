import { createRouter, createWebHistory } from "vue-router";
import MainView from "../views/MainView.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/base",
      name: "base",
      component: import("../views/HomeView.vue"),
    },
    {
      path: "/",
      name: "main",
      component: MainView,
    },
    {
      path: "/matching_matrix",
      name: "matching_matrix",
      component: () => import("../views/MatchingMatrix.vue"),
    },
  ],
});

export default router;
