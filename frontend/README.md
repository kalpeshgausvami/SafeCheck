# Reel Truth Checker Frontend 💻🎨

This directory contains the user interface of the **Reel Truth Checker** application. It is built using **React**, **TypeScript**, **Vite**, and **TailwindCSS**, featuring a modern dark/light themed, responsive dashboard.

---

## 📂 Frontend Directory Structure

```directory
src/
├── assets/                  # Hero image, logo, and static SVG icons
├── components/              # Core reusable UI React components:
│   ├── FactHero.tsx         # Input interface for the Fact-Checker mode
│   ├── FactProgressScreen.tsx # Multi-step simulation analyzer screen for Reels
│   ├── FactResultsDashboard.tsx # Analysis breakdown for Reel fact-checking
│   ├── Hero.tsx             # Input interface for the Account Safety mode
│   ├── Navbar.tsx           # Global navigation bar
│   ├── ProcessSteps.tsx     # Overview of how analysis works
│   ├── ProgressScreen.tsx   # Scanning progress screen for Account Safety
│   └── ResultsDashboard.tsx # Analysis breakdown for Account Safety
├── App.css                  # Custom root styling classes
├── App.tsx                  # Root component holding state-machine & modes
├── index.css                # Global styles, variables, utility classes
├── main.tsx                 # Vite mounting file
├── factCheckData.ts         # Mock data and resolver logic for Fact-Checking
└── mockData.ts              # Mock data and resolver logic for Account Safety
```

---

## ⚙️ Core Application Modes & States

The React interface acts as a state machine managed via `src/App.tsx`.

### 1. Application Modes (`AppMode`)
*   `account`: The **Account Safety** module, which evaluates a user profile username, analyzes bot risk levels, calculates a trust score, and outputs details of active security signals.
*   `factcheck`: The **Fact Checker** module, which evaluates specific Instagram Reel URLs, extracts claims, verifies them, and showcases explainability matrices.

### 2. View States (`ViewState`)
*   `landing`: Home page with heroes and search input.
*   `analyzing`: Loading stage simulating real-time NLP claim extraction and transcription.
*   `results`: Final dashboards populated with model scores.

---

## 🛠️ Local Development & Scripts

### 1. Prerequisites
Make sure you have **Node.js (v20+)** installed.

### 2. Setup & Execution
Run the following commands in the root of the project (where `package.json` is located):

```bash
# Install dependencies
npm install

# Run Vite dev server
npm run dev

# Build production bundle
npm run build

# Preview production build locally
npm run preview

# Run ESLint validation
npm run lint
```
Vite will start the development server, usually accessible at [http://localhost:5173](http://localhost:5173).

---

## 🎨 Styles & Customizations
*   **Design Tokens**: Custom CSS variables for gradients, border-radius, background orbs, and text are defined in `src/index.css`.
*   **Tailwind Configuration**: Tailwind integration is handled in `tailwind.config.js` and `postcss.config.js`.
*   **Dark Mode**: Handled via class injection (`document.body.classList.add('dark')`). The toggle action resides in the Navbar component.
