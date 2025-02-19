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

First you want to figure out what is the production VITE_API_BASE_URL. For example on the machine where you run the backend run `ngrok http 8000` and read the output terminal info. Then run something like `VITE_API_BASE_URL=https://2665-77-222-255-69.ngrok-free.app ./node_modules/.bin/vite build && surge dist --domain https://topomatch.surge.sh` or change the VITE_API_BASE_URL in package.json "deploy" script and run `npm run deploy`

```sh
VITE_API_BASE_URL=figured_out_prod_api_url npm run deploy
```

Lately there was downtime to surge.sh and I created a github action that build and deploys the vite app to github pages. It happens on push to main and the url is https://jedrula.github.io/dockerize-image-matching-model/

### Run Unit Tests with [Vitest](https://vitest.dev/)

```sh
npm run test:unit
```

### Lint with [ESLint](https://eslint.org/)

```sh
npm run lint
```
