use anyhow::Result;
use sqlx::SqlitePool;

use crate::models::Item;

#[derive(Clone)]
pub struct ItemService {
    db: SqlitePool,
}

impl ItemService {
    pub fn new(db: SqlitePool) -> Self {
        Self { db }
    }

    pub async fn get_all_items(&self) -> Result<Vec<Item>> {
        let items = sqlx::query_as::<_, Item>("SELECT * FROM items ORDER BY name")
            .fetch_all(&self.db)
            .await?;
        Ok(items)
    }

    pub async fn get_item_by_id(&self, id: i32) -> Result<Option<Item>> {
        let item = sqlx::query_as::<_, Item>("SELECT * FROM items WHERE id = ?")
            .bind(id)
            .fetch_optional(&self.db)
            .await?;
        Ok(item)
    }

    pub async fn search_items(&self, query: &str) -> Result<Vec<Item>> {
        let items = sqlx::query_as::<_, Item>(
            "SELECT * FROM items WHERE name LIKE ? OR description LIKE ? ORDER BY name",
        )
        .bind(format!("%{}%", query))
        .bind(format!("%{}%", query))
        .fetch_all(&self.db)
        .await?;
        Ok(items)
    }
}
