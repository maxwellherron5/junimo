use anyhow::Result;
use chrono::Utc;
use sqlx::SqlitePool;

use crate::models::UserProgress;

#[derive(Clone)]
pub struct ProgressService {
    db: SqlitePool,
}

impl ProgressService {
    pub fn new(db: SqlitePool) -> Self {
        Self { db }
    }

    pub async fn mark_completed(&self, bundle_item_id: i32) -> Result<()> {
        sqlx::query(
            "INSERT OR REPLACE INTO user_progress (bundle_item_id, completed, completed_at) 
             VALUES (?, true, ?)",
        )
        .bind(bundle_item_id)
        .bind(Utc::now())
        .execute(&self.db)
        .await?;
        Ok(())
    }

    pub async fn mark_incomplete(&self, bundle_item_id: i32) -> Result<()> {
        sqlx::query("DELETE FROM user_progress WHERE bundle_item_id = ?")
            .bind(bundle_item_id)
            .execute(&self.db)
            .await?;
        Ok(())
    }

    pub async fn get_progress(&self) -> Result<Vec<UserProgress>> {
        let progress = sqlx::query_as::<_, UserProgress>("SELECT * FROM user_progress")
            .fetch_all(&self.db)
            .await?;
        Ok(progress)
    }
}
