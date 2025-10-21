use anyhow::Result;
use sqlx::SqlitePool;

use crate::models::{Bundle, BundleItem};

#[derive(Clone)]
pub struct BundleService {
    db: SqlitePool,
}

impl BundleService {
    pub fn new(db: SqlitePool) -> Self {
        Self { db }
    }

    pub async fn get_all_bundles(&self) -> Result<Vec<Bundle>> {
        let bundles = sqlx::query_as::<_, Bundle>("SELECT * FROM bundles ORDER BY room, name")
            .fetch_all(&self.db)
            .await?;
        Ok(bundles)
    }

    pub async fn get_bundle_items(&self, bundle_id: i32) -> Result<Vec<BundleItem>> {
        let items = sqlx::query_as::<_, BundleItem>(
            "SELECT * FROM bundle_items WHERE bundle_id = ? ORDER BY id",
        )
        .bind(bundle_id)
        .fetch_all(&self.db)
        .await?;
        Ok(items)
    }
}
