# Chat Frontend

A React + TypeScript single-page chat interface for the Cybersecurity Training Assistant.

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Chat.tsx          # Main chat container component
│   │   ├── ChatMessage.tsx   # Individual message component
│   │   └── InputBar.tsx      # Message input component
│   ├── api/
│   │   └── client.ts         # Backend API client
│   ├── styles/
│   │   └── chat.css          # Chat UI theme and styles
│   ├── App.tsx               # Root app component
│   ├── main.tsx              # Application entry point
│   └── index.css             # Global styles
├── index.html                # HTML template
├── package.json              # Dependencies and scripts
├── tsconfig.json             # TypeScript configuration
├── vite.config.ts            # Vite build configuration
└── README.md                 # This file
```

## Getting Started

### Prerequisites

- Node.js 18+ and npm/yarn/pnpm

### Installation

```bash
npm install
```

### Development

Start the development server:

```bash
npm run dev
```

The app will be available at `http://localhost:3000`

### Build

Build for production:

```bash
npm run build
```

### Preview

Preview the production build:

```bash
npm run preview
```

## Configuration

The API base URL can be configured via environment variable:

- Create a `.env` file in the `frontend/` directory
- Add: `VITE_API_BASE_URL=http://localhost:8000`

By default, the app connects to `http://localhost:8000` (configured in `vite.config.ts` proxy settings).

## Features

- Real-time chat interface
- Message history
- Loading states with typing indicator
- Error handling
- Responsive design
- Modern UI with gradient themes

