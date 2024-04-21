const express = require("express");
const router = express.Router();
const User = require("../models/users.model");

// create a new user
router.post("/create-user", async (req, res, next) => {
  try {
    const existingUser = await User.findOne({ username: req.body.username });

    if (existingUser) {
      return res
        .status(400)
        .json({ message: "User already exists", status: 400 });
    }

    const newUser = await User.create(req.body);
    res.json({
      message: "User created successfully",
      data: newUser,
      status: 200,
    });
  } catch (err) {
    return next(err);
  }
});

// get a user
router.post("/signin", async (req, res, next) => {
  try {
    const { username, password } = req.body;
    const user = await User.findOne({ username, password });

    if (!user) {
      return res
        .status(401)
        .json({ message: "Invalid credentials", status: 401 });
    }

    // user team
    const { team } = user;

    // User found, generate token/session
    res.json({
      message: "Sign In successful",
      data: { user, team },
      status: 200,
    });
  } catch (err) {
    return next(err);
  }
});

router.get("/stats", async (req, res, next) => {
  try {
    const totalUsers = await User.countDocuments();
    res.json({
      "Total Users": totalUsers,
    });
  } catch (err) {}
});

module.exports = router;
