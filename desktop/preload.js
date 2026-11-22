// Runs before Angular. Gives it the url of the backend that main.js started,
// read in frontend/src/app/services/products.ts as window.desktop.apiUrl
const { contextBridge } = require('electron');

const arg = process.argv.find((value) => value.startsWith('--api-url='));

contextBridge.exposeInMainWorld('desktop', {
  apiUrl: arg ? arg.slice('--api-url='.length) : null,
});
