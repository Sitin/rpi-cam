const isProduction = process.env.NODE_ENV === 'production';
const apiRoot = isProduction ? window.location.origin : 'http://127.0.0.1:8080';

const config = {
  apiRoot: apiRoot,
  mediaPrefix: isProduction ? '' : apiRoot,
  isProduction: isProduction,
};

console.log('Application config:', config);

export { config }