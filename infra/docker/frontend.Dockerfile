# Stage 1: Build the frontend application
FROM node:20-alpine AS builder

WORKDIR /app

COPY telegram-automation/frontend/package.json .
COPY telegram-automation/frontend/pnpm-lock.yaml .

RUN pnpm install --frozen-lockfile

COPY telegram-automation/frontend/ .

RUN npm run build

# Stage 2: Serve the frontend application
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

