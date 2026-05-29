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

    const migrations = [
      '001_initial_schema.sql',
      '002_guest_sessions.sql'
    ];

    for (const migration of migrations) {
      const sqlFile = path.join(migrationsDir, migration);
      if (fs.existsSync(sqlFile)) {
        const sql = fs.readFileSync(sqlFile, 'utf8');
        await client.query(sql);
        console.log(`   ✓ ${migration}`);
      }
    }

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
