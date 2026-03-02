FROM node:20-alpine AS frontend-build
WORKDIR /frontend

COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM caddy:2-alpine
# use your prod Caddyfile
COPY caddy/Caddyfile.prod /etc/caddy/Caddyfile
COPY --from=frontend-build /frontend/dist /srv/frontend
RUN mkdir -p /srv/static /srv/media
