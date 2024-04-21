const express = require("express");
const router = express.Router();
const { exec, ChildProcess } = require("child_process");
const path = require("path");

router.post("/chat", (req, res) => {
  const userMessage = req.body.message;
  const relativePath = "../Chatbot/chatbot.py";
  const absolutePath = path.resolve(__dirname, relativePath);

  const command = `python3 "${absolutePath}" "${userMessage}"`;

  const childProcess = exec(command, async (err, stdout, stderr) => {
    if (err) {
      console.error(`Error: ${err.message}`);
      res.status(500).send("Internal Server Error");
      return;
    }

    try {
      console.log(stdout);
      const outputData = JSON.parse(stdout);
      await res.json(outputData);
    } catch (error) {
      console.error("Error parsing JSON:", error);
      res.status(500).send("Internal Server Error");
    }
  });
});

module.exports = router;
