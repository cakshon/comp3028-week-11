'use strict';
const { createApp } = require('./app');
const port = Number(process.env.PORT || 3000);

// 0.0.0.0 is important for reaching the server through Docker port mapping.
createApp().listen(port, '0.0.0.0', () => {
  console.log(`LocalLoop API listening on port ${port}`);
});
