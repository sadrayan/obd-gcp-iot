const axios = require("axios");
require("dotenv").config();

const MENDER_LOGIN_URL = "https://hosted.mender.io/api/management/v1/useradm/auth/login";
const MENDER_LIST_DEPLOYMENT_URL = "https://hosted.mender.io/api/management/v1/deployments/deployments";

const authorizeMender = async () => {
  var user = process.env.MENDER_USERNAME;
  var password = process.env.MENDER_PASSWORD;
  // console.log(user, password)

  try {
    var base64encodedData = Buffer.from(`${user}:${password}`, "utf8").toString("base64");
    const headers = {
      "Content-Type": "application/json",
      Accept: "application/jwt",
      Authorization: `Basic ${base64encodedData}`,
    };
    const response = await axios.post(MENDER_LOGIN_URL, null, {
      headers: headers,
    });
    //   console.log(response.data)
    axios.defaults.headers.common = { Authorization: `Bearer ${response.data}`};

    return response.data;
  } catch (error) {
    console.error(error.config, error.response.data);
    throw new Error("Mender Authentication failed...");
  }
};

const getDeployments = async () => {
  try {
    const response = await axios.get(MENDER_LIST_DEPLOYMENT_URL);
    //   console.log(response)
    return response.data;
  } catch (error) {
    console.error(error.config, error.response.data);
    throw new Error("Mender get deplpyment failed...");
  }
};

const getArtifacts = async () => {
  try {
    const response = await axios.get(MENDER_LIST_DEPLOYMENT_URL);
    console.log(response);
  } catch (error) {
    console.error(error.config, error.response.data);
    throw new Error("Mender Authentication failed...");
  }
};

exports.authorizeMender = authorizeMender;
exports.getDeployments  = getDeployments;
exports.getArtifacts    = getArtifacts;
