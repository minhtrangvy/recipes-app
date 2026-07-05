import { createRouter, createWebHistory } from "vue-router";

import RecipeCreateView from "./views/RecipeCreateView.vue";
import RecipeDetailView from "./views/RecipeDetailView.vue";
import RecipeListView from "./views/RecipeListView.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      name: "recipes",
      component: RecipeListView,
    },
    {
      path: "/recipes/new",
      name: "recipe-create",
      component: RecipeCreateView,
    },
    {
      path: "/recipes/:recipeId",
      name: "recipe-detail",
      component: RecipeDetailView,
    },
  ],
});

export default router;
