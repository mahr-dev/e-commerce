# ============================================================
# Stage 1: Build the Angular app
# ============================================================
FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies (cached layer)
COPY package*.json ./
RUN npm install

# Copy source and build
COPY . .
RUN npm run build -- --configuration production

# ============================================================
# Stage 2: Serve with Nginx
# ============================================================
FROM nginx:alpine

# Copy built assets
COPY --from=builder /app/dist/ecommerce-frontend/browser /usr/share/nginx/html

# Nginx config for SPA routing (all routes → index.html)
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
