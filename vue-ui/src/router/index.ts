import { createRouter, createWebHistory } from "vue-router";
import MainView from "../views/MainView.vue";
import AddView from "../views/AddView.vue";
import RegionView from "../views/RegionView.vue";
import CragView from "../views/CragView.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      // legacy route but still functional and can be useful for debugging matching mechanisms/results
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
      // TODO - just a placeholder, will allow adding new topos in the future
      path: "/add-topo",
      name: "add-topo",
      component: AddView,
    },
    {
      // lists all crags in a region
      path: "/region/:region",
      name: "region",
      component: RegionView,
    },
    {
      // shows single crag (with multiple paths), allows editing
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
