### Stage 1: build ############################################################
FROM node:20-alpine AS builder

WORKDIR /app

# Install deps first (cached layer — only invalidated when package.json changes)
COPY package*.json ./
RUN npm ci

COPY . .

# In production the frontend is served through Nginx, which proxies /api to
# the backend on the same origin — so a relative URL works without knowing
# the backend host at build time.
ARG VITE_API_URL=/api/v1
ARG VITE_APP_NAME=MedServicePrice.kz
ENV VITE_API_URL=$VITE_API_URL
ENV VITE_APP_NAME=$VITE_APP_NAME

RUN npm run build

### Stage 2: serve ############################################################
FROM nginx:1.27-alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
