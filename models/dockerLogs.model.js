const mongoose = require("mongoose");
const Schema = mongoose.Schema;

const dockerLogsSchema = new Schema(
  {
    date: {
      type: String,
      default: () => {
        const now = new Date();
        return now.toLocaleDateString("en-GB");
      },
    },
    time: {
      type: String,
      default: () => {
        const now = new Date();
        const hours = now.getHours().toString().padStart(2, "0");
        const minutes = now.getMinutes().toString().padStart(2, "0");
        const seconds = now.getSeconds().toString().padStart(2, "0");
        return `${hours}:${minutes}:${seconds}`;
      },
    },
    team: {
      type: String,
      required: true,
    },
    target: {
      type: String,
      required: true,
    },
    attackName: {
      type: String,
      required: true,
    },

    success: {
      type: Boolean,
      required: true,
    },
  },
  {
    collection: "dockerLogs",
  }
);

module.exports = mongoose.model("DockerLogs", dockerLogsSchema);
