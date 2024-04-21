const express = require("express");
const router = express.Router();
const { exec } = require("child_process");
const path = require("path");

const DockerLogs = require("../models/dockerLogs.model");

router.get("/containers", (req, res, next) => {
  const relativePath = "../RedTeamScripts/detection.py";
  const absolutePath = path.resolve(__dirname, relativePath);

  exec(`python3 ${absolutePath}`, (err, stdout, stderr) => {
    if (err) {
      console.error(`Error: ${err.message}`);
      res.status(500).send("Internal Server Error");
      return;
    }
    if (stderr) {
      console.error(`Error: ${stderr}`);
      res.status(500).send("Internal Server Error");
      return;
    }

    // Trim leading and trailing whitespaces from the output
    const containers = stdout.trim();

    try {
      const containersData = JSON.parse(containers);
      res.json(containersData);
    } catch (error) {
      console.error("Error parsing JSON:", error);
      res.status(500).send("Internal Server Error");
    }
  });
});

router.get("/logs", async (req, res, next) => {
  try {
    // Fetch Docker logs from the database
    const dockerLogs = await DockerLogs.find().lean();
    // Reverse the array to get the latest logs first
    await dockerLogs.reverse();
    // Send the response
    res.json(dockerLogs);
  } catch (error) {
    console.error("Error fetching Docker logs:", error);
    res.status(500).send("Internal Server Error");
  }
});

router.get("/attack", async (req, res, next) => {
  const containerName = req.query.containerName;
  const attackName = req.query.attackName;
  const relativePath = `../RedTeamScripts/${attackName}.py`;
  const absolutePath = path.resolve(__dirname, relativePath);

  exec(`python3 ${absolutePath} ${containerName}`, (err, stdout, stderr) => {
    if (err) {
      console.error(`Error: ${err.message}`);
      res.status(500).send("Internal Server Error");
      return;
    }
    if (stderr) {
      console.error(`Error: ${stderr}`);
      res.status(500).send("Internal Server Error");
      return;
    }

    try {
      const outputData = JSON.parse(stdout);
      res.json(outputData);

      if (outputData.success === undefined) {
        outputData.success = true;
      }
      const newLogEntry = new DockerLogs({
        team: "Red",
        attackName: `${attackName}`,
        target: `${containerName}`,
        success: outputData.success,
      });
      newLogEntry.save();
    } catch (error) {
      console.error("Error parsing JSON:", error);
      success = false;
      res.status(500).send("Internal Server Error");
    }
  });
});

router.get("/scan", (req, res, next) => {
  const containerName = req.query.containerName;
  const relativePath = "../RedTeamScripts/Scanner.py";
  const absolutePath = path.resolve(__dirname, relativePath);

  exec(`python3 ${absolutePath} ${containerName}`, (err, stdout, stderr) => {
    if (err) {
      console.error(`Error: ${err.message}`);
      res.status(500).send("Internal Server Error");
      return;
    }
    if (stderr) {
      console.error(`Error: ${stderr}`);
      res.status(500).send("Internal Server Error");
      return;
    }

    try {
      const outputData = JSON.parse(stdout);
      res.json(outputData);
    } catch (error) {
      console.error("Error parsing JSON:", error);
      res.status(500).send("Internal Server Error");
    }
  });
});

router.get("/defence", async (req, res, next) => {
  const containerName = req.query.containerName;
  const defenceName = req.query.defenceName;
  const imageName = req.query.imageName;
  const relativePath = `../BlueTeamScripts/${defenceName}.py`;
  const absolutePath = path.resolve(__dirname, relativePath);

  try {
    // Create a new DockerLogs document
    const newLogEntry = new DockerLogs({
      team: "Blue", // Assuming you have the user information stored in req.user
      attackName: `${defenceName}`,
      target: `${containerName}`,
      success: true,
    });
    await newLogEntry.save();
  } catch (err) {
    console.log(err);
  }

  exec(
    `python3 ${absolutePath} ${containerName} ${imageName}`,
    (err, stdout, stderr) => {
      if (err) {
        console.error(`Error: ${err.message}`);
        res.status(500).send("Internal Server Error");
        return;
      }
      if (stderr) {
        console.error(`Error: ${stderr}`);
        res.status(500).send("Internal Server Error");
        return;
      }

      try {
        const outputData = JSON.parse(stdout);
        res.json(outputData);
      } catch (error) {
        console.error("Error parsing JSON:", error);
        res.status(500).send("Internal Server Error");
      }
    }
  );
});

router.get("/analysis", (req, res, next) => {
  const relativePath = `../BlueTeamScripts/Benchmark.py`;
  const absolutePath = path.resolve(__dirname, relativePath);

  exec(`python3 ${absolutePath}`, (err, stdout, stderr) => {
    if (err) {
      console.error(`Error: ${err.message}`);
      res.status(500).send("Internal Server Error");
      return;
    }
    if (stderr) {
      console.error(`Error: ${stderr}`);
      res.status(500).send("Internal Server Error");
      return;
    }

    try {
      const outputData = JSON.parse(stdout);
      res.json(outputData);
    } catch (error) {
      console.error("Error parsing JSON:", error);
      res.status(500).send("Internal Server Error");
    }
  });
});

