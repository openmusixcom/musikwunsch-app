import fs from 'fs';
import path from 'path';
import { Pool } from 'pg';
import dotenv from 'dotenv';

dotenv.config();

const pool = new Pool({
  host: process.env.DB_HOST,
  port: process.env.DB_PORT,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME,
});

const migrationsDir = path.dirname(import.meta.url.replace('file://', ''));

async function runMigrations() {
  const client = await pool.connect();
  try {
    console.log('🔄 Running migrations...');

    // Read and execute SQL file
    const sqlFile = path.join(migrationsDir, '001_initial_schema.sql');
    const sql = fs.readFileSync(sqlFile, 'utf8');

    await client.query(sql);
    console.log('✅ Migrations completed successfully');
  } catch (error) {
    console.error('❌ Migration error:', error);
    process.exit(1);
  } finally {
    await client.end();
    await pool.end();
  }
}

runMigrations();
