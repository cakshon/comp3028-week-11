# syntax=docker/dockerfile:1
# Node 24 is an LTS release. Use a fixed version rather than 'latest'.
FROM node:24-alpine
WORKDIR /app
ENV NODE_ENV=production

# Copy manifests first to benefit from image-layer caching.
COPY package*.json ./
RUN npm ci --omit=dev

# Do not copy local dependencies, tests, secrets or Git history.
COPY --chown=node:node src ./src
USER node
EXPOSE 3000
CMD ["node", "src/server.js"]
