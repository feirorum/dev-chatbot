# RAG Documentation Assistant - Frontend

React-based web chat interface for the RAG Documentation Assistant.

## Features

- Clean, modern chat interface
- Real-time conversation with documentation
- Source panel showing relevant documents
- Health status indicator
- Responsive design

## Setup

1. Install dependencies:
```bash
npm install
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env to point to your backend API
```

3. Run development server:
```bash
npm run dev
```

The app will be available at `http://localhost:5173`

## Building for Production

```bash
npm run build
```

The built files will be in the `dist/` directory, ready to deploy to GitHub Pages or any static hosting.

## GitHub Pages Deployment

1. Build the app:
```bash
npm run build
```

2. Deploy to GitHub Pages:
```bash
# Add the dist folder to git
git add dist -f
git commit -m "Build frontend"
git subtree push --prefix dist origin gh-pages
```

Or use GitHub Actions for automated deployment.

## Environment Variables

- `VITE_API_URL`: URL of the backend API (default: `http://localhost:8000`)

## Usage

1. Make sure the backend is running
2. Start the frontend dev server
3. Open the app in your browser
4. Start asking questions about your documentation

The app will retrieve relevant documents and use the LLM to generate helpful responses based on your indexed documentation.
