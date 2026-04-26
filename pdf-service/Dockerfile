FROM ghcr.io/puppeteer/puppeteer:23

WORKDIR /app
COPY package.json ./
RUN npm install --omit=dev --no-audit --no-fund
COPY index.js ./

ENV PORT=9000
EXPOSE 9000
CMD ["node", "index.js"]
