import { createRouter, createWebHistory } from "vue-router";
import MainView from "../views/MainView.vue";
import AddView from "../views/AddView.vue";
import RegionView from "../views/RegionView.vue";
import CragView from "../views/CragView.vue";

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
      path: "/add-topo",
      name: "add-topo",
      component: AddView,
    },
    {
      path: "/region/:region",
      name: "region",
      component: RegionView,
    },
    {
      path: "/crag/:region/:crag",
      name: "crag",
      component: CragView,
    },
    {
      path: "/matching_matrix",
      name: "matching_matrix",
      component: () => import("../views/MatchingMatrix.vue"),
    },
  ],
});

export default router;
