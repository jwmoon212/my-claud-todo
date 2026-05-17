# My Blog Platform

## Project Overview 
A simple blogging platform where users can create, edit,
and publish articles. Built with Next.js and Prisma.

## Tech Stack
-Framework: Next.js 14 (App Router)
-Database: PostgreSQL via Prisma ORM
-Styling: Tailwind CSS
-Auth: NextAuth.js

## Key Commands
-Install: npm install
-Dev server: npm run dev
-Run tests: npm test
-Database migration: npx prisma migrate dev

## Project Structure
app/ --Next.js app router pages
components/ --Reusable React components
lib/ --Utility functions (prisma client, auth,etc. )
prisma/ --Database schema and migrations

## Coding Conventions
-Use TypeScript strict mode
-Use functional components with hooks
-Prefer async/await for database queries
-Write tests for all API routes
