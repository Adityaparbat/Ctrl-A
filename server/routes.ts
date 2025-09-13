import type { Express, Request } from "express";
import { createServer, type Server } from "http";
import bcrypt from "bcrypt";
import { storage } from "./storage";
import { insertUserSchema, insertAnalyticsSchema } from "@shared/schema";
import { z } from "zod";

// Just use Express Request with session, TypeScript will infer types from express-session
import session from 'express-session';

// Login schema for validation
const loginSchema = z.object({
  email: z.string().email(),
  password: z.string().min(6),
});

export async function registerRoutes(app: Express): Promise<Server> {
  // User registration
  app.post("/api/auth/register", async (req, res) => {
    try {
      const userData = insertUserSchema.parse(req.body);
      
      // Check if user already exists
      const existingUser = await storage.getUserByEmail(userData.email);
      if (existingUser) {
        return res.status(400).json({ error: "User already exists" });
      }

      const existingUsername = await storage.getUserByUsername(userData.username);
      if (existingUsername) {
        return res.status(400).json({ error: "Username already taken" });
      }

      // Hash password
      const saltRounds = 12;
      const hashedPassword = await bcrypt.hash(userData.password, saltRounds);
      
      // Create user
      const user = await storage.createUser({
        ...userData,
        password: hashedPassword,
      });

      // Store user in session
      req.session.userId = user.id;
      req.session.user = { id: user.id, username: user.username, email: user.email };

      // Track registration event
      await storage.trackAnalytics({
        event: "user_registered",
        userId: user.id,
        sessionId: req.sessionID,
        metadata: JSON.stringify({ username: user.username }),
      });

      res.status(201).json({ 
        user: { id: user.id, username: user.username, email: user.email },
        message: "User registered successfully" 
      });
    } catch (error) {
      if (error instanceof z.ZodError) {
        return res.status(400).json({ error: "Invalid input", details: error.errors });
      }
      console.error("Registration error:", error);
      res.status(500).json({ error: "Internal server error" });
    }
  });

  // User login
  app.post("/api/auth/login", async (req, res) => {
    try {
      const { email, password } = loginSchema.parse(req.body);
      
      // Find user
      const user = await storage.getUserByEmail(email);
      if (!user) {
        return res.status(401).json({ error: "Invalid credentials" });
      }

      // Verify password
      const passwordValid = await bcrypt.compare(password, user.password);
      if (!passwordValid) {
        return res.status(401).json({ error: "Invalid credentials" });
      }

      // Store user in session
      req.session.userId = user.id;
      req.session.user = { id: user.id, username: user.username, email: user.email };

      // Track login event
      await storage.trackAnalytics({
        event: "user_login",
        userId: user.id,
        sessionId: req.sessionID,
        metadata: JSON.stringify({ username: user.username }),
      });

      res.json({ 
        user: { id: user.id, username: user.username, email: user.email },
        message: "Login successful" 
      });
    } catch (error) {
      if (error instanceof z.ZodError) {
        return res.status(400).json({ error: "Invalid input", details: error.errors });
      }
      console.error("Login error:", error);
      res.status(500).json({ error: "Internal server error" });
    }
  });

  // User logout
  app.post("/api/auth/logout", async (req, res) => {
    const userId = req.session.userId;
    
    if (userId) {
      // Track logout event
      await storage.trackAnalytics({
        event: "user_logout",
        userId,
        sessionId: req.sessionID,
        metadata: JSON.stringify({}),
      });
    }

    req.session.destroy((err: any) => {
      if (err) {
        console.error("Session destruction error:", err);
        return res.status(500).json({ error: "Logout failed" });
      }
      res.clearCookie("inlightex-session"); // Clear our custom session cookie
      res.json({ message: "Logout successful" });
    });
  });

  // Get current user
  app.get("/api/auth/me", async (req, res) => {
    const userId = req.session.userId;
    if (!userId) {
      return res.status(401).json({ error: "Not authenticated" });
    }

    try {
      const user = await storage.getUser(userId);
      if (!user) {
        return res.status(404).json({ error: "User not found" });
      }

      res.json({ 
        user: { id: user.id, username: user.username, email: user.email }
      });
    } catch (error) {
      console.error("Get user error:", error);
      res.status(500).json({ error: "Internal server error" });
    }
  });

  // Get testimonials
  app.get("/api/testimonials", async (req, res) => {
    try {
      const testimonials = await storage.getTestimonials();
      res.json(testimonials);
    } catch (error) {
      console.error("Get testimonials error:", error);
      res.status(500).json({ error: "Internal server error" });
    }
  });

  // Track analytics events
  app.post("/api/analytics/track", async (req, res) => {
    try {
      const analyticsData = insertAnalyticsSchema.parse(req.body);
      const userId = req.session.userId;
      
      await storage.trackAnalytics({
        ...analyticsData,
        userId: userId || null,
        sessionId: req.sessionID,
      });

      res.json({ message: "Event tracked" });
    } catch (error) {
      if (error instanceof z.ZodError) {
        return res.status(400).json({ error: "Invalid input", details: error.errors });
      }
      console.error("Analytics tracking error:", error);
      res.status(500).json({ error: "Internal server error" });
    }
  });

  const httpServer = createServer(app);
  return httpServer;
}