router.get("/stats", async (req, res, next) => {
  try {
    const totalAttacks = await DockerLogs.countDocuments({ team: "Red" });
    const totalSuccessfulAttacks = await DockerLogs.countDocuments({
      team: "Red",
      success: true,
    });
    const totalFailedAttacks = await DockerLogs.countDocuments({
      team: "Red",
      success: false,
    });

    res.json({
      "Total Attacks": totalAttacks,
      "Attacks Won": totalSuccessfulAttacks,
      "Attacks Defended": totalFailedAttacks,
    });
  } catch (error) {
    console.error("Error counting attacks:", error);
    res.status(500).send("Internal Server Error");
  }
});

router.get("/attack-counts", async (req, res, next) => {
  try {
    const PrivilegeEscalation = await DockerLogs.countDocuments({
      attackName: "Privilege-Escalation",
      team: "Red",
    });
    const DoS = await DockerLogs.countDocuments({
      attackName: "DoS",
      team: "Red",
    });
    const PayloadDelivery = await DockerLogs.countDocuments({
      attackName: "Payload-Delivery",
      team: "Red",
    });
    const ExposeFilesystem = await DockerLogs.countDocuments({
      attackName: "Expose-Filesystem",
      team: "Red",
    });
    const ExposeHashes = await DockerLogs.countDocuments({
      attackName: "Expose-Hashes",
      team: "Red",
    });
    const ExposeNamespaces = await DockerLogs.countDocuments({
      attackName: "Expose-Namespace",
      team: "Red",
    });
    const ChangePassword = await DockerLogs.countDocuments({
      attackName: "Change-Password",
      team: "Red",
    });
    const ExposeSecrets = await DockerLogs.countDocuments({
      attackName: "Expose-Secrets",
      team: "Red",
    });

    res.json({
      "Privilege Escalation": PrivilegeEscalation,
      DoS: DoS,
      "Payload Delivery": PayloadDelivery,
      Filesystem: ExposeFilesystem,
      Hashes: ExposeHashes,
      Namespaces: ExposeNamespaces,
      "Change Password": ChangePassword,
      Secrets: ExposeSecrets,
    });
  } catch (err) {
    console.log(err);
    res.status(500).send("Internal Server Error");
  }
});

router.get("/severity", async (req, res) => {
  try {
    // Retrieve all successful attacks from MongoDB by the Red team
    const attacks = await DockerLogs.find({ team: "Red", success: true });

    // Process attacks to determine severity counts
    severityCounts = {
      High: 0,
      Medium: 0,
      Low: 0,
    };

    // Group attacks by target and count unique targets attacked by the Red team
    const targetCounts = {};
    attacks.forEach((attack) => {
      const { target } = attack;
      if (!targetCounts[target]) {
        targetCounts[target] = 0;
      }
      targetCounts[target]++;
    });

    // Categorize severity based on the number of unique targets attacked
    Object.values(targetCounts).forEach((count) => {
      if (count >= 5) {
        severityCounts["High"]++;
      } else if (count >= 3) {
        severityCounts["Medium"]++;
      } else {
        severityCounts["Low"]++;
      }
    });

    // Respond with the severity counts
    res.json(severityCounts);
  } catch (error) {
    console.error("Error fetching and analyzing attacks:", error);
    res.status(500).json({ message: "Internal server error" });
  }
});

router.get("/suggestions", async (req, res) => {
  const containerName = req.query.containerName;
  const imageName = req.query.imageName;
  const containerId = req.query.containerID;
  const relativePath = `../RedTeamScripts/Models/Suggestions.py`;
  const absolutePath = path.resolve(__dirname, relativePath);

  // Call the comprehensive Python script with the necessary arguments
  const command = `python "${absolutePath}" "${containerName}" "${imageName}" "${containerId}"`;

  exec(command, (err, stdout, stderr) => {
    if (err) {
      console.log(`Execution Error: ${err.message}`);
      console.error(`Execution Error: ${err.message}`);
      return res
        .status(500)
        .send("Internal Server Error due to execution failure.");
    }

    try {
      const predictions = JSON.parse(stdout);
      res.json(predictions);
    } catch (error) {
      console.error("JSON Parsing Error:", error);
      return res
        .status(500)
        .send("Internal Server Error due to parsing failure.");
    }
  });
});

// Route to fetch time series attack data for line chart
router.get("/time-series-attacks", async (req, res) => {
  try {
    const timeSeriesAttacks = await DockerLogs.aggregate([
      {
        $group: {
          _id: { date: "$date", attackName: "$attackName" },
          count: { $sum: 1 },
        },
      },
      {
        $group: {
          _id: "$_id.date",
          attacks: {
            $push: {
              attackName: "$_id.attackName",
              count: "$count",
            },
          },
        },
      },
    ]);

    const chartData = timeSeriesAttacks.map((entry) => {
      const date = entry._id;
      const attackCounts = {};
      entry.attacks.forEach((attack) => {
        attackCounts[attack.attackName] = attack.count;
      });
      return { date, ...attackCounts };
    });

    console.log("Time series attack data:", chartData);
    res.json(chartData);
  } catch (error) {
    console.error("Error fetching time series attack data:", error);
    res.status(500).json({ error: "Internal Server Error" });
  }
});

// Route to fetch attack possibilities data for bar chart
router.get("/attack-possibilities", async (req, res) => {
  try {
    const attackPossibilities = await DockerLogs.aggregate([
      { $group: { _id: "$attackName", count: { $sum: 1 } } },
    ]);

    // Convert data to a more usable format for frontend
    const formattedData = attackPossibilities.map((entry) => ({
      attackName: entry._id,
      count: entry.count,
    }));

    res.json(formattedData);
  } catch (error) {
    console.error("Error fetching attack possibilities:", error);
    res.status(500).json({ error: "Internal Server Error" });
  }
});

module.exports = router;
