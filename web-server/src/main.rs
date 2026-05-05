use anyhow::Result;
use dotenv::dotenv;
use serde::{Deserialize, Serialize};
use sqlx::{Pool, Sqlite, SqlitePool};
use std::convert::Infallible;
use std::sync::Arc;
use tokio;
use warp::Filter;

// Database models
#[derive(Debug, Clone, Serialize, Deserialize, sqlx::FromRow)]
pub struct Item {
    pub id: i32,
    pub name: String,
    pub description: Option<String>,
    pub category: String,
    pub sell_price: Option<i32>,
    pub energy: Option<i32>,
    pub health: Option<i32>,
    pub seasons: Option<String>,
    pub location: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, sqlx::FromRow)]
pub struct Bundle {
    pub id: i32,
    pub name: String,
    pub room: String,
    pub reward: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, sqlx::FromRow)]
pub struct BundleItem {
    pub id: i32,
    pub bundle_id: i32,
    pub item_id: i32,
    pub quantity: i32,
    pub quality: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, sqlx::FromRow)]
pub struct Villager {
    pub id: i32,
    pub name: String,
    pub birthday: Option<String>,
    pub location: Option<String>,
    pub description: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, sqlx::FromRow)]
pub struct VillagerGiftPreference {
    pub id: i32,
    pub villager_id: i32,
    pub item_name: String,
    pub preference_type: String,
}

// API Response wrapper
#[derive(Serialize)]
struct ApiResponse<T> {
    success: bool,
    data: Option<T>,
    error: Option<String>,
}

impl<T> ApiResponse<T> {
    fn success(data: T) -> Self {
        Self {
            success: true,
            data: Some(data),
            error: None,
        }
    }

    fn error(message: String) -> Self {
        Self {
            success: false,
            data: None,
            error: Some(message),
        }
    }
}

type Db = Arc<Pool<Sqlite>>;

async fn init_db() -> Result<Pool<Sqlite>> {
    let database_url = std::env::var("DATABASE_URL")
        .unwrap_or_else(|_| "sqlite:junimo.db".to_string());
    Ok(SqlitePool::connect(&database_url).await?)
}

// API Handlers
async fn get_items(db: Db) -> Result<warp::reply::Json, Infallible> {
    match sqlx::query_as::<_, Item>("SELECT * FROM items ORDER BY name")
        .fetch_all(db.as_ref())
        .await
    {
        Ok(items) => Ok(warp::reply::json(&ApiResponse::success(items))),
        Err(e) => Ok(warp::reply::json(&ApiResponse::<Vec<Item>>::error(e.to_string()))),
    }
}

async fn search_items(query: String, db: Db) -> Result<warp::reply::Json, Infallible> {
    if query.is_empty() {
        return get_items(db).await;
    }

    match sqlx::query_as::<_, Item>(
        "SELECT * FROM items WHERE name LIKE ? OR description LIKE ? ORDER BY name"
    )
    .bind(format!("%{}%", query))
    .bind(format!("%{}%", query))
    .fetch_all(db.as_ref())
    .await
    {
        Ok(items) => Ok(warp::reply::json(&ApiResponse::success(items))),
        Err(e) => Ok(warp::reply::json(&ApiResponse::<Vec<Item>>::error(e.to_string()))),
    }
}

async fn get_bundles(db: Db) -> Result<warp::reply::Json, Infallible> {
    match sqlx::query_as::<_, Bundle>("SELECT * FROM bundles ORDER BY id")
        .fetch_all(db.as_ref())
        .await
    {
        Ok(bundles) => Ok(warp::reply::json(&ApiResponse::success(bundles))),
        Err(e) => Ok(warp::reply::json(&ApiResponse::<Vec<Bundle>>::error(e.to_string()))),
    }
}

async fn get_bundle_items(bundle_id: i32, db: Db) -> Result<warp::reply::Json, Infallible> {
    match sqlx::query_as::<_, BundleItem>(
        "SELECT * FROM bundle_items WHERE bundle_id = ? ORDER BY id"
    )
    .bind(bundle_id)
    .fetch_all(db.as_ref())
    .await
    {
        Ok(items) => Ok(warp::reply::json(&ApiResponse::success(items))),
        Err(e) => Ok(warp::reply::json(&ApiResponse::<Vec<BundleItem>>::error(e.to_string()))),
    }
}

