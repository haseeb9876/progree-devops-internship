// Runs once, when MongoDB's data volume is empty.
const fs = require('fs');
const appDb = db.getSiblingDB('wanderlust');
appDb.createUser({
  user: 'wanderlust',
  pwd: fs.readFileSync('/run/secrets/mongo_app_password', 'utf8').trim(),
  roles: [{ role: 'readWrite', db: 'wanderlust' }],
});
