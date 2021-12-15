// const fetch = require('node-fetch')
import { config } from 'dotenv';
config();

/**
 * Generic background Cloud Function to be triggered by Cloud Storage.
 *
 * @param {object} file The Cloud Storage file metadata.
 * @param {object} context The event metadata.
 */
export function listDevice(file, context) {

  console.log(`  Event: ${context.eventId}`);
  console.log(`  Event Type: ${context.eventType}`);
  console.log(`  Bucket: ${file.bucket}`);
  console.log(`  File: ${file.name}`);
  console.log(`  Metageneration: ${file.metageneration}`);
  console.log(`  Created: ${file.timeCreated}`);
  console.log(`  Updated: ${file.updated}`);

  var user = process.env.MENDER_USERNAME
  var password = process.env.MENDER_PASSWORD
  console.log(user, password)
}

// var user = process.env.MENDER_USERNAME
// var password = process.env.MENDER_PASSWORD
// var base64encodedData = Buffer.from(user + ':' + password).toString('base64');
// var jwtToken = ''
// var headers = {
//   'Content-Type':'application/json',
//   'Accept':'application/jwt',
//   'Authorization':`Basic ${base64encodedData}`
// };

// console.log(user, password)

// fetch('https://hosted.mender.io/api/management/v1/useradm/auth/login',
// {
//   method: 'POST',
//   headers: headers
// })
// .then(function(res) {
//   jwtToken = res['headers'].get('set-cookie').split(';')[0].substring(4)
//   console.log(jwtToken);

//   headers = {
//     'Accept':'application/json',
//     'Authorization':`Bearer ${jwtToken}`
//   };
  
//   fetch('https://hosted.mender.io/api/management/v1/deployments/deployments',
//   {
//     method: 'GET',
//     headers: headers
//   })
//   .then(function(res) {
//       return res.json();
//   }).then(function(body) {
//       console.log(body);
//   });


// });