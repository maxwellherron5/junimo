use serde::{Deserialize, Serialize};
use sqlx::FromRow;

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct Item {
    pub id: i32,
    pub name: String,
    pub description: Option<String>,
    pub category: String,
    pub sell_price: Option<i32>,
    pub energy: Option<i32>,
    pub health: Option<i32>,
}
