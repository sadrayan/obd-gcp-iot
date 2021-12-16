const { authorizeMender, getDeployments } = require("./mender_service");

/**
 * Cloud Function to be triggered by Cloud Storage Device artifact updates
 *
 * @param {object} file The Cloud Storage file metadata.
 * @param {object} context The event metadata.
 */
const listDevice = async (file, context) => {
  console.log(`  Bucket: ${file.bucket}`);
  console.log(`  File: ${file.name}`);

  await authorizeMender();
  const res = await getDeployments();
  console.log(res);
};

file = { bucket: "bucket", name: "somefile.txt" };
listDevice(file, null);

exports.listDevice;