async fn get_villagers(db: Db) -> Result<warp::reply::Json, Infallible> {
    match sqlx::query_as::<_, Villager>("SELECT * FROM villagers ORDER BY name")
        .fetch_all(db.as_ref())
        .await
    {
        Ok(villagers) => Ok(warp::reply::json(&ApiResponse::success(villagers))),
        Err(e) => Ok(warp::reply::json(&ApiResponse::<Vec<Villager>>::error(e.to_string()))),
    }
}

async fn get_villager_gifts(villager_id: i32, db: Db) -> Result<warp::reply::Json, Infallible> {
    match sqlx::query_as::<_, VillagerGiftPreference>(
        "SELECT * FROM villager_gift_preferences WHERE villager_id = ? ORDER BY preference_type, item_name"
    )
    .bind(villager_id)
    .fetch_all(db.as_ref())
    .await
    {
        Ok(gifts) => Ok(warp::reply::json(&ApiResponse::success(gifts))),
        Err(e) => Ok(warp::reply::json(&ApiResponse::<Vec<VillagerGiftPreference>>::error(e.to_string()))),
    }
}

fn with_db(db: Db) -> impl Filter<Extract = (Db,), Error = Infallible> + Clone {
    warp::any().map(move || db.clone())
}

#[tokio::main]
async fn main() -> Result<()> {
    dotenv().ok();
    
    println!("🍄 Starting Junimo Web Server...");
    
    // Initialize database
    let db = Arc::new(init_db().await?);
    println!("✓ Database initialized");
    
    // Test database
    let item_count: (i64,) = sqlx::query_as("SELECT COUNT(*) FROM items")
        .fetch_one(db.as_ref())
        .await?;
    println!("✓ Found {} items in database", item_count.0);
    
    // Static files
    let index = warp::path::end()
        .map(|| warp::reply::html(include_str!("../static/index.html")));
    
    let js = warp::path("main.js")
        .map(|| warp::reply::with_header(
            include_str!("../static/main.js"),
            "content-type",
            "application/javascript"
        ));
    
    let web_api_js = warp::path("web-api.js")
        .map(|| warp::reply::with_header(
            include_str!("../static/web-api.js"),
            "content-type",
            "application/javascript"
        ));
    
    let junimo_icon = warp::path("assets")
        .and(warp::path("junimo.png"))
        .map(|| warp::reply::with_header(
            include_bytes!("../static/assets/junimo.png").as_slice(),
            "content-type",
            "image/png"
        ));
    
    // API routes
    let items = warp::path("api")
        .and(warp::path("items"))
        .and(warp::path::end())
        .and(warp::get())
        .and(with_db(db.clone()))
        .and_then(get_items);
    
    let search = warp::path("api")
        .and(warp::path("items"))
        .and(warp::path("search"))
        .and(warp::get())
        .and(warp::query::<std::collections::HashMap<String, String>>())
        .and(with_db(db.clone()))
        .and_then(|params: std::collections::HashMap<String, String>, db| {
            let query = params.get("q").cloned().unwrap_or_default();
            search_items(query, db)
        });
    
    let bundles = warp::path("api")
        .and(warp::path("bundles"))
        .and(warp::path::end())
        .and(warp::get())
        .and(with_db(db.clone()))
        .and_then(get_bundles);
    
    let bundle_items = warp::path("api")
        .and(warp::path("bundles"))
        .and(warp::path::param::<i32>())
        .and(warp::path("items"))
        .and(warp::get())
        .and(with_db(db.clone()))
        .and_then(get_bundle_items);
    
    let villagers = warp::path("api")
        .and(warp::path("villagers"))
        .and(warp::path::end())
        .and(warp::get())
        .and(with_db(db.clone()))
        .and_then(get_villagers);
    
    let villager_gifts = warp::path("api")
        .and(warp::path("villagers"))
        .and(warp::path::param::<i32>())
        .and(warp::path("gifts"))
        .and(warp::path::end())
        .and(warp::get())
        .and(with_db(db.clone()))
        .and_then(get_villager_gifts);
    
    let cors = warp::cors()
        .allow_any_origin()
        .allow_headers(vec!["content-type"])
        .allow_methods(vec!["GET", "POST"]);
    
    let routes = index
        .or(js)
        .or(web_api_js)
        .or(junimo_icon)
        .or(items)
        .or(search)
        .or(bundles)
        .or(bundle_items)
        .or(villagers)
        .or(villager_gifts)
        .with(cors);
    
    println!("🚀 Server starting on http://localhost:3000");
    
    warp::serve(routes)
        .run(([0, 0, 0, 0], 3000))
        .await;
    
    Ok(())
}