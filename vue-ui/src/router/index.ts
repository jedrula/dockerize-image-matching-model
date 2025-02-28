import { createRouter, createWebHistory } from "vue-router";
import MainView from "../views/MainView.vue";
import AddView from "../views/AddView.vue";
import RegionView from "../views/RegionView.vue";
import RegionsListView from "../views/RegionsListView.vue";
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
      path: "/match-images",
      name: "match-images",
      component: () => import("../views/MatchImagesView.vue"),
    },
    {
      path: "/",
      name: "main",
      component: MainView,
    },
    {
      path: "/add-region",
      name: "add-region",
      component: AddView,
    },
    {
      path: "/regions",
      name: "regions",
      component: RegionsListView,
    },
    {
      // lists all crags in a region
      path: "/regions/:region",
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
