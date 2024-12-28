## Project Setup

```sh
npm install
```

### Compile and Hot-Reload for Development

```sh
npm run dev
```

### Type-Check, Compile and Minify for Production

```sh
npm run build
```

### Deploy

First you want to figure out what is the production VITE_API_BASE_URL. For example on the machine where you run the backend run `ngrok http 8000` and read the output terminal info. Then run something like `VITE_API_BASE_URL=https://f14b-31-0-120-247.ngrok-free.app npm run deploy`

```sh
VITE_API_BASE_URL=figured_out_prod_api_url npm run deploy
```

### Run Unit Tests with [Vitest](https://vitest.dev/)

```sh
npm run test:unit
```

### Lint with [ESLint](https://eslint.org/)

```sh
npm run lint
```
