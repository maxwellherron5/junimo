use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use sqlx::FromRow;

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct UserProgress {
    pub id: i32,
    pub bundle_item_id: i32,
    pub completed: bool,
    pub completed_at: Option<DateTime<Utc>>,
}
