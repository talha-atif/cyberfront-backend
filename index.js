const express = require("express");
const cors = require("cors");
const bodyParser = require("body-parser");
const mongoose = require("mongoose");

const app = express();

const allowedOrigins = [
  "http://192.168.18.185:3000",
  "http://localhost:3000",
  "http://localhost:5000",
  "http://0.0.0.0:2375",
];

app.use(
  cors({
    origin: allowedOrigins,
  })
);
app.use(bodyParser.json());

mongoose
  .connect("mongodb://0.0.0.0:27017/cyberfront", {
    useNewUrlParser: true,
    useUnifiedTopology: true,
  })
  .then(() => console.log("DB connected"))
  .catch((err) => console.log("Error connecting to DB", err));

const userRoutes = require("./routes/user.routes");
const dockerRoutes = require("./routes/docker.routes");
const chatbotRoutes = require("./routes/chatbot.routes");

app.use("/users", userRoutes);
app.use("/docker", dockerRoutes);
app.use("/chatbot", chatbotRoutes);

const port = process.env.PORT || 5000;
app.listen(port, () => console.log(`Server started on port ${port}`));

// Error Handling Middleware
app.use((err, req, res, next) => {
  console.error(err.message);
  if (!err.statusCode) err.statusCode = 500;
  res.status(err.statusCode).send(err.message);
});
