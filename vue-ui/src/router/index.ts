import { createRouter, createWebHistory } from "vue-router";
import HomeView from "../views/HomeView.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "home",
      component: HomeView,
    },
    {
      path: "/matching_matrix",
      name: "matching_matrix",
      component: () => import("../views/MatchingMatrix.vue"),
    },
  ],
});

export default router;
