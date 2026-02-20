# multi-stage Dockerfile for a Node.js server (adjust scripts/paths as needed)
FROM node:18-alpine AS builder
WORKDIR /app
# install dependencies based on lockfile if present
COPY package*.json ./
RUN npm ci
# copy source and build (if you have a build step)
COPY . .
RUN npm run build --if-present

FROM node:18-alpine AS runtime
WORKDIR /app
ENV NODE_ENV=production \
    PORT=3000
# copy only what's needed for runtime
COPY --from=builder /app/package*.json ./
COPY --from=builder /app/node_modules ./node_modules
# prefer dist if build produced it, otherwise copy source
COPY --from=builder /app/src ./src

EXPOSE 8080
USER node
# use package.json start script (ensure "start" is defined)
CMD ["npm", "start"]
