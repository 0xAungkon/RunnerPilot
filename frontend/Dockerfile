# Build and runtime in one stage using npm preview
FROM node:20-alpine

WORKDIR /app

# Copy necessary files
COPY package*.json ./
COPY tsconfig*.json ./
COPY vite.config.ts ./
COPY index.html ./
COPY eslint.config.js ./
COPY components.json ./
COPY src ./src
COPY public ./public

# Install dependencies and build
RUN npm ci && npm run build


# Start using Vite preview
CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0"]
