use serde::{Deserialize, Serialize};
use sqlx::FromRow;

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct Bundle {
    pub id: i32,
    pub name: String,
    pub room: String,
    pub reward: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct BundleItem {
    pub id: i32,
    pub bundle_id: i32,
    pub item_id: i32,
    pub quantity: i32,
    pub quality: Option<String>,
}
