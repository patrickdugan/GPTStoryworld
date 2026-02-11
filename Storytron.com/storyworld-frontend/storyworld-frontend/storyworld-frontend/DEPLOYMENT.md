# Deployment Guide

## Quick Deploy Options

### 1. Vercel (Recommended - Easiest)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd storyworld-frontend
vercel
```

**Features**:
- ✅ Zero config
- ✅ Automatic HTTPS
- ✅ CDN distribution
- ✅ Free tier available

**Result**: `https://gpt-storyworld.vercel.app`

---

### 2. Netlify

```bash
# Install Netlify CLI
npm i -g netlify-cli

# Build
npm run build

# Deploy
netlify deploy --prod --dir=dist
```

**Features**:
- ✅ Drag-and-drop option via web UI
- ✅ Continuous deployment from GitHub
- ✅ Serverless functions available

**Result**: `https://gpt-storyworld.netlify.app`

---

### 3. GitHub Pages

```bash
# Add to package.json
{
  "scripts": {
    "deploy": "vite build && gh-pages -d dist"
  }
}

# Install gh-pages
npm i -D gh-pages

# Deploy
npm run deploy
```

**Features**:
- ✅ Free hosting
- ✅ Auto-deploy on push
- ✅ Custom domain support

**Result**: `https://patrickdugan.github.io/GPTStoryworld`

---

### 4. Self-Hosted (Docker)

```dockerfile
# Create Dockerfile
FROM node:18-alpine

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=0 /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

```bash
# Build & run
docker build -t gpt-storyworld .
docker run -p 80:80 gpt-storyworld
```

**Features**:
- ✅ Full control
- ✅ Works anywhere
- ✅ Easy scaling

**Result**: `http://your-server.com`

---

## Environment Configuration

### Production Environment Variables

Create `.env.production`:

```bash
VITE_API_ENDPOINT=https://api.openai.com/v1
VITE_DEFAULT_MODEL=gpt-4
VITE_APP_VERSION=1.0.0
```

### Build Optimization

In `vite.config.js`:

```javascript
export default defineConfig({
  build: {
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true
      }
    },
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom'],
          'icons': ['lucide-react']
        }
      }
    }
  }
})
```

---

## Custom Domain Setup

### Vercel

1. Go to project settings → Domains
2. Add your domain: `storyworld.yoursite.com`
3. Update DNS with provided records

### Netlify

1. Domain settings → Add custom domain
2. Configure DNS:
   ```
   storyworld.yoursite.com CNAME xyz.netlify.app
   ```

---

## CI/CD Workflows

### GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 18
      - run: npm ci
      - run: npm run build
      - uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./dist
```

---

## Performance Optimization

### 1. Enable Compression

For nginx:

```nginx
gzip on;
gzip_types text/plain text/css application/json application/javascript;
gzip_min_length 1000;
```

### 2. Add Cache Headers

```nginx
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### 3. Preload Critical Resources

In `index.html`:

```html
<link rel="preconnect" href="https://api.openai.com">
<link rel="preload" as="style" href="/assets/index.css">
```

---

## Security Considerations

### 1. CSP Headers

Add to your server config:

```
Content-Security-Policy: default-src 'self'; connect-src 'self' https://api.openai.com; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';
```

### 2. API Key Protection

**❌ Never commit API keys to git**

Add to `.gitignore`:
```
.env
.env.local
.env.*.local
```

### 3. Rate Limiting

Consider adding client-side rate limiting:

```javascript
let lastRequest = 0;
const MIN_INTERVAL = 2000; // 2 seconds

async function rateLimitedGenerate() {
  const now = Date.now();
  if (now - lastRequest < MIN_INTERVAL) {
    alert('Please wait before generating again');
    return;
  }
  lastRequest = now;
  await handleGenerate();
}
```

---

## Monitoring

### Analytics Integration

Add to `index.html`:

```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```

### Error Tracking (Sentry)

```bash
npm install @sentry/react
```

```javascript
// main.jsx
import * as Sentry from "@sentry/react";

Sentry.init({
  dsn: "YOUR_SENTRY_DSN",
  environment: "production"
});
```

---

## Troubleshooting

### Build Fails

```bash
# Clear cache
rm -rf node_modules dist
npm cache clean --force
npm install
npm run build
```

### CORS Issues

If you encounter CORS errors with OpenAI API, ensure you're:
1. Using HTTPS in production
2. Not trying to call API from `file://` protocol
3. Using correct API endpoint

### Large Bundle Size

```bash
# Analyze bundle
npm run build
npx vite-bundle-visualizer
```

---

## Checklist Before Deploy

- [ ] Remove all `console.log` statements
- [ ] Test with real API key
- [ ] Verify all environment variables
- [ ] Check responsive design on mobile
- [ ] Test in multiple browsers (Chrome, Firefox, Safari)
- [ ] Validate JSON output format
- [ ] Set up error monitoring
- [ ] Configure CDN/caching
- [ ] Add robots.txt if needed
- [ ] Set up SSL certificate
- [ ] Test API rate limits

---

## Support

Deployment issues? Check:
- [Vite Deployment Docs](https://vitejs.dev/guide/static-deploy.html)
- [Vercel Docs](https://vercel.com/docs)
- [Netlify Docs](https://docs.netlify.com/)

Or open an issue on GitHub!
