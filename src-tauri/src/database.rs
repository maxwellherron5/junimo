use anyhow::Result;
use sqlx::{Pool, Sqlite, SqlitePool};

use crate::config::Config;

pub type Database = Pool<Sqlite>;

pub async fn init() -> Result<Database> {
    let config = Config::from_env();
    let pool = SqlitePool::connect(&config.database_url).await?;
    Ok(pool)
}

pub async fn migrate(db: &Database) -> Result<()> {
    sqlx::migrate!("../migrations").run(db).await?;
    Ok(())
}
