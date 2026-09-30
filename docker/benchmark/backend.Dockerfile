# Comparison only: an unoptimized image containing source and dev dependencies.
FROM node:22-alpine@sha256:0a7108bf6c7bf5de370ffb1a3ed6be93d405b43ff159f681a8d18c0e2bc2e402
WORKDIR /app
COPY package*.json ./
RUN npm ci --no-audit --no-fund
COPY . .
CMD ["node", "server.js"]
