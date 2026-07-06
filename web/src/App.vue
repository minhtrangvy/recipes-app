<template>
  <main class="app-shell">
    <header class="app-header">
      <div>
        <p class="eyebrow"><RouterLink to="/">Recipe Book</RouterLink></p>
        <h1>Recipes</h1>
      </div>
      <nav class="app-nav">
        <RouterLink to="/recipes/new">Add recipe</RouterLink>
      </nav>
    </header>

    <RouterView />
  </main>
</template>

<style scoped>
:global(body) {
  margin: 0;
  font-family: Arial, sans-serif;
  background: #f7f1e8;
  color: #1e1a16;
}

:global(*) {
  box-sizing: border-box;
}

:global(a) {
  color: inherit;
}

.app-shell {
  max-width: 960px;
  margin: 0 auto;
  padding: 32px 20px 48px;
}

.app-header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: end;
  margin-bottom: 32px;
}

.eyebrow {
  margin: 0 0 8px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-size: 12px;
}

h1 {
  margin: 0;
  font-size: 40px;
}

.app-nav {
  display: flex;
  gap: 16px;
  font-weight: 700;
}
</style>
