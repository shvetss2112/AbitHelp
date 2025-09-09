FROM node:20-alpine AS base

WORKDIR /app

COPY package.json package-lock.json* ./

RUN npm ci

COPY . .

RUN npm run build

FROM base AS dev

COPY . .

CMD ["npm", "run", "dev"]

FROM node:20-alpine AS prod

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci --only=production

COPY --from=base /app/.next ./.next
COPY --from=base /app/public ./public

EXPOSE 3000
CMD ["npm", "start"]
