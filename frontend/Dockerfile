# Build stage
FROM node:lts-alpine as build-stage

# Set working directory
WORKDIR /app

# Install pnpm and configure registry
RUN npm install -g pnpm && \
    pnpm config set registry https://registry.npmmirror.com/

# Copy package.json and pnpm-lock.yaml files
COPY package.json pnpm-lock.yaml ./

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy project files and folders to the current working directory (i.e. 'app' folder)
COPY . .

# Build app for production with minification
RUN pnpm build

# Production stage
FROM nginx:stable-alpine as production-stage

COPY ./docker/nginx/default.conf /etc/nginx/conf.d/

# Copy built assets from build-stage to nginx server
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Expose port 80 to the outside once the container has launched
EXPOSE 80

# When the container starts, this command will be executed.
CMD ["nginx", "-g", "daemon off;"]
